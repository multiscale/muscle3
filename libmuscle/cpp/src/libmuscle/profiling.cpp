#include <libmuscle/profiling.hpp>

#include <chrono>


using ymmsl::Port;
using std::chrono::duration_cast;
using ns = std::chrono::nanoseconds;
using std::chrono::steady_clock;
using std::chrono::system_clock;


namespace {
    int64_t get_time_ref_() {
        auto now_steady = steady_clock::now();
        auto now_wall = system_clock::now();

        int64_t now_steady_ns = duration_cast<ns>(
                now_steady.time_since_epoch()).count();
        int64_t now_wall_ns = duration_cast<ns>(
                now_wall.time_since_epoch()).count();
        return now_wall_ns - now_steady_ns;
    }
}


namespace libmuscle { namespace _MUSCLE_IMPL_NS {

/* Note that this is not inlined, as translation units are compiled
 * separately and we don't use LTO. That should keep the compiler from
 * moving it with respect to the thing we want to profile while optimising.
 */
ProfileTimestamp::ProfileTimestamp() {
    auto now = steady_clock::now().time_since_epoch();
    this->nanoseconds = duration_cast<ns>(now).count() + time_ref_;
}

ProfileTimestamp::ProfileTimestamp(int64_t nanoseconds)
    : nanoseconds(nanoseconds)
{}

int64_t ProfileTimestamp::time_ref_ = get_time_ref_();

std::ostream & operator<<(std::ostream & os, ProfileTimestamp ts) {
    return os << ts.nanoseconds;
}


ProfileEvent::ProfileEvent(
        ProfileEventType event_type,
        Optional<ProfileTimestamp> start_time,
        Optional<ProfileTimestamp> stop_time,
        Optional<ymmsl::Port> const & port,
        Optional<int> port_length,
        Optional<int> slot,
        Optional<std::size_t> message_size,
        Optional<double> message_timestamp)
    : event_type(event_type)
    , start_time(start_time)
    , stop_time(stop_time)
    , port(port)
    , port_length(port_length)
    , slot(slot)
    , message_size(message_size)
    , message_timestamp(message_timestamp)
{}

void ProfileEvent::start() {
    start_time = ProfileTimestamp();
}

void ProfileEvent::stop() {
    stop_time = ProfileTimestamp();
}

} }


