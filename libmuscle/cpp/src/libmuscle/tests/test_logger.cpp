// Inject mocks
#define LIBMUSCLE_MOCK_MMP_CLIENT <mocks/mock_mmp_client.hpp>

// into the real implementation,
#include <libmuscle/logger.cpp>
#include <libmuscle/logging.cpp>
#include <libmuscle/timestamp.cpp>

// then add mock implementations as needed.
#include <mocks/mock_mmp_client.cpp>


// Test code dependencies
#include <libmuscle/logger.hpp>
#include <libmuscle/logging.hpp>

#include <gtest/gtest.h>


using libmuscle::impl::Logger;
using libmuscle::impl::LogLevel;
using libmuscle::impl::MockMMPClient;


int main(int argc, char *argv[]) {
    ::testing::InitGoogleTest(&argc, argv);
    return RUN_ALL_TESTS();
}

// Helpers for accessing internal state
namespace libmuscle { namespace impl {

struct TestTimestamp {
    static double seconds_(Timestamp const & timestamp) {
        return timestamp.seconds_;
    }
};

} }

using libmuscle::impl::TestTimestamp;

/* Mocks have internal state, which needs to be reset before each test. This
 * means that the tests are not reentrant, and cannot be run in parallel.
 * It's all fast enough, so that's not a problem.
 */
void reset_mocks() {
    MockMMPClient::reset();
}

TEST(libmuscle_logging, test_logger) {
    reset_mocks();
    MockMMPClient manager("");
    Logger logger("test_instance[10]", manager);

    logger.log(LogLevel::CRITICAL, "Testing: ", 10, " == ", 10.0);

    auto const & msg = MockMMPClient::last_submitted_log_message;
    ASSERT_EQ(msg.instance_id, "test_instance[10]");
    ASSERT_GT(TestTimestamp::seconds_(msg.timestamp), 0.0);
    ASSERT_EQ(msg.level, LogLevel::CRITICAL);
    ASSERT_EQ(msg.text, "Testing: 10 == 10");
}

TEST(libmuscle_logging, test_set_level) {
    reset_mocks();
    MockMMPClient manager("");
    Logger logger("test_instance", manager);

    // default is WARNING
    logger.log(LogLevel::WARNING, "WARNING");
    ASSERT_EQ(MockMMPClient::last_submitted_log_message.text, "WARNING");

    logger.log(LogLevel::INFO, "INFO");
    ASSERT_EQ(MockMMPClient::last_submitted_log_message.text, "WARNING");

    logger.log(LogLevel::WARNING, "WARNING2");
    ASSERT_EQ(MockMMPClient::last_submitted_log_message.text, "WARNING2");

    logger.log(LogLevel::DEBUG, "DEBUG");
    ASSERT_EQ(MockMMPClient::last_submitted_log_message.text, "WARNING2");

    logger.log(LogLevel::CRITICAL, "CRITICAL");
    ASSERT_EQ(MockMMPClient::last_submitted_log_message.text, "CRITICAL");

    logger.set_remote_level(LogLevel::DEBUG);

    logger.log(LogLevel::DEBUG, "DEBUG");
    ASSERT_EQ(MockMMPClient::last_submitted_log_message.text, "DEBUG");

    logger.log(LogLevel::CRITICAL, "CRITICAL");
    ASSERT_EQ(MockMMPClient::last_submitted_log_message.text, "CRITICAL");

    logger.set_remote_level(LogLevel::CRITICAL);

    logger.log(LogLevel::ERROR, "ERROR");
    ASSERT_EQ(MockMMPClient::last_submitted_log_message.text, "CRITICAL");

    logger.log(LogLevel::CRITICAL, "CRITICAL2");
    ASSERT_EQ(MockMMPClient::last_submitted_log_message.text, "CRITICAL2");
}

