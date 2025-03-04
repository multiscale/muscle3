// Inject mocks
#define LIBMUSCLE_MOCK_LOGGER <mocks/mock_logger.hpp>
#define LIBMUSCLE_MOCK_MMP_CLIENT <mocks/mock_mmp_client.hpp>
#define LIBMUSCLE_MOCK_MPP_CLIENT <mocks/mock_mpp_client.hpp>
#define LIBMUSCLE_MOCK_MPP_SERVER <mocks/mock_mpp_server.hpp>
#define LIBMUSCLE_MOCK_PORT_MANAGER <mocks/mock_port_manager.hpp>
#define LIBMUSCLE_MOCK_PROFILER <mocks/mock_profiler.hpp>

// into the real implementation under test.
#include <ymmsl/ymmsl.hpp>

#include <libmuscle/close_port.cpp>
#include <libmuscle/communicator.cpp>
#include <libmuscle/data.cpp>
#include <libmuscle/endpoint.cpp>
#include <libmuscle/mcp/data_pack.cpp>
#include <libmuscle/mpp_message.cpp>
#include <libmuscle/mcp/tcp_util.cpp>
#include <libmuscle/mcp/transport_client.cpp>
#include <libmuscle/message.cpp>
#include <libmuscle/peer_info.cpp>
#include <libmuscle/port.cpp>
#include <libmuscle/profiling.cpp>
#include <libmuscle/receive_timeout_handler.cpp>
#include <libmuscle/timestamp.cpp>

// Test code dependencies
#include <memory>
#include <stdexcept>
#include <gtest/gtest.h>
#include <libmuscle/communicator.hpp>
#include <libmuscle/namespace.hpp>
#include <fixtures.hpp>
#include <mocks/mock_mmp_client.hpp>
#include <mocks/mock_mpp_client.hpp>
#include <mocks/mock_mpp_server.hpp>
#include <mocks/mock_logger.hpp>
#include <mocks/mock_profiler.hpp>


int main(int argc, char *argv[]) {
    ::testing::InitGoogleTest(&argc, argv);
    return RUN_ALL_TESTS();
}


using libmuscle::_MUSCLE_IMPL_NS::Communicator;
using libmuscle::_MUSCLE_IMPL_NS::Data;
using libmuscle::_MUSCLE_IMPL_NS::DataConstRef;
using libmuscle::_MUSCLE_IMPL_NS::Endpoint;
using libmuscle::_MUSCLE_IMPL_NS::is_close_port;
using libmuscle::_MUSCLE_IMPL_NS::Message;
using libmuscle::_MUSCLE_IMPL_NS::MockLogger;
using libmuscle::_MUSCLE_IMPL_NS::MockMMPClient;
using libmuscle::_MUSCLE_IMPL_NS::MockMPPClient;
using libmuscle::_MUSCLE_IMPL_NS::MockMPPServer;
using libmuscle::_MUSCLE_IMPL_NS::MockPortManager;
using libmuscle::_MUSCLE_IMPL_NS::MockProfiler;
using libmuscle::_MUSCLE_IMPL_NS::MPPMessage;
using libmuscle::_MUSCLE_IMPL_NS::Optional;
using libmuscle::_MUSCLE_IMPL_NS::PeerDims;
using libmuscle::_MUSCLE_IMPL_NS::PeerInfo;
using libmuscle::_MUSCLE_IMPL_NS::PeerLocations;
using libmuscle::_MUSCLE_IMPL_NS::PortsDescription;
using libmuscle::_MUSCLE_IMPL_NS::mcp::ProfileData;
using libmuscle::_MUSCLE_IMPL_NS::mcp::TimeoutHandler;
using libmuscle::_MUSCLE_IMPL_NS::ProfileTimestamp;

using ymmsl::Conduit;
using ymmsl::Reference;


/* Fixture */
struct libmuscle_communicator
        : ConnectedPortManagerFixture
        , ::testing::Test
{
    RESET_MOCKS(
            MockLogger, MockMMPClient, MockMPPClient, MockMPPServer, MockProfiler);

    MockLogger logger_;
    MockProfiler profiler_;
    MockPortManager port_manager_;
    MockMMPClient manager_;

    Communicator communicator_;

    libmuscle_communicator()
        : communicator_("component", {}, connected_port_manager_, logger_, profiler_, manager_)
    {
        port_manager_.settings_in_connected.return_value = false;
    }
};


