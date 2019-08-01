/* This is a part of the integration test suite, and is run from a Python
 * test in /integration_test. It is not a unit test.
 */
#include <libmuscle/mcp/data.hpp>
#include <libmuscle/mcp/data_pack.hpp>
#include <libmuscle/mcp/message.hpp>
#include <libmuscle/mcp/client.hpp>
#include <libmuscle/mcp/tcp_client.hpp>
#include <ymmsl/identity.hpp>

#include <cassert>
#include <iostream>
#include <ostream>
#include <memory>

#include <msgpack.hpp>


using libmuscle::mcp::DataConstRef;
using libmuscle::mcp::Message;
using libmuscle::mcp::Client;
using libmuscle::mcp::TcpClient;
using ymmsl::Reference;


int main(int argc, char *argv[]) {
    // get server location from command line
    assert(argc == 2);
    std::string server_location(argv[1]);

    // start tcp client for the receiver
    assert(TcpClient::can_connect_to(server_location));

    Reference instance_id("test_receiver");
    std::shared_ptr<Client> client = std::make_unique<TcpClient>(instance_id, server_location);

    // receive a message
    Reference receiver("test_receiver.test_port2");
    Message message = client->receive(receiver);

    // check message
    assert(message.sender == Reference("test_sender.test_port"));
    assert(message.receiver == receiver);
    assert(message.port_length == 10);
    assert(message.timestamp == 1.0);
    assert(message.next_timestamp == 2.0);

    auto zone = std::make_shared<msgpack::zone>();
    DataConstRef overlay = ::libmuscle::mcp::unpack_data(
            zone, message.parameter_overlay.as_byte_array(),
            message.parameter_overlay.size());

    assert(overlay.is_a_dict());
    assert(overlay["test_setting"].is_a<int>());
    assert(overlay["test_setting"].as<int>() == 42);

    DataConstRef data = ::libmuscle::mcp::unpack_data(
            zone, message.data.as_byte_array(),
            message.data.size());

    assert(data.is_a_dict());
    assert(data["test1"].is_a<int>());
    assert(data["test1"].as<int>() == 10);
    assert(data["test2"].is_a_list());
    assert(data["test2"][0].is_nil());
    assert(data["test2"][1].as<bool>() == true);
    assert(data["test2"][2].as<std::string>() == "testing");

    return 0;
}

