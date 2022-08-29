#include <gtest/gtest.h>
#include <msgpack.hpp>

#include <libmuscle/mpp_message.hpp>
#include <libmuscle/mcp/tcp_transport_server.hpp>
#include <libmuscle/mpp_client.hpp>

#include <libmuscle/data.hpp>
#include <libmuscle/post_office.hpp>
#include <libmuscle/util.hpp>
#include <ymmsl/ymmsl.hpp>

#include <string>
#include <utility>


using libmuscle::impl::Data;
using libmuscle::impl::DataConstRef;
using libmuscle::impl::MPPMessage;
using libmuscle::impl::MPPClient;
using libmuscle::impl::mcp::TcpTransportServer;
using libmuscle::impl::PostOffice;

using ymmsl::Reference;


int main(int argc, char *argv[]) {
    ::testing::InitGoogleTest(&argc, argv);
    return RUN_ALL_TESTS();
}

TEST(test_tcp_communication, send_receive) {
    PostOffice post_office;
    Reference receiver("test_receiver.port");

    MPPMessage msg(
            "test_sender.port", receiver, 10,
            0.0, 1.0,
            Data::dict("par1", 13), 1,
            Data::dict("var1", 1, "var2", 2.0, "var3", "3"));
    auto msg_data = std::make_unique<DataConstRef>(msg.encoded());
    post_office.deposit(receiver, std::move(msg_data));

    TcpTransportServer server(post_office);
    std::vector<std::string> locations = {server.get_location()};
    MPPClient client(locations);
    DataConstRef bytes = client.receive(receiver);
    MPPMessage m = MPPMessage::from_bytes(bytes);

    ASSERT_EQ(m.sender, "test_sender.port");
    ASSERT_EQ(m.receiver, "test_receiver.port");
    ASSERT_EQ(m.port_length, 10);
    ASSERT_EQ(m.timestamp, 0.0);
    ASSERT_EQ(m.next_timestamp, 1.0);
    ASSERT_EQ(m.settings_overlay["par1"].as<int>(), 13);
    ASSERT_EQ(m.message_number, 1);
    ASSERT_EQ(m.data["var1"].as<int>(), 1);
    ASSERT_EQ(m.data["var2"].as<double>(), 2.0);
    ASSERT_EQ(m.data["var3"].as<std::string>(), "3");

    client.close();
    server.close();
}

