/* This is a part of the integration test suite, and is run from a Python
 * test in /integration_test. It is not a unit test.
 */
#include <libmuscle/logging.hpp>
#include <libmuscle/mmp_client.hpp>
#include <ymmsl/ymmsl.hpp>

#include <cassert>
#include <tuple>


using libmuscle::impl::LogLevel;
using libmuscle::impl::LogMessage;
using libmuscle::impl::MMPClient;
using libmuscle::impl::Timestamp;
using ymmsl::Operator;
using ymmsl::Port;
using ymmsl::Reference;
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

void test_register_instance(MMPClient & client) {
    client.register_instance(
            {"tcp:test1", "tcp:test2"},
            {Port("out", Operator::O_F), Port("in", Operator::F_INIT)});
}

void test_request_peers(MMPClient & client) {
    auto result = client.request_peers();
    assert(std::get<0>(result).size() == 2);
    assert(std::get<0>(result)[0].sender == "macro.out");
    assert(std::get<0>(result)[0].receiver == "micro.in");
    assert(std::get<0>(result)[1].sender == "micro.out");
    assert(std::get<0>(result)[1].receiver == "macro.in");

    assert(std::get<1>(result).size() == 1);
    assert(std::get<1>(result).at("macro").size() == 1);
    assert(std::get<1>(result).at("macro").at(0) == 10);

    assert(std::get<2>(result).size() == 1);
    assert(std::get<2>(result).at("macro").size() == 2);
    assert(std::get<2>(result).at("macro")[0] == "tcp:test3");
    assert(std::get<2>(result).at("macro")[1] == "tcp:test4");
}

void test_deregister_instance(MMPClient & client) {
    client.deregister_instance();
}

int main(int argc, char *argv[]) {
    MMPClient client(Reference("micro[3]"), argv[1]);

    test_get_settings(client);
    test_submit_log_message(client);
    test_register_instance(client);
    test_deregister_instance(client);

    return 0;
}

