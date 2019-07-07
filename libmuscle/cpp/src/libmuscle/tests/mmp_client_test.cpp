/* This is a part of the integration test suite, and is run from a Python
 * test in /integration_test. It is not a unit test.
 */
#include <libmuscle/logging.hpp>
#include <libmuscle/mmp_client.hpp>

using libmuscle::LogLevel;
using libmuscle::LogMessage;
using libmuscle::MMPClient;
using libmuscle::Timestamp;


int main(int argc, char *argv[]) {
    auto client = MMPClient("localhost:9000");

    client.submit_log_message(LogMessage("test_logging", Timestamp(2.0),
                LogLevel::CRITICAL, "Integration testing"));

    return 0;
}