struct libmuscle_communicator2 : libmuscle_communicator {
    Communicator & connected_communicator_;

    libmuscle_communicator2()
        : connected_communicator_(communicator_)
    {
        std::vector<Conduit> conduits({
            Conduit("peer.out", "component.in"),
            Conduit("peer2.out_v", "component.in_v"),
            Conduit("peer3.out_r", "component.in_r"),
            Conduit("component.out_v", "peer2.in"),
            Conduit("component.out_r", "peer3.in_r"),
            Conduit("component.out", "peer.in")});

        PeerDims peer_dims({
                {Reference("peer"), {}},
                {Reference("peer2"), {13}},
                {Reference("peer3"), {}}});

        PeerLocations peer_locations({
                {Reference("peer"), {"tcp:peer:9001"}},
                {Reference("peer3"), {"tcp:peer3:9001"}},
                });
        for (int i = 0; i < 13; ++i) {
            auto port_name = std::string("peer2[") + std::to_string(i) + "]";
            peer_locations[port_name] = {"tcp:peer2:9001"};
        }

        PeerInfo peer_info("component", {}, conduits, peer_dims, peer_locations);
        connected_communicator_.set_peer_info(peer_info);
        // disable receive timeouts for these tests, so we can check call
        // signatures: mpp_client->receive.called_with(..., nullptr)
        connected_communicator_.set_receive_timeout(-1.0);
    }
};


/* Tests */
TEST_F(libmuscle_communicator, create_communicator) {}

TEST_F(libmuscle_communicator2, send_message) {
    Message msg(0.0, 1.0, "test", Settings({{"s0", 0}, {"s1", "1"}}));

    connected_communicator_.send_message("out_v", msg, 7, -1.0);

    auto & server = communicator_.server_;
    ASSERT_EQ(server.deposit.call_arg<0>(), "peer2[7].in");

    auto const & encoded_msg = *server.deposit.call_arg<1>();
    ASSERT_EQ(encoded_msg.sender, "component.out_v[7]");
    ASSERT_EQ(encoded_msg.receiver, "peer2[7].in");
    ASSERT_EQ(encoded_msg.timestamp, 0.0);
    ASSERT_EQ(encoded_msg.next_timestamp, 1.0);
    ASSERT_TRUE(encoded_msg.settings_overlay.is_a<Settings>());
    auto overlay = encoded_msg.settings_overlay.as<Settings>();
    ASSERT_EQ(overlay["s0"].as<int64_t>(), 0);
    ASSERT_EQ(overlay["s1"].as<std::string>(), "1");
    ASSERT_EQ(encoded_msg.saved_until, -1.0);
    ASSERT_EQ(encoded_msg.data.as<std::string>(), "test");
}

TEST_F(libmuscle_communicator2, send_message_disconnected) {
    Message msg(0.0, "not_connected", Settings());

    connected_communicator_.send_message("not_connected", msg);

    ASSERT_FALSE(communicator_.server_.deposit.called());
}

TEST_F(libmuscle_communicator2, receive_message) {
    MPPMessage msg(
            "peer.out", "component.in", {}, 2.0, 3.0,
            Settings({{"s0", "0"}, {"s1", true}}), 0, 1.0, "Testing");

    MockMPPClient::return_value.receive.return_value = std::make_tuple(
            msg.encoded(), ProfileData());

    auto recv_msg_saved_until = connected_communicator_.receive_message("in");
    auto const & recv_msg = std::get<0>(recv_msg_saved_until);
    double saved_until = std::get<1>(recv_msg_saved_until);

    auto & mpp_client = connected_communicator_.clients_.at("peer");
    ASSERT_TRUE(mpp_client->receive.called_with("component.in", nullptr));

    ASSERT_EQ(recv_msg.timestamp(), 2.0);
    ASSERT_EQ(recv_msg.next_timestamp(), 3.0);
    ASSERT_EQ(recv_msg.data().as<std::string>(), "Testing");
    ASSERT_EQ(recv_msg.settings().at("s0"), "0");
    ASSERT_TRUE(recv_msg.settings().at("s1").as<bool>());
    ASSERT_EQ(saved_until, 1.0);
}

