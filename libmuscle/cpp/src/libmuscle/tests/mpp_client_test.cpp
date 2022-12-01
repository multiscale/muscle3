/* This is a part of the integration test suite, and is run from a Python
 * test in /integration_test. It is not a unit test.
 */
#include <libmuscle/data.hpp>
#include <libmuscle/mcp/data_pack.hpp>
#include <libmuscle/mpp_message.hpp>
#include <libmuscle/mpp_client.hpp>
#include <ymmsl/ymmsl.hpp>

#include <cassert>
#include <memory>
#include <tuple>

#include <msgpack.hpp>


using libmuscle::impl::DataConstRef;
using libmuscle::impl::MPPMessage;
using libmuscle::impl::MPPClient;
using libmuscle::impl::mcp::unpack_data;
using ymmsl::Reference;
using ymmsl::Settings;


int main(int argc, char *argv[]) {
    // get server location from command line
    assert(argc == 2);
    std::string server_location(argv[1]);
    std::vector<std::string> server_locations = {server_location};

    // create client connecting to it
    MPPClient client(server_locations);

    // receive a message
    Reference receiver("test_receiver.test_port2");
    DataConstRef bytes = std::get<0>(client.receive(receiver));
    MPPMessage message = MPPMessage::from_bytes(bytes);

    // check message
    assert(message.sender == Reference("test_sender.test_port"));
    assert(message.receiver == receiver);
    assert(message.port_length == 10);
    assert(message.timestamp == 1.0);
    assert(message.next_timestamp == 2.0);

    auto overlay = message.settings_overlay.as<Settings>();
    assert(overlay["test_setting"].is_a<int64_t>());
    assert(overlay["test_setting"].as<int64_t>() == 42);

    assert(message.data.is_a_dict());
    assert(message.data["test1"].is_a<int>());
    assert(message.data["test1"].as<int>() == 10);
    assert(message.data["test2"].is_a_list());
    assert(message.data["test2"][0].is_nil());
    assert(message.data["test2"][1].as<bool>() == true);
    assert(message.data["test2"][2].as<std::string>() == "testing");

    return 0;
}

