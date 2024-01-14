// Inject mocks
#define LIBMUSCLE_MOCK_MMP_CLIENT <mocks/mock_mmp_client.hpp>
#define LIBMUSCLE_PATCH_PROFILER_COMMUNICATION_INTERVAL \
    std::chrono::steady_clock::duration communication_interval_();

// into the real implementation,
#include <libmuscle/profiler.cpp>
#include <libmuscle/profiling.cpp>
#include <libmuscle/timestamp.cpp>

// then add mock implementations as needed.
#include <mocks/mock_mmp_client.hpp>

// and provide the background thread communication interval function
// patched in above.
#include <chrono>

using std::chrono_literals::operator""ms;

auto communication_interval = 10000ms;

std::chrono::steady_clock::duration communication_interval_() {
    return communication_interval;
}


// Test code dependencies
#include <libmuscle/tests/fixtures.hpp>
#include <libmuscle/namespace.hpp>
#include <libmuscle/profiler.hpp>
#include <libmuscle/profiling.hpp>

#include <chrono>
#include <cstdlib>
#include <time.h>
#include <utility>
#include <gtest/gtest.h>


using libmuscle::_MUSCLE_IMPL_NS::Profiler;
using libmuscle::_MUSCLE_IMPL_NS::ProfileEvent;
using libmuscle::_MUSCLE_IMPL_NS::ProfileEventType;
using libmuscle::_MUSCLE_IMPL_NS::ProfileTimestamp;
using libmuscle::_MUSCLE_IMPL_NS::MockMMPClient;
using ymmsl::Port;


int main(int argc, char *argv[]) {
    ::testing::InitGoogleTest(&argc, argv);
    return RUN_ALL_TESTS();
}


namespace ymmsl { namespace impl {

bool operator==(Port const & lhs, Port const & rhs) {
    return lhs.name == rhs.name && lhs.oper == rhs.oper;
}

} }


namespace libmuscle { namespace _MUSCLE_IMPL_NS {

// Helpers for comparison, not needed in the main code so put here.
bool operator==(ProfileTimestamp const & lhs, ProfileTimestamp const & rhs) {
    return lhs.nanoseconds == rhs.nanoseconds;
}

bool operator<(ProfileTimestamp const & lhs, ProfileTimestamp const & rhs) {
    return lhs.nanoseconds < rhs.nanoseconds;
}

bool operator==(ProfileEvent const & lhs, ProfileEvent const & rhs) {
    if (lhs.event_type != rhs.event_type)
        return false;

    if (lhs.start_time != rhs.start_time)
        return false;

    if (lhs.stop_time != rhs.stop_time)
        return false;

    if (lhs.port != rhs.port)
        return false;

    if (lhs.port_length != rhs.port_length)
        return false;

    if (lhs.slot != rhs.slot)
        return false;

    if (lhs.message_size != rhs.message_size)
        return false;

    if (lhs.message_timestamp != rhs.message_timestamp)
        return false;

    return true;
}

} }

// Profiler has an internal mutex, which we need to lock when accessing
std::size_t num_queued_events(Profiler & profiler) {
    std::lock_guard<std::mutex> lock(profiler.mutex_);
    return profiler.events_.size();
}

ProfileEvent get_queued_event(
        Profiler & profiler, std::size_t i) {
    std::lock_guard<std::mutex> lock(profiler.mutex_);
    return profiler.events_.at(i);
}


struct libmuscle_profiler : ::testing::Test {
    RESET_MOCKS(MockMMPClient);
    MockMMPClient mock_mmp_client_;
};


TEST_F(libmuscle_profiler, test_recording_events) {
    Profiler profiler(mock_mmp_client_);

    ProfileTimestamp t1, t2;
    ProfileEvent e(ProfileEventType::register_, t1, t2);

    profiler.record_event(ProfileEvent(e));

    ASSERT_EQ(e.start_time, t1);
    ASSERT_EQ(e.stop_time, t2);
    ASSERT_EQ(get_queued_event(profiler, 0), e);
}


TEST_F(libmuscle_profiler, test_disabling) {
    Profiler profiler(mock_mmp_client_);
    profiler.set_level("none");

    ProfileTimestamp t1, t2;
    ProfileEvent e(ProfileEventType::register_, t1, t2);

    profiler.record_event(ProfileEvent(e));

    ASSERT_EQ(e.start_time, t1);
    ASSERT_EQ(e.stop_time, t2);
    ASSERT_EQ(num_queued_events(profiler), 0u);
}


TEST_F(libmuscle_profiler, test_auto_stop_time) {
    Profiler profiler(mock_mmp_client_);

    ProfileTimestamp t1;
    ProfileEvent e(ProfileEventType::send, t1);

    // Wait a bit to ensure we get a different timestamp on platforms with
    // low time resolution. A millisecond should definitely do it.
    timespec sleep_time;
    sleep_time.tv_sec = 0l;
    sleep_time.tv_nsec = 1000000l;
    nanosleep(&sleep_time, nullptr);

    profiler.record_event(std::move(e));

    auto const & e2 = get_queued_event(profiler, 0);
    ASSERT_EQ(e2.start_time, t1);
    ASSERT_TRUE(e2.stop_time.is_set());
    ASSERT_LT(e2.start_time.get(), e2.stop_time.get());
}

TEST_F(libmuscle_profiler, test_send_to_mock_mmp_client) {
    Profiler profiler(mock_mmp_client_);

    ProfileEvent e1(
            ProfileEventType::receive, ProfileTimestamp(), ProfileTimestamp());
    profiler.record_event(ProfileEvent(e1));

    for (int i = 1; i < 9999; ++i) {
        ProfileEvent e(
                ProfileEventType::send, ProfileTimestamp(), ProfileTimestamp());
        profiler.record_event(std::move(e));
    }

    ASSERT_FALSE(mock_mmp_client_.submit_profile_events.called());

    ProfileEvent e2(
            ProfileEventType::receive_transfer, ProfileTimestamp(), ProfileTimestamp());
    profiler.record_event(ProfileEvent(e2));

    ASSERT_TRUE(mock_mmp_client_.submit_profile_events.called());
    auto const & events = mock_mmp_client_.submit_profile_events.call_arg<0>();
    ASSERT_EQ(events.size(), 10000u);
    ASSERT_EQ(events.at(0), e1);
    ASSERT_EQ(events.at(9999), e2);
}

TEST_F(libmuscle_profiler, test_send_timeout) {
    std::chrono::steady_clock::duration wait_time;

    if (getenv("CI")) {
        communication_interval = 40ms;
        wait_time = 500ms;
    }
    else {
        communication_interval = 40ms;
        wait_time = 60ms;
    }

    Profiler profiler(mock_mmp_client_);

    ProfileEvent e1(
            ProfileEventType::receive, ProfileTimestamp(), ProfileTimestamp());
    profiler.record_event(ProfileEvent(e1));

    std::this_thread::sleep_for(wait_time);

    ASSERT_EQ(mock_mmp_client_.submit_profile_events.call_arg<0>().size(), 1u);
    ASSERT_EQ(mock_mmp_client_.submit_profile_events.call_arg<0>().at(0), e1);
}

