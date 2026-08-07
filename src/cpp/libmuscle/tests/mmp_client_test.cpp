/* This is a part of the integration test suite, and is run from a Python
 * test in /integration_test. It is not a unit test.
 */
#include <libmuscle/logging.hpp>
#include <libmuscle/mmp_client.hpp>
#include <libmuscle/namespace.hpp>
#include <ymmsl/ymmsl.hpp>

#include <cassert>
#include <tuple>


using libmuscle::_MUSCLE_IMPL_NS::LogLevel;
using libmuscle::_MUSCLE_IMPL_NS::LogMessage;
using libmuscle::_MUSCLE_IMPL_NS::MMPClient;
using libmuscle::_MUSCLE_IMPL_NS::Timestamp;
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
    auto peer_info = client.request_peers();

    auto const & incoming_ports = peer_info.list_incoming_ports();
    assert(incoming_ports.size() == 1);
    assert(std::get<0>(incoming_ports[0]) == "micro.in");

    auto const & outgoing_ports = peer_info.list_outgoing_ports();
    assert(outgoing_ports.size() == 1);
    assert(std::get<0>(outgoing_ports[0]) == "micro.out");

    auto const & in_peer_ports = peer_info.get_peer_ports("micro.in");
    assert(in_peer_ports.size() == 1);
    assert(in_peer_ports[0] == "macro.out");

    auto const & out_peer_ports = peer_info.get_peer_ports("micro.out");
    assert(out_peer_ports.size() == 1);
    assert(out_peer_ports[0] == "macro.in");

    auto const & peer_dimensions = peer_info.get_peer_dims("macro");
    assert(peer_dimensions.size() == 1);
    assert(peer_dimensions[0] == 10);

    auto const & peer_locations = peer_info.get_peer_locations("macro");
    assert(peer_locations.size() == 2);
    assert(peer_locations[0] == "tcp:test3");
    assert(peer_locations[1] == "tcp:test4");
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

