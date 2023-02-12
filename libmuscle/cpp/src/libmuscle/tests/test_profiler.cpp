// Inject mocks
#define LIBMUSCLE_MOCK_MMP_CLIENT <mocks/mock_mmp_client.hpp>

// into the real implementation,
#include <libmuscle/profiler.cpp>
#include <libmuscle/profiling.cpp>
#include <libmuscle/timestamp.cpp>

// then add mock implementations as needed.
#include <mocks/mock_mmp_client.cpp>


// Test code dependencies
#include <libmuscle/profiler.hpp>
#include <libmuscle/profiling.hpp>

#include <utility>
#include <gtest/gtest.h>


using libmuscle::impl::Profiler;
using libmuscle::impl::ProfileEvent;
using libmuscle::impl::ProfileEventType;
using libmuscle::impl::ProfileTimestamp;
using libmuscle::impl::MockMMPClient;
using ymmsl::Port;


int main(int argc, char *argv[]) {
    ::testing::InitGoogleTest(&argc, argv);
    return RUN_ALL_TESTS();
}


namespace libmuscle { namespace impl {

// Helper for accessing internal state

struct TestProfiler {
    static std::vector<ProfileEvent> & events_(Profiler & profiler) {
        return profiler.events_;
    }
};


// Helpers for comparison, not needed in the main code so put here.
bool operator==(ProfileTimestamp const & lhs, ProfileTimestamp const & rhs) {
    return lhs.nanoseconds == rhs.nanoseconds;
}

bool operator<(ProfileTimestamp const & lhs, ProfileTimestamp const & rhs) {
    return lhs.nanoseconds < rhs.nanoseconds;
}

bool operator==(Port const & lhs, Port const & rhs) {
    return lhs.name == rhs.name && lhs.oper == rhs.oper;
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

using libmuscle::impl::TestProfiler;


/* Mocks have internal state, which needs to be reset before each test. This
 * means that the tests are not reentrant, and cannot be run in parallel.
 * It's all fast enough, so that's not a problem.
 */
void reset_mocks() {
    MockMMPClient::reset();
}


TEST(libmuscle_profiler, test_recording_events) {
    reset_mocks();
    MockMMPClient mock_mmp_client(Reference("test_instance[10]"), "");
    Profiler profiler(mock_mmp_client);

    ProfileTimestamp t1, t2;
    ProfileEvent e(ProfileEventType::register_, t1, t2);

    profiler.record_event(ProfileEvent(e));

    ASSERT_EQ(e.start_time, t1);
    ASSERT_EQ(e.stop_time, t2);
    ASSERT_EQ(TestProfiler::events_(profiler).at(0), e);
}


TEST(libmuscle_profiler, test_auto_stop_time) {
    reset_mocks();
    MockMMPClient mock_mmp_client(Reference("test_instance[10]"), "");
    Profiler profiler(mock_mmp_client);

    ProfileTimestamp t1;
    ProfileEvent e(ProfileEventType::send, t1);

    profiler.record_event(std::move(e));

    auto const & e2 = TestProfiler::events_(profiler).at(0);
    ASSERT_EQ(e2.start_time, t1);
    ASSERT_TRUE(e2.stop_time.is_set());
    ASSERT_LT(e2.start_time.get(), e2.stop_time.get());
}

TEST(libmuscle_profiler, test_send_to_mock_mmp_client) {
    reset_mocks();
    MockMMPClient mock_mmp_client(Reference("test_instance[10]"), "");
    Profiler profiler(mock_mmp_client);

    ProfileEvent e1(
            ProfileEventType::receive, ProfileTimestamp(), ProfileTimestamp());
    profiler.record_event(ProfileEvent(e1));

    for (int i = 1; i < 99; ++i) {
        ProfileEvent e(
                ProfileEventType::send, ProfileTimestamp(), ProfileTimestamp());
        profiler.record_event(std::move(e));
    }

    ASSERT_EQ(mock_mmp_client.last_submitted_profile_events.size(), 0u);

    ProfileEvent e2(
            ProfileEventType::receive_transfer, ProfileTimestamp(), ProfileTimestamp());
    profiler.record_event(ProfileEvent(e2));

    ASSERT_EQ(mock_mmp_client.last_submitted_profile_events.size(), 100u);
    ASSERT_EQ(mock_mmp_client.last_submitted_profile_events.at(0), e1);
    ASSERT_EQ(mock_mmp_client.last_submitted_profile_events.at(99), e2);
}

