/* This is a part of the integration test suite, and is run from a Python
 * test in /integration_test. It is not a unit test.
 */
#include <libmuscle/logging.hpp>
#include <libmuscle/mmp_client.hpp>
#include <ymmsl/settings.hpp>

#include <cassert>

using libmuscle::LogLevel;
using libmuscle::LogMessage;
using libmuscle::MMPClient;
using libmuscle::Timestamp;
using ymmsl::Settings;


void test_get_settings(MMPClient & client) {
    Settings settings(client.get_settings());

    assert(settings.at("test1") == 13);
    assert(settings.at("test2") == 13.3);
    assert(settings.at("test3") == "testing");
    assert(settings.at("test4") == true);
    assert(settings.at("test5") == std::vector<double>({2.3, 5.6}));

    auto test6 = settings.at("test6").as<std::vector<std::vector<double>>>();
    assert(test6[0][0] == 1.0);
    assert(test6[0][1] == 2.0);
    assert(test6[1][0] == 3.0);
    assert(test6[1][1] == 1.0);
}

void test_submit_log_message(MMPClient & client) {
    client.submit_log_message(LogMessage("test_logging", Timestamp(2.0),
                LogLevel::CRITICAL, "Integration testing"));
}


int main(int argc, char *argv[]) {
    auto client = MMPClient("localhost:9000");

    test_get_settings(client);
    test_submit_log_message(client);

    return 0;
}

