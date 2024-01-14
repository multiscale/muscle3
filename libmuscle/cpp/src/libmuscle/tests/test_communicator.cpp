// Inject mocks
#define LIBMUSCLE_MOCK_LOGGER <mocks/mock_logger.hpp>
#define LIBMUSCLE_MOCK_MPP_CLIENT <mocks/mock_mpp_client.hpp>
#define LIBMUSCLE_MOCK_MCP_TCP_TRANSPORT_SERVER <mocks/mcp/mock_tcp_transport_server.hpp>
#define LIBMUSCLE_MOCK_PEER_MANAGER <mocks/mock_peer_manager.hpp>
#define LIBMUSCLE_MOCK_POST_OFFICE <mocks/mock_post_office.hpp>
#define LIBMUSCLE_MOCK_PROFILER <mocks/mock_profiler.hpp>

// into the real implementation under test.
#include <ymmsl/ymmsl.hpp>

#include <libmuscle/close_port.cpp>
#include <libmuscle/communicator.cpp>
#include <libmuscle/data.cpp>
#include <libmuscle/endpoint.cpp>
#include <libmuscle/mcp/data_pack.cpp>
#include <libmuscle/mpp_message.cpp>
#include <libmuscle/mcp/tcp_transport_client.cpp>
#include <libmuscle/mcp/tcp_util.cpp>
#include <libmuscle/mcp/transport_client.cpp>
#include <libmuscle/mcp/transport_server.cpp>
#include <libmuscle/message.cpp>
#include <libmuscle/port.cpp>
#include <libmuscle/profiling.cpp>
#include <libmuscle/timestamp.cpp>

// Test code dependencies
#include <memory>
#include <stdexcept>
#include <gtest/gtest.h>
#include <fixtures.hpp>
#include <libmuscle/communicator.hpp>
#include <libmuscle/namespace.hpp>
#include <mocks/mock_mpp_client.hpp>
#include <mocks/mcp/mock_tcp_transport_server.hpp>
#include <mocks/mock_logger.hpp>
#include <mocks/mock_peer_manager.hpp>
#include <mocks/mock_post_office.hpp>
#include <mocks/mock_profiler.hpp>


using libmuscle::_MUSCLE_IMPL_NS::Communicator;
using libmuscle::_MUSCLE_IMPL_NS::Data;
using libmuscle::_MUSCLE_IMPL_NS::Endpoint;
using libmuscle::_MUSCLE_IMPL_NS::Optional;
using libmuscle::_MUSCLE_IMPL_NS::PeerDims;
using libmuscle::_MUSCLE_IMPL_NS::PeerLocations;
using libmuscle::_MUSCLE_IMPL_NS::PortsDescription;
using libmuscle::_MUSCLE_IMPL_NS::Message;
using libmuscle::_MUSCLE_IMPL_NS::MockMPPClient;
using libmuscle::_MUSCLE_IMPL_NS::MockPeerManager;
using libmuscle::_MUSCLE_IMPL_NS::MockPostOffice;
using libmuscle::_MUSCLE_IMPL_NS::MockProfiler;
using libmuscle::_MUSCLE_IMPL_NS::mcp::MockTcpTransportServer;
using libmuscle::_MUSCLE_IMPL_NS::MPPMessage;
using libmuscle::_MUSCLE_IMPL_NS::ProfileTimestamp;

using ymmsl::Conduit;
using ymmsl::Identifier;
using ymmsl::Reference;


int main(int argc, char *argv[]) {
    ::testing::InitGoogleTest(&argc, argv);
    return RUN_ALL_TESTS();
}


struct libmuscle_communicator : ::testing::Test {
    RESET_MOCKS(
            ::libmuscle::_MUSCLE_IMPL_NS::MockLogger,
            ::libmuscle::_MUSCLE_IMPL_NS::MockMPPClient,
            ::libmuscle::_MUSCLE_IMPL_NS::MockPeerManager,
            ::libmuscle::_MUSCLE_IMPL_NS::MockPostOffice,
            ::libmuscle::_MUSCLE_IMPL_NS::MockProfiler,
            ::libmuscle::_MUSCLE_IMPL_NS::mcp::MockTcpTransportServer);

    ::libmuscle::_MUSCLE_IMPL_NS::MockLogger mock_logger_;
    ::libmuscle::_MUSCLE_IMPL_NS::MockProfiler mock_profiler_;