TEST_F(libmuscle_communicator2, receive_message_vector) {
    MPPMessage msg(
            "peer2.out_v", "component.in_v", 5, 4.0, 6.0,
            Settings({{"s0", {0.0}}, {"s1", 1.0}}), 0, 3.5, "Testing2");

    MockMPPClient::return_value.receive.return_value = std::make_tuple(
            msg.encoded(), ProfileData());

    auto recv_msg_saved_until = connected_communicator_.receive_message("in_v", 5);
    auto const & recv_msg = std::get<0>(recv_msg_saved_until);
    double saved_until = std::get<1>(recv_msg_saved_until);

    auto mpp_client = connected_communicator_.clients_.at("peer2[5]").get();
    ASSERT_TRUE(mpp_client->receive.called_with("component.in_v[5]", nullptr));

    ASSERT_EQ(recv_msg.timestamp(), 4.0);
    ASSERT_EQ(recv_msg.next_timestamp(), 6.0);
    ASSERT_EQ(recv_msg.data().as<std::string>(), "Testing2");
    ASSERT_EQ(recv_msg.settings().at("s0"), std::vector<double>{0.0});
    ASSERT_EQ(recv_msg.settings().at("s1"), 1.0);
    ASSERT_EQ(saved_until, 3.5);
}

TEST_F(libmuscle_communicator2, receive_close_port) {
    MPPMessage msg(
            "peer.out", "component.in", {}, std::numeric_limits<double>::infinity(), {},
            Settings(), 0, 0.1, ClosePort());

    MockMPPClient::return_value.receive.return_value = std::make_tuple(
            msg.encoded(), ProfileData());

    connected_communicator_.receive_message("in");

    ASSERT_FALSE(mock_ports_.at("in")->is_open());
}

TEST_F(libmuscle_communicator2, receive_close_port_vector) {
    MPPMessage msg(
            "peer2.out_v", "component.in_v", 5, std::numeric_limits<double>::infinity(),
            {}, Settings(), 0, 3.5, ClosePort());

    MockMPPClient::return_value.receive.return_value = std::make_tuple(
            msg.encoded(), ProfileData());

    connected_communicator_.receive_message("in_v", 5);

    ASSERT_FALSE(mock_ports_["in_v"]->is_open(5));
}

TEST_F(libmuscle_communicator2, port_count_validation) {
    MPPMessage msg(
            "peer.out", "component.in",
            {}, 0.0, {}, Settings({{"test1", 12}}), 0, 7.6, "test");

    MockMPPClient::return_value.receive.return_value = std::make_tuple(
            msg.encoded(), ProfileData());

    connected_communicator_.receive_message("in");

    ASSERT_EQ(
            connected_port_manager_.get_port("in").get_message_counts(),
            std::vector<int>({1}));

    // the message received has message_number = 0 again
    ASSERT_THROW(connected_communicator_.receive_message("in"), std::runtime_error);
}

TEST_F(libmuscle_communicator2, port_discard_error_on_resume) {
    MPPMessage msg(
            "other.out[13]", "kernel[13].in",
            {}, 0.0, {}, Settings({{"test1", 12}}), 1, 2.3, "test");

    MockMPPClient::return_value.receive.return_value = std::make_tuple(
            msg.encoded(), ProfileData());

    connected_port_manager_.get_port("out").restore_message_counts({0});
    connected_port_manager_.get_port("in").restore_message_counts({2});

    for (auto & port : {"out", "in"}) {
        ASSERT_EQ(
                connected_port_manager_.get_port(port).is_resuming_,
                std::vector<bool>({true}));
        ASSERT_TRUE(connected_port_manager_.get_port(port).is_resuming());
    }

    // In the next block, the first message with message_number=1 is discarded.
    // The RuntimeError is raised when 'receiving' the second message with
    // message_number=1
    ASSERT_THROW(connected_communicator_.receive_message("in"), std::runtime_error);
    bool message_logged = false;
    for (auto const & log_args : logger_.caplog.call_args_list) {
        auto const & msg = std::get<1>(log_args);
        if (msg.find("Discarding received message") != msg.npos) {
            message_logged = true;
            break;
        }
    }
    ASSERT_TRUE(message_logged);
}

