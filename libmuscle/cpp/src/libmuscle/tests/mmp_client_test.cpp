/* This is a part of the integration test suite, and is run from a Python
 * test in /integration_test. It is not a unit test.
 */
#include <libmuscle/logging.hpp>
#include <libmuscle/mmp_client.hpp>
#include <ymmsl/settings.hpp>

using libmuscle::LogLevel;
using libmuscle::LogMessage;
using libmuscle::MMPClient;
using libmuscle::Timestamp;
using ymmsl::Settings;


bool settings_ok(Settings const & settings) {
    if (settings.at("test1") != 13)
        return false;
    if (settings.at("test2") != 13.3)
        return false;
    if (settings.at("test3") != "testing")
        return false;
    if (settings.at("test4") != true)
        return false;
    if (settings.at("test5") != std::vector<double>({2.3, 5.6}))
        return false;
    auto test6 = settings.at("test6").get<std::vector<std::vector<double>>>();
    if (test6[0][0] != 1.0 || test6[0][1] != 2.0 || test6[1][0] != 3.0 || test6[1][1] != 1.0)
        return false;
    return true;
}


int main(int argc, char *argv[]) {
    auto client = MMPClient("localhost:9000");

    Settings settings(client.get_settings());

    if (!settings_ok(settings))
        return 1;

    client.submit_log_message(LogMessage("test_logging", Timestamp(2.0),
                LogLevel::CRITICAL, "Integration testing"));

    return 0;
}

