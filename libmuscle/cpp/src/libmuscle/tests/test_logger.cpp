// Inject mocks
#define LIBMUSCLE_MOCK_MMP_CLIENT <mocks/mock_mmp_client.hpp>

// into the real implementation,
#include <libmuscle/logger.cpp>
#include <libmuscle/logging.cpp>
#include <libmuscle/timestamp.cpp>

// then add mock implementations as needed.
#include <mocks/mock_mmp_client.hpp>

// Test code dependencies
#include <libmuscle/tests/fixtures.hpp>
#include <libmuscle/logger.hpp>
#include <libmuscle/logging.hpp>
#include <libmuscle/namespace.hpp>

#include <gtest/gtest.h>


using libmuscle::_MUSCLE_IMPL_NS::Logger;
using libmuscle::_MUSCLE_IMPL_NS::LogLevel;
using libmuscle::_MUSCLE_IMPL_NS::MockMMPClient;
using ymmsl::Reference;


int main(int argc, char *argv[]) {
    ::testing::InitGoogleTest(&argc, argv);
    return RUN_ALL_TESTS();
}


struct libmuscle_logging : ::testing::Test {
    RESET_MOCKS(MockMMPClient);
    MockMMPClient mock_mmp_client_;
};


TEST_F(libmuscle_logging, test_logger) {
    Logger logger("test_instance[10]", "", mock_mmp_client_);

    logger.log(LogLevel::CRITICAL, "Testing: ", 10, " == ", 10.0);

    auto const & msg = mock_mmp_client_.submit_log_message.call_arg<0>();
    ASSERT_EQ(msg.instance_id, "test_instance[10]");
    ASSERT_GT(msg.timestamp.seconds, 0.0);
    ASSERT_EQ(msg.level, LogLevel::CRITICAL);
    ASSERT_EQ(msg.text, "Testing: 10 == 10");
}

TEST_F(libmuscle_logging, test_set_level) {
    Logger logger("test_instance", "", mock_mmp_client_);

    auto const & submit = mock_mmp_client_.submit_log_message;

    // default is WARNING
    logger.log(LogLevel::WARNING, "WARNING");
    ASSERT_EQ(submit.call_arg<0>().text, "WARNING");

    logger.log(LogLevel::INFO, "INFO");
    ASSERT_EQ(submit.call_arg<0>().text, "WARNING");

    logger.log(LogLevel::WARNING, "WARNING2");
    ASSERT_EQ(submit.call_arg<0>().text, "WARNING2");

    logger.log(LogLevel::DEBUG, "DEBUG");
    ASSERT_EQ(submit.call_arg<0>().text, "WARNING2");

    logger.log(LogLevel::CRITICAL, "CRITICAL");
    ASSERT_EQ(submit.call_arg<0>().text, "CRITICAL");

    logger.set_remote_level(LogLevel::DEBUG);

    logger.log(LogLevel::DEBUG, "DEBUG");
    ASSERT_EQ(submit.call_arg<0>().text, "DEBUG");

    logger.log(LogLevel::CRITICAL, "CRITICAL");
    ASSERT_EQ(submit.call_arg<0>().text, "CRITICAL");

    logger.set_remote_level(LogLevel::CRITICAL);

    logger.log(LogLevel::ERROR, "ERROR");
    ASSERT_EQ(submit.call_arg<0>().text, "CRITICAL");

    logger.log(LogLevel::CRITICAL, "CRITICAL2");
    ASSERT_EQ(submit.call_arg<0>().text, "CRITICAL2");
}