    MPPMessage next_received_message;

    libmuscle_communicator()
        : next_received_message(
                "test.out", "test2.in", 0, 0.0, 1.0, Settings({{"test2", 3.1}}),
                0, 9.0, Data::dict("test1", 12))
    {
        MockPeerManager::return_value.is_connected.return_value = true;

        auto & ret_val = MockMPPClient::return_value;

        using RecvRet = std::tuple<
            DataConstRef, std::tuple<
                ProfileTimestamp, ProfileTimestamp, ProfileTimestamp>>;

        ret_val.receive.side_effect = [this](Reference const &) -> RecvRet {
            return std::make_tuple(
                    next_received_message.encoded(), std::make_tuple(
                        ProfileTimestamp(1.0), ProfileTimestamp(2.0),
                        ProfileTimestamp(3.0)));
        };
    }

    std::unique_ptr<Communicator> connected_communicator() {
        std::unique_ptr<Communicator> comm(new Communicator(
                Reference("kernel"), {13}, {}, mock_logger_, mock_profiler_));

        std::vector<Conduit> conduits({
            Conduit("kernel.out", "other.in"),
            Conduit("other.out", "kernel.in")});

        PeerDims peer_dims({{Reference("other"), {1}}});

        PeerLocations peer_locations({
                {Reference("other"), {"tcp:test"}}});

        auto & peer_manager = MockPeerManager::return_value;
        peer_manager.get_peer_dims.return_value = std::vector<int>({1});
        peer_manager.get_peer_endpoints.side_effect = []
            (Identifier const & port, std::vector<int> const & slot)
        {
            Reference port_slot(port);
            port_slot += slot;

            if (port_slot == "out")
                return std::vector<Endpoint>({Endpoint("other", {}, "in", {13})});
            if (port_slot == "in")
                return std::vector<Endpoint>({Endpoint("other", {}, "out", {13})});
            throw std::runtime_error(
                    "Invalid port/slot " + std::string(port_slot) + " in get_peer_endpoints");
        };

        peer_manager.get_peer_locations.return_value = std::vector<std::string>(
                {std::string("tcp:test")});

        comm->connect(conduits, peer_dims, peer_locations);
        return comm;
    }

    std::unique_ptr<Communicator> connected_communicator2() {
        std::unique_ptr<Communicator> comm(new Communicator(
                Reference("other"), {}, {}, mock_logger_, mock_profiler_));

        std::vector<Conduit> conduits({
            Conduit("kernel.out", "other.in"),
            Conduit("other.out", "kernel.in")});

        PeerDims peer_dims({{Reference("kernel"), {20}}});

        PeerLocations peer_locations({
                {Reference("kernel"), {"tcp:test"}}});

        auto & peer_manager = MockPeerManager::return_value;
        peer_manager.get_peer_dims.return_value = std::vector<int>({20});
        peer_manager.get_peer_endpoints.side_effect = []
            (Identifier const & port, std::vector<int> const & slot)
        {
            Reference port_slot(port);
            port_slot += slot;

            if (port_slot == "in[13]")
                return std::vector<Endpoint>({Endpoint("kernel", {13}, "out", {})});
            if (port_slot == "out[13]")
                return std::vector<Endpoint>({Endpoint("kernel", {13}, "in", {})});
            throw std::runtime_error(
                    "Invalid port/slot " + std::string(port_slot) + " in get_peer_endpoints");
        };

        peer_manager.get_peer_locations.return_value = std::vector<std::string>(
                {std::string("tcp:test")});

        comm->connect(conduits, peer_dims, peer_locations);
        return comm;
    }

