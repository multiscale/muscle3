/* This is a part of the integration test suite, and is run from a Python
 * test in /integration_test. It is not a unit test.
 */
#include <libmuscle/data.hpp>
#include <libmuscle/mcp/data_pack.hpp>
#include <libmuscle/mcp/message.hpp>
#include <libmuscle/mcp/server.hpp>
#include <libmuscle/mcp/tcp_server.hpp>
#include <libmuscle/post_office.hpp>
#include <ymmsl/identity.hpp>

#include <cassert>
#include <iostream>
#include <ostream>
#include <memory>

#include <msgpack.hpp>


using libmuscle::PostOffice;
using libmuscle::Data;
using libmuscle::mcp::Message;
using libmuscle::mcp::Server;
using libmuscle::mcp::TcpServer;
using ymmsl::Reference;


int main(int argc, char *argv[]) {
    PostOffice post_office;
    Reference receiver("test_receiver.port");

    auto overlay_dict = Data::dict("par1", 13);
    msgpack::sbuffer overlay_buf;
    msgpack::pack(overlay_buf, overlay_dict);

    auto data_dict = Data::dict("var1", 1, "var2", 2.0, "var3", "3");
    msgpack::sbuffer data_buf;
    msgpack::pack(data_buf, data_dict);

    auto msg = std::make_unique<Message>(
            "test_sender.port", receiver, 10,
            0.0, 1.0,
            Data::byte_array(overlay_buf.data(), overlay_buf.size()),
            Data::byte_array(data_buf.data(), data_buf.size()));
    post_office.deposit(receiver, std::move(msg));

    TcpServer server("test_sender", post_office);
    std::cout << server.get_location() << std::endl;

    post_office.wait_for_receivers();

    server.close();
    return 0;
}