TEST_F(libmuscle_communicator2, port_discard_success_on_resume) {
    // TODO: add support to the mocking framework for assigning a vector of results
    // to side_effect? But call it return_values so it actually makes sense.
    std::vector<MPPMessage> side_effect;
    for (int message_number : {1, 2}) {
        side_effect.push_back(MPPMessage(
                "other.out[13]", "kernel[13].in",
                {}, 0.0, {}, Settings({{"test1", 12}}), message_number, 1.0,
                Data::dict("this is message", message_number)));
    }

    int count = 0;

    MockMPPClient::return_value.receive.side_effect = [&](Reference const &, TimeoutHandler *) {
        return std::make_tuple(
                side_effect.at(count++).encoded(), ProfileData());
    };

    connected_port_manager_.get_port("out").restore_message_counts({0});
    connected_port_manager_.get_port("in").restore_message_counts({2});

    for (auto const & port : {"out", "in"}) {
        ASSERT_EQ(
                connected_port_manager_.get_port(port).is_resuming_,
                std::vector<bool>({true}));
        ASSERT_TRUE(connected_port_manager_.get_port(port).is_resuming());
    }

    auto recv_msg_saved_until = connected_communicator_.receive_message("in");
    auto const & recv_msg = std::get<0>(recv_msg_saved_until);

    bool message_logged = false;
    for (auto const & log_args : logger_.caplog.call_args_list) {
        auto const & log_msg = std::get<1>(log_args);
        if (log_msg.find("Discarding received message") != log_msg.npos) {
            message_logged = true;
            break;
        }
    }
    ASSERT_TRUE(message_logged);

    // message_number=1 should have been discarded
    ASSERT_EQ(recv_msg.data()["this is message"].as<int>(), 2);
    ASSERT_EQ(
            connected_communicator_.port_manager_.get_port("in").get_message_counts(),
            std::vector<int>({3}));
}

TEST_F(libmuscle_communicator2, test_shutdown) {
    std::unordered_map<Reference, std::unique_ptr<MPPMessage>> messages;

    messages["component.in"] = std::make_unique<MPPMessage>(
            "peer.out", "component.in", Optional<int>(),
            std::numeric_limits<double>::infinity(), Optional<double>(), Settings(),
            0, 0.0, ClosePort());

    std::vector<std::tuple<std::string, std::string, std::string>> port_sender({
            {"in_v", "peer2[", "].out_v"},
            {"in_r", "peer3.out[", "]"}});

    for (auto const & port_name_sender : port_sender) {
        auto const & port_name = std::get<0>(port_name_sender);
        auto const & snd1 = std::get<1>(port_name_sender);
        auto const & snd2 = std::get<2>(port_name_sender);

        auto & port = connected_port_manager_.get_port(port_name);
        for (int slot = 0; slot < port.get_length(); ++slot) {
            Reference sender(snd1 + std::to_string(slot) + snd2);
            Reference receiver("component." + port_name + "[" + std::to_string(slot) + "]");
            messages[receiver] = std::make_unique<MPPMessage>(
                    sender, receiver, slot, std::numeric_limits<double>::infinity(),
                    Optional<double>(), Settings(), 0, 3.5,
                    ClosePort());
        }
    }

    MockMPPClient::return_value.receive.side_effect = [&](Reference const & receiver, TimeoutHandler*) {
        return std::make_tuple(messages.at(receiver)->encoded(), ProfileData());
    };

    connected_communicator_.shutdown();

    std::unordered_set<Reference> expected_receivers({"peer.in"});
    auto const & pm = connected_port_manager_;
    for (int slot = 0; slot < pm.get_port("out_v").get_length(); ++slot)
        expected_receivers.emplace("peer2[" + std::to_string(slot) + "].in");
    for (int slot = 0; slot < pm.get_port("out_r").get_length(); ++slot)
        expected_receivers.emplace("peer3.in[" + std::to_string(slot) + "]");

    auto const & srv = connected_communicator_.server_;
    for (auto const & args: srv.deposit.call_args_list) {
        ASSERT_TRUE(expected_receivers.count(std::get<0>(args)));
        std::shared_ptr<MPPMessage> msg = std::get<1>(args);
        ASSERT_TRUE(is_close_port(msg->data));
        expected_receivers.erase(std::get<0>(args));
    }

    ASSERT_TRUE(expected_receivers.empty());
}