    std::unique_ptr<Communicator> connected_communicator3() {
        PortsDescription desc({
                {Operator::O_I, {"out[]"}},
                {Operator::S, {"in[]"}}
                });

        std::unique_ptr<Communicator> comm(new Communicator(
                Reference("kernel"), {}, desc, mock_logger_, mock_profiler_));

        std::vector<Conduit> conduits({
            Conduit("kernel.out", "other.in"),
            Conduit("other.out", "kernel.in")});

        PeerDims peer_dims({{Reference("other"), {}}});

        PeerLocations peer_locations({
                {Reference("other"), {"tcp:test"}}});

        auto & peer_manager = MockPeerManager::return_value;
        peer_manager.get_peer_dims.return_value = std::vector<int>({});
        peer_manager.get_peer_endpoints.side_effect = []
            (Identifier const & port, std::vector<int> const & slot)
        {
            Reference port_slot(port);
            port_slot += slot;

            if (port_slot == "in[13]")
                return std::vector<Endpoint>({Endpoint("other", {}, "out", {13})});
            if (port_slot == "out[13]")
                return std::vector<Endpoint>({Endpoint("other", {}, "in", {13})});
            throw std::runtime_error(
                    "Invalid port/slot " + std::string(port_slot) + " in get_peer_endpoints");
        };

        peer_manager.get_peer_ports.side_effect = [](Identifier const & port) {
            if (port == "out")
                return std::vector<Reference>({"other.in"});
            if (port == "in")
                return std::vector<Reference>({"other.out"});
            throw std::runtime_error(
                    "Invalid port " + port + " in get_peer_ports");
        };

        peer_manager.get_peer_locations.return_value = std::vector<std::string>(
                {std::string("tcp:test")});

        comm->connect(conduits, peer_dims, peer_locations);
        return comm;
    }
};


TEST_F(libmuscle_communicator, create_communicator) {
    Communicator comm(
            Reference("kernel"), {13}, {}, mock_logger_, mock_profiler_);
    ASSERT_EQ(comm.servers_.size(), 1);
    ASSERT_TRUE(comm.clients_.empty());
}

TEST_F(libmuscle_communicator, get_locations) {
    Communicator comm(
            Reference("kernel"), {13}, {}, mock_logger_, mock_profiler_);
    auto server = dynamic_cast<MockTcpTransportServer *>(comm.servers_.back().get());
    server->get_location_mock.return_value = "tcp:test_location";
    ASSERT_EQ(comm.get_locations().size(), 1);
    ASSERT_EQ(comm.get_locations()[0], "tcp:test_location");
}

TEST_F(libmuscle_communicator, test_connect) {
    Communicator comm(
            Reference("kernel"), {13}, {}, mock_logger_, mock_profiler_);

    std::vector<Conduit> conduits({
        Conduit("kernel.out", "other.in"),
        Conduit("other.out", "kernel.in")});
    PeerDims peer_dims({{Reference("other"), {1}}});
    PeerLocations peer_locations({
            {Reference("other"), {"tcp:test"}}});

    MockPeerManager::return_value.get_peer_dims.return_value = std::vector<int>({1});
    MockPeerManager::return_value.is_connected.return_value = true;
    comm.connect(conduits, peer_dims, peer_locations);

    ASSERT_EQ(comm.peer_manager_->get_peer_dims.call_arg<0>(), "other");
    ASSERT_EQ(comm.peer_manager_->constructor.call_arg<0>(), "kernel");
    ASSERT_EQ(comm.peer_manager_->constructor.call_arg<1>(), std::vector<int>({13}));

    // check inferred ports
    auto const & ports = comm.ports_;

    ASSERT_EQ(ports.at("in").name, "in");
    ASSERT_EQ(ports.at("in").oper, Operator::F_INIT);
    ASSERT_FALSE(ports.at("in").is_vector());

    ASSERT_EQ(ports.at("out").name, "out");
    ASSERT_EQ(ports.at("out").oper, Operator::O_F);
    ASSERT_FALSE(ports.at("out").is_vector());
}

