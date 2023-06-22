#include <libmuscle/profiler.hpp>

#include <libmuscle/profiling.hpp>

#include <chrono>
#include <mutex>
#include <random>


using std::chrono::steady_clock;
using duration = std::chrono::steady_clock::duration;
using time_point = std::chrono::steady_clock::time_point;


#ifdef LIBMUSCLE_PATCH_PROFILER_COMMUNICATION_INTERVAL
LIBMUSCLE_PATCH_PROFILER_COMMUNICATION_INTERVAL
#else

namespace {
    constexpr duration communication_interval_() {
        return std::chrono::seconds(10);
    }
}

#endif


namespace libmuscle { namespace _MUSCLE_IMPL_NS {

Profiler::Profiler(MMPClient & manager)
    : manager_(manager)
    , enabled_(true)
    , events_()
    , thread_(communicate_, this)
    , done_(false)
{}

Profiler::~Profiler() {
    stop_thread_();
}

void Profiler::shutdown() {
    stop_thread_();

    // with the thread gone, there's no need to lock anymore
    flush_();
}

void Profiler::set_level(std::string const & level) {
    std::lock_guard<std::mutex> lock(mutex_);
    enabled_ = level == "all";
}

void Profiler::record_event(ProfileEvent && event) {
    if (!event.stop_time.is_set())
        event.stop_time = ProfileTimestamp();

    if (enabled_) {
        std::lock_guard<std::mutex> lock(mutex_);
        events_.push_back(std::move(event));
        if (events_.size() >= 10000)
            flush_();
        next_send_ = steady_clock::now() + communication_interval_();
    }
}

void Profiler::communicate_(Profiler * self) {
    auto seed = std::random_device()();
    std::default_random_engine generator(seed);
    std::uniform_real_distribution<double> rand01;
    duration initial_delay = std::chrono::duration_cast<duration>(
            communication_interval_() * rand01(generator));

    std::unique_lock<std::mutex> lock(self->mutex_);

    self->next_send_ = steady_clock::now() + initial_delay;

    while (!self->done_) {
        auto status = self->done_cv_.wait_until(lock, self->next_send_);
        if (status == std::cv_status::timeout) {
            auto now = steady_clock::now();
            if (self->next_send_ <= now) {
                self->flush_();
                self->next_send_ = now + communication_interval_();
            }
        }
    }
}

// To be called only with mutex_ locked
void Profiler::flush_() {
    if (!events_.empty()) {
        manager_.submit_profile_events(events_);
        events_.clear();
    }
}

void Profiler::stop_thread_() {
    {
        std::lock_guard<std::mutex> lock(mutex_);

        if (done_)
            return;

        done_ = true;
    }
    done_cv_.notify_all();
    thread_.join();
}

} }

