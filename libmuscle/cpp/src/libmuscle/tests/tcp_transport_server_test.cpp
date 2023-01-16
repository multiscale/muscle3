/* This is a part of the integration test suite, and is run from a Python
 * test in /integration_test. It is not a unit test.
 */
#include <libmuscle/data.hpp>
#include <libmuscle/mcp/data_pack.hpp>
#include <libmuscle/mpp_message.hpp>
#include <libmuscle/mcp/tcp_transport_server.hpp>
#include <libmuscle/post_office.hpp>
#include <ymmsl/ymmsl.hpp>

#include <cassert>
#include <iostream>
#include <ostream>
#include <memory>

#include <msgpack.hpp>


using libmuscle::impl::PostOffice;
using libmuscle::impl::Data;
using libmuscle::impl::DataConstRef;
using libmuscle::impl::MPPMessage;
using libmuscle::impl::mcp::TcpTransportServer;
using ymmsl::Reference;
using ymmsl::Settings;


int main(int argc, char *argv[]) {
    PostOffice post_office;
    Reference receiver("test_receiver.port");

    Settings overlay_settings;
    overlay_settings["par1"] = 13;

    auto data_dict = Data::dict("var1", 1, "var2", 2.0, "var3", "3");

    MPPMessage msg(
            "test_sender.port", receiver, 10,
            0.0, 1.0,
            overlay_settings,
            0, 6.0,
            data_dict);
    auto msg_data = std::make_unique<DataConstRef>(msg.encoded());
    post_office.deposit(receiver, std::move(msg_data));

    TcpTransportServer server(post_office);
    std::cout << server.get_location() << std::endl;

    post_office.wait_for_receivers();

    server.close();
    return 0;
}