TEST_F(libmuscle_communicator, test_connect_vector_ports) {
    PortsDescription desc({
            {Operator::F_INIT, {"in[]"}},
            {Operator::O_F, {"out1", "out2[]"}}
            });

    Communicator comm(
            Reference("kernel"), {13}, desc, mock_logger_, mock_profiler_);

    std::vector<Conduit> conduits({
        Conduit("other1.out", "kernel.in"),
        Conduit("kernel.out1", "other.in"),
        Conduit("kernel.out2", "other3.in")
        });
    PeerDims peer_dims({
            {Reference("other1"), {20, 7}},
            {Reference("other"), {25}},
            {Reference("other3"), {20}}
            });
    PeerLocations peer_locations({
            {Reference("other"), {"tcp:test"}},
            {Reference("other1"), {"tcp:test1"}},
            {Reference("other3"), {"tcp:test3"}}
            });

    MockPeerManager::return_value.get_peer_ports.side_effect = []
        (Identifier const & port)
    {
        if (port == "in")
            return std::vector<Reference>({"other1.out"});
        if (port == "out1")
            return std::vector<Reference>({"other.in"});
        if (port == "out2")
            return std::vector<Reference>({"other3.in"});
        throw std::runtime_error("Unexpected port " + port + " in get_peer_ports");
    };

    MockPeerManager::return_value.get_peer_dims.side_effect = []
        (Reference const & peer_kernel)
    {
        if (peer_kernel == "other1")
            return std::vector<int>({20, 7});
        if (peer_kernel == "other")
            return std::vector<int>({25});
        if (peer_kernel == "other3")
            return std::vector<int>({20});
        throw std::runtime_error("Unexpected kernel in get_peer_dims");
    };

    comm.connect(conduits, peer_dims, peer_locations);

    ASSERT_EQ(comm.peer_manager_->constructor.call_arg<2>(), conduits);
    ASSERT_EQ(comm.peer_manager_->constructor.call_arg<3>(), peer_dims);
    ASSERT_EQ(comm.peer_manager_->constructor.call_arg<4>(), peer_locations);

    auto const & ports = comm.ports_;

    ASSERT_EQ(ports.at("in").name, "in");
    ASSERT_EQ(ports.at("in").oper, Operator::F_INIT);
    ASSERT_TRUE(ports.at("in").is_vector());
    ASSERT_EQ(ports.at("in").get_length(), 7);
    ASSERT_FALSE(ports.at("in").is_resizable());

    ASSERT_EQ(ports.at("out1").name, "out1");
    ASSERT_EQ(ports.at("out1").oper, Operator::O_F);
    ASSERT_FALSE(ports.at("out1").is_vector());

    ASSERT_EQ(ports.at("out2").name, "out2");
    ASSERT_EQ(ports.at("out2").oper, Operator::O_F);
    ASSERT_TRUE(ports.at("out2").is_vector());
    ASSERT_EQ(ports.at("out2").get_length(), 0);
    ASSERT_TRUE(ports.at("out2").is_resizable());
}

TEST_F(libmuscle_communicator, test_connect_multidimensional_ports) {
    PortsDescription desc({
            {Operator::F_INIT, {"in[][]"}}
            });

    Communicator comm(
            Reference("kernel"), {13}, desc, mock_logger_, mock_profiler_);

    std::vector<Conduit> conduits({
        Conduit("other.out", "kernel.in")
        });

    PeerDims peer_dims({
            {Reference("other"), {20, 7, 30}}
            });

    PeerLocations peer_locations({
            {Reference("other"), {"tcp:test"}}
            });

    MockPeerManager::return_value.get_peer_ports.return_value = std::vector<Reference>(
            {"other.out"});
    MockPeerManager::return_value.get_peer_dims.return_value = std::vector<int>({20, 7, 30});

    ASSERT_THROW(
            comm.connect(conduits, peer_dims, peer_locations),
            std::invalid_argument);

    ASSERT_EQ(comm.peer_manager_->constructor.call_arg<2>(), conduits);
    ASSERT_EQ(comm.peer_manager_->constructor.call_arg<3>(), peer_dims);
    ASSERT_EQ(comm.peer_manager_->constructor.call_arg<4>(), peer_locations);
}

TEST_F(libmuscle_communicator, test_connect_inferred_ports) {
    Communicator comm(
            Reference("kernel"), {13}, {}, mock_logger_, mock_profiler_);

    std::vector<Conduit> conduits({
        Conduit("other1.out", "kernel.in"),
        Conduit("kernel.out1", "other.in"),
        Conduit("kernel.out3", "other2.in")
        });

    PeerDims peer_dims({
            {Reference("other1"), {20, 7}},
            {Reference("other"), {25}},
            {Reference("other2"), {}}
            });

    PeerLocations peer_locations({
            {Reference("other"), {"tcp:test"}},
            {Reference("other1"), {"tcp:test1"}},
            {Reference("other2"), {"tcp:test2"}}
            });

    MockPeerManager::return_value.get_peer_ports.side_effect = []
        (Identifier const & port)
    {
        if (port == "in")
            return std::vector<Reference>({"other1.out"});
        if (port == "out1")
            return std::vector<Reference>({"other.in"});
        if (port == "out3")
            return std::vector<Reference>({"other2.in"});
        throw std::runtime_error("Unexpected port in get_peer_ports");
    };

    MockPeerManager::return_value.get_peer_dims.side_effect = []
        (Reference const & peer_kernel)
    {
        if (peer_kernel == "other1")
            return std::vector<int>({20, 7});
        if (peer_kernel == "other")
            return std::vector<int>({25});
        if (peer_kernel == "other2")
            return std::vector<int>();
        throw std::runtime_error("Unexpected kernel in get_peer_dims");
    };

    comm.connect(conduits, peer_dims, peer_locations);

    ASSERT_EQ(comm.peer_manager_->constructor.call_arg<2>(), conduits);
    ASSERT_EQ(comm.peer_manager_->constructor.call_arg<3>(), peer_dims);
    ASSERT_EQ(comm.peer_manager_->constructor.call_arg<4>(), peer_locations);

    auto const & ports = comm.ports_;

    ASSERT_EQ(ports.at("in").name, "in");
    ASSERT_EQ(ports.at("in").oper, Operator::F_INIT);
    ASSERT_TRUE(ports.at("in").is_vector());
    ASSERT_EQ(ports.at("in").get_length(), 7);
    ASSERT_FALSE(ports.at("in").is_resizable());

    ASSERT_EQ(ports.at("out1").name, "out1");
    ASSERT_EQ(ports.at("out1").oper, Operator::O_F);
    ASSERT_FALSE(ports.at("out1").is_vector());

    ASSERT_EQ(ports.at("out3").name, "out3");
    ASSERT_EQ(ports.at("out3").oper, Operator::O_F);
    ASSERT_FALSE(ports.at("out3").is_vector());
}

TEST_F(libmuscle_communicator, send_message) {
    auto comm = connected_communicator();

    Message message(0.0, "test", Settings());
    comm->send_message("out", message);

    ASSERT_EQ(comm->post_office_.deposit.call_arg<0>(), "other.in[13]");
    auto const & sent_msg = comm->post_office_.deposit.call_arg<1>();
    ASSERT_EQ(sent_msg->sender, "kernel[13].out");
    ASSERT_EQ(sent_msg->receiver, "other.in[13]");
    ASSERT_EQ(sent_msg->timestamp, 0.0);
    ASSERT_FALSE(sent_msg->next_timestamp.is_set());
    ASSERT_EQ(sent_msg->data.as<std::string>(), "test");
    ASSERT_TRUE(sent_msg->settings_overlay.is_a<Settings>());
}

TEST_F(libmuscle_communicator, send_on_disconnected_port) {
    auto comm = connected_communicator();

    comm->peer_manager_->is_connected.return_value = false;

    Message message(0.0, "test", Settings());
    comm->send_message("not_connected", message);
}

TEST_F(libmuscle_communicator, send_on_invalid_port) {
    auto comm = connected_communicator();
    Message message(0.0, "test", Settings());
    ASSERT_THROW(comm->send_message("[$Invalid_id", message), std::invalid_argument);
}

TEST_F(libmuscle_communicator, send_msgpack) {
    auto comm = connected_communicator();

    Message message(0.0, Data::dict("test", 17), Settings());
    comm->send_message("out", message);

    ASSERT_EQ(comm->post_office_.deposit.call_arg<0>(), "other.in[13]");
    auto const & sent_msg = comm->post_office_.deposit.call_arg<1>();
    ASSERT_EQ(sent_msg->sender, "kernel[13].out");
    ASSERT_EQ(sent_msg->receiver, "other.in[13]");
    ASSERT_EQ(sent_msg->timestamp, 0.0);
    ASSERT_FALSE(sent_msg->next_timestamp.is_set());
    ASSERT_EQ(sent_msg->data["test"].as<int>(), 17);
    ASSERT_TRUE(sent_msg->settings_overlay.is_a<Settings>());
}

TEST_F(libmuscle_communicator, send_message_with_slot) {
    auto comm = connected_communicator2();

    Message message(0.0, "test", Settings());
    comm->send_message("out", message, 13);

    ASSERT_EQ(comm->post_office_.deposit.call_arg<0>(), "kernel[13].in");
    auto const & sent_msg = comm->post_office_.deposit.call_arg<1>();
    ASSERT_EQ(sent_msg->sender, "other.out[13]");
    ASSERT_EQ(sent_msg->receiver, "kernel[13].in");
    ASSERT_EQ(sent_msg->timestamp, 0.0);
    ASSERT_FALSE(sent_msg->next_timestamp.is_set());
    ASSERT_EQ(sent_msg->data.as<std::string>(), "test");
    ASSERT_TRUE(sent_msg->settings_overlay.is_a<Settings>());
}

TEST_F(libmuscle_communicator, send_message_resizable) {
    auto comm = connected_communicator3();
    Message message(0.0, "test", Settings());

    ASSERT_THROW(comm->send_message("out", message, 13), std::runtime_error);

    comm->get_port("out").set_length(20);
    comm->send_message("out", message, 13);

    ASSERT_EQ(comm->post_office_.deposit.call_arg<0>(), "other.in[13]");
    auto const & sent_msg = comm->post_office_.deposit.call_arg<1>();
    ASSERT_EQ(sent_msg->sender, "kernel.out[13]");
    ASSERT_EQ(sent_msg->receiver, "other.in[13]");
    ASSERT_EQ(sent_msg->port_length.get(), 20);
    ASSERT_EQ(sent_msg->timestamp, 0.0);
    ASSERT_FALSE(sent_msg->next_timestamp.is_set());
    ASSERT_EQ(sent_msg->data.as<std::string>(), "test");
    ASSERT_TRUE(sent_msg->settings_overlay.is_a<Settings>());
}

TEST_F(libmuscle_communicator, send_with_settings) {
    auto comm = connected_communicator();

    Settings settings;
    settings["test2"] = "testing";
    Message message(0.0, "test", settings);
    comm->send_message("out", message);

    ASSERT_EQ(comm->post_office_.deposit.call_arg<0>(), "other.in[13]");
    auto const & sent_msg = comm->post_office_.deposit.call_arg<1>();
    ASSERT_EQ(sent_msg->sender, "kernel[13].out");
    ASSERT_EQ(sent_msg->receiver, "other.in[13]");
    ASSERT_EQ(sent_msg->timestamp, 0.0);
    ASSERT_FALSE(sent_msg->next_timestamp.is_set());
    ASSERT_EQ(sent_msg->data.as<std::string>(), "test");
    ASSERT_TRUE(sent_msg->settings_overlay.is_a<Settings>());
    ASSERT_EQ(sent_msg->settings_overlay.as<Settings>()["test2"], "testing");
}

TEST_F(libmuscle_communicator, send_settings) {
    auto comm = connected_communicator();

    Settings settings;
    settings["test1"] = "testing";
    Message message(0.0, settings, Settings());
    comm->send_message("out", message);

    ASSERT_EQ(comm->post_office_.deposit.call_arg<0>(), "other.in[13]");
    auto const & sent_msg = comm->post_office_.deposit.call_arg<1>();
    ASSERT_EQ(sent_msg->sender, "kernel[13].out");
    ASSERT_EQ(sent_msg->receiver, "other.in[13]");
    ASSERT_EQ(sent_msg->timestamp, 0.0);
    ASSERT_FALSE(sent_msg->next_timestamp.is_set());
    ASSERT_TRUE(sent_msg->data.is_a<Settings>());
    ASSERT_EQ(sent_msg->data.as<Settings>()["test1"], "testing");
    ASSERT_TRUE(sent_msg->settings_overlay.is_a<Settings>());
}

TEST_F(libmuscle_communicator, close_port) {
    auto comm = connected_communicator();

    comm->close_port("out");

    ASSERT_EQ(comm->post_office_.deposit.call_arg<0>(), "other.in[13]");
    auto const & sent_msg = comm->post_office_.deposit.call_arg<1>();
    ASSERT_EQ(sent_msg->sender, "kernel[13].out");
    ASSERT_EQ(sent_msg->receiver, "other.in[13]");
    ASSERT_EQ(sent_msg->timestamp, std::numeric_limits<double>::infinity());
    ASSERT_FALSE(sent_msg->next_timestamp.is_set());
    ASSERT_TRUE(::libmuscle::_MUSCLE_IMPL_NS::is_close_port(sent_msg->data));
}

TEST_F(libmuscle_communicator, receive_message) {
    next_received_message.sender = "other.out[13]";
    next_received_message.receiver = "kernel[13].in";

    auto comm = connected_communicator();
    Message msg = comm->receive_message("in");

    ASSERT_EQ(comm->clients_.at("other")->receive.call_arg<0>(), "kernel[13].in");
    ASSERT_TRUE(msg.data().is_a_dict());
    ASSERT_EQ(msg.data()["test1"].as<int>(), 12);
}

TEST_F(libmuscle_communicator, receive_message_default) {
    MockPeerManager::return_value.is_connected.return_value = false;

    Message default_msg(3.0, 4.0, "test");
    auto comm = connected_communicator();
    Message msg = comm->receive_message("not_connected", {}, default_msg);

    ASSERT_EQ(msg.timestamp(), 3.0);
    ASSERT_EQ(msg.next_timestamp(), 4.0);
    ASSERT_EQ(msg.data().as<std::string>(), "test");
    ASSERT_FALSE(msg.has_settings());
}

TEST_F(libmuscle_communicator, receive_message_no_default) {
    MockPeerManager::return_value.is_connected.return_value = false;

    auto comm = connected_communicator();
    ASSERT_THROW(comm->receive_message("not_connected"), std::runtime_error);
}

TEST_F(libmuscle_communicator, receive_on_invalid_port) {
    auto comm = connected_communicator();
    ASSERT_THROW(comm->receive_message("@$Invalid_id"), std::invalid_argument);
}

TEST_F(libmuscle_communicator, receive_message_with_slot) {
    next_received_message.sender = "kernel[13].out";
    next_received_message.receiver = "other.in[13]";

    auto comm = connected_communicator2();
    Message msg = comm->receive_message("in", 13);

    ASSERT_EQ(comm->clients_.at("kernel[13]")->receive.call_arg<0>(), "other.in[13]");
    ASSERT_TRUE(msg.data().is_a_dict());
    ASSERT_EQ(msg.data()["test1"].as<int>(), 12);
}

TEST_F(libmuscle_communicator, receive_message_resizable) {
    next_received_message.sender = "other.out[13]";
    next_received_message.receiver = "kernel.in[13]";
    next_received_message.port_length = 20;

    auto comm = connected_communicator3();
    Message msg = comm->receive_message("in", 13);

    ASSERT_EQ(comm->clients_.at("other")->receive.call_arg<0>(), "kernel.in[13]");
    ASSERT_TRUE(msg.data().is_a_dict());
    ASSERT_EQ(msg.data()["test1"].as<int>(), 12);
    ASSERT_EQ(comm->get_port("in").get_length(), 20);
}

TEST_F(libmuscle_communicator, receive_with_settings) {
    next_received_message.sender = "other.out[13]";
    next_received_message.receiver = "kernel[13].in";

    auto comm = connected_communicator();
    Message msg = comm->receive_message("in");

    ASSERT_EQ(comm->clients_.at("other")->receive.call_arg<0>(), "kernel[13].in");
    ASSERT_TRUE(msg.data().is_a_dict());
    ASSERT_EQ(msg.data()["test1"].as<int>(), 12);
    ASSERT_EQ(msg.settings().at("test2").as<double>(), 3.1);
}

TEST_F(libmuscle_communicator, receive_message_with_slot_and_settings) {
    next_received_message.sender = "kernel[13].out";
    next_received_message.receiver = "other.in[13]";

    auto comm = connected_communicator2();
    Message msg = comm->receive_message("in", 13);

    ASSERT_EQ(comm->clients_.at("kernel[13]")->receive.call_arg<0>(), "other.in[13]");
    ASSERT_TRUE(msg.data().is_a_dict());
    ASSERT_EQ(msg.data()["test1"].as<int>(), 12);
    ASSERT_EQ(msg.settings().at("test2"), 3.1);
}

TEST_F(libmuscle_communicator, port_message_counts) {
    auto comm = connected_communicator();

    Message message(0.0, "test", Settings());
    comm->send_message("out", message);

    auto msg_counts = comm->get_message_counts();
    ASSERT_EQ(msg_counts.size(), 3);
    ASSERT_EQ(msg_counts["out"], std::vector<int>({1}));
    ASSERT_EQ(msg_counts["in"], std::vector<int>({0}));
    ASSERT_EQ(msg_counts["muscle_settings_in"], std::vector<int>({0}));

    comm->restore_message_counts({
            {"out", {3}},
            {"in", {2}},
            {"muscle_settings_in", {4}}});
    comm->send_message("out", message);
    msg_counts = comm->get_message_counts();
    ASSERT_EQ(msg_counts.size(), 3);
    ASSERT_EQ(msg_counts["out"], std::vector<int>({4}));
    ASSERT_EQ(msg_counts["in"], std::vector<int>({2}));
    ASSERT_EQ(msg_counts["muscle_settings_in"], std::vector<int>({4}));

    ASSERT_THROW(
            comm->restore_message_counts({{"x?invalid_port", {3}}}),
            std::runtime_error);
}

TEST_F(libmuscle_communicator, vector_port_message_counts) {
    auto comm = connected_communicator2();

    auto msg_counts = comm->get_message_counts();
    ASSERT_EQ(msg_counts.size(), 3);
    std::vector<int> expected_counts(20);  // 20 zeros
    ASSERT_EQ(msg_counts["out"], expected_counts);
    ASSERT_EQ(msg_counts["in"], expected_counts);
    ASSERT_EQ(msg_counts["muscle_settings_in"], std::vector<int>({0}));

    Message message(0.0, "test", Settings());
    comm->send_message("out", message, 13);
    msg_counts = comm->get_message_counts();
    ASSERT_EQ(msg_counts.size(), 3);
    ASSERT_EQ(msg_counts["in"], expected_counts);
    ASSERT_EQ(msg_counts["muscle_settings_in"], std::vector<int>({0}));
    expected_counts[13] = 1;
    ASSERT_EQ(msg_counts["out"], expected_counts);

    std::iota(expected_counts.begin(), expected_counts.end(), 0);
    // expected_counts = {0, 1, ..., 19}
    comm->restore_message_counts({
            {"out", expected_counts},
            {"in", expected_counts},
            {"muscle_settings_in", {4}}});
    comm->send_message("out", message, 13);
    msg_counts = comm->get_message_counts();
    ASSERT_EQ(msg_counts.size(), 3);
    ASSERT_EQ(msg_counts["in"], expected_counts);
    ASSERT_EQ(msg_counts["muscle_settings_in"], std::vector<int>({4}));
    expected_counts[13] = 14;
    ASSERT_EQ(msg_counts["out"], expected_counts);
}

TEST_F(libmuscle_communicator, port_count_validation) {
    next_received_message.sender = "other.out[13]";
    next_received_message.receiver = "kernel[13].in";

    auto comm = connected_communicator();
    Message msg = comm->receive_message("in");

    ASSERT_EQ(comm->get_message_counts()["in"], std::vector<int>({1}));

    // the message received has message_number = 0 again
    ASSERT_THROW(comm->receive_message("in"), std::runtime_error);
}

TEST_F(libmuscle_communicator, port_discard_error_on_resume) {
    next_received_message.sender = "other.out[13]";
    next_received_message.receiver = "kernel[13].in";
    next_received_message.message_number = 1;

    auto comm = connected_communicator();

    comm->restore_message_counts({
            {"out", {0}},
            {"in", {2}},
            {"muscle_settings_in", {0}}});
    auto & ports = comm->ports_;
    for (auto const & port : ports) {
        ASSERT_TRUE(port.second.is_resuming());
    }

    // In the next block, the first message with message_number=1 is discarded.
    // The RuntimeError is raised when 'receiving' the second message with
    // message_number=1
    ASSERT_THROW(comm->receive_message("in"), std::runtime_error);
    // TODO: test that a debug message was logged?
}

TEST_F(libmuscle_communicator, port_discard_success_on_resume) {
    next_received_message.sender = "other.out[13]";
    next_received_message.receiver = "kernel[13].in";
    next_received_message.message_number = 1;
    next_received_message.timestamp = 1.0;

    auto & ret_val = MockMPPClient::return_value;

    using RecvRet = std::tuple<
        DataConstRef, std::tuple<
            ProfileTimestamp, ProfileTimestamp, ProfileTimestamp>>;

    ret_val.receive.side_effect = [this](Reference const &) -> RecvRet {
        // ensure message_number increases after every receive()
        next_received_message.message_number++;
        next_received_message.timestamp += 1.0;
        return std::make_tuple(
                next_received_message.encoded(), std::make_tuple(
                    ProfileTimestamp(1.0), ProfileTimestamp(2.0),
                    ProfileTimestamp(3.0)));
    };

    auto comm = connected_communicator();

    comm->restore_message_counts({
            {"out", {0}},
            {"in", {2}},
            {"muscle_settings_in", {0}}});
    auto & ports = comm->ports_;
    for (auto const & port : ports) {
        ASSERT_TRUE(port.second.is_resuming());
    }

    auto msg = comm->receive_message("in");
    // TODO: test that a debug message was logged?
    ASSERT_EQ(msg.timestamp(), 2.0);
    ASSERT_EQ(comm->get_message_counts()["in"], std::vector<int>({3}));
}
