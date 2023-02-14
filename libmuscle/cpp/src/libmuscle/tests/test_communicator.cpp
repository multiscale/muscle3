// Inject mocks
#define LIBMUSCLE_MOCK_LOGGER <mocks/mock_logger.hpp>
#define LIBMUSCLE_MOCK_MPP_CLIENT <mocks/mock_mpp_client.hpp>
#define LIBMUSCLE_MOCK_MCP_TCP_TRANSPORT_SERVER <mocks/mcp/mock_tcp_transport_server.hpp>
#define LIBMUSCLE_MOCK_PEER_MANAGER <mocks/mock_peer_manager.hpp>
#define LIBMUSCLE_MOCK_POST_OFFICE <mocks/mock_post_office.hpp>
#define LIBMUSCLE_MOCK_PROFILER <mocks/mock_profiler.hpp>

// into the real implementation,
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

// then add mock implementations as needed.
#include <mocks/mock_logger.cpp>
#include <mocks/mock_peer_manager.cpp>
#include <mocks/mock_post_office.cpp>
#include <mocks/mock_profiler.cpp>
#include <mocks/mock_mpp_client.cpp>
#include <mocks/mcp/mock_tcp_transport_server.cpp>


// Test code dependencies
#include <memory>
#include <stdexcept>
#include <gtest/gtest.h>
#include <libmuscle/communicator.hpp>
#include <mocks/mock_mpp_client.hpp>
#include <mocks/mcp/mock_tcp_transport_server.hpp>
#include <mocks/mock_logger.hpp>
#include <mocks/mock_peer_manager.hpp>
#include <mocks/mock_profiler.hpp>


using libmuscle::impl::Communicator;
using libmuscle::impl::Data;
using libmuscle::impl::Endpoint;
using libmuscle::impl::Optional;
using libmuscle::impl::PeerDims;
using libmuscle::impl::PeerLocations;
using libmuscle::impl::PortsDescription;
using libmuscle::impl::Message;
using libmuscle::impl::MockLogger;
using libmuscle::impl::MockPeerManager;
using libmuscle::impl::MockPostOffice;
using libmuscle::impl::MockProfiler;
using libmuscle::impl::MockMPPClient;
using libmuscle::impl::mcp::MockTcpTransportServer;

using ymmsl::Conduit;
using ymmsl::Reference;


int main(int argc, char *argv[]) {
    ::testing::InitGoogleTest(&argc, argv);
    return RUN_ALL_TESTS();
}


// Helpers for accessing internal state
namespace libmuscle { namespace impl {

struct TestCommunicator {
    static std::unordered_map<std::string, libmuscle::impl::Port> const & ports_(
            Communicator const & comm)
    {
        return comm.ports_;
    }
};

} }

using libmuscle::impl::TestCommunicator;


/* Mocks have internal state, which needs to be reset before each test. This
 * means that the tests are not reentrant, and cannot be run in parallel.
 * It's all fast enough, so that's not a problem.
 */
void reset_mocks() {
    MockPeerManager::reset();
    MockMPPClient::reset();
    MockTcpTransportServer::reset();
}

MockLogger & mock_logger() {
    static MockLogger logger;
    return logger;
}

MockProfiler & mock_profiler() {
    static MockProfiler profiler;
    return profiler;
}

std::unique_ptr<Communicator> connected_communicator() {
    std::unique_ptr<Communicator> comm(new Communicator(
            Reference("kernel"), {13}, {}, mock_logger(), mock_profiler()));

    std::vector<Conduit> conduits({
        Conduit("kernel.out", "other.in"),
        Conduit("other.out", "kernel.in")});

    PeerDims peer_dims({{Reference("other"), {1}}});

    PeerLocations peer_locations({
            {Reference("other"), {"tcp:test"}}});

    MockPeerManager::get_peer_dims_table.emplace("other", std::vector<int>({1}));
    MockPeerManager::get_peer_endpoint_table.emplace("out",
            std::vector<Endpoint>({Endpoint("other", {}, "in", {13})}));
    MockPeerManager::get_peer_endpoint_table.emplace("in",
            std::vector<Endpoint>({Endpoint("other", {}, "out", {13})}));

    comm->connect(conduits, peer_dims, peer_locations);
    return std::move(comm);
}

std::unique_ptr<Communicator> connected_communicator2() {
    std::unique_ptr<Communicator> comm(new Communicator(
            Reference("other"), {}, {}, mock_logger(), mock_profiler()));

    std::vector<Conduit> conduits({
        Conduit("kernel.out", "other.in"),
        Conduit("other.out", "kernel.in")});

    PeerDims peer_dims({{Reference("kernel"), {20}}});

    PeerLocations peer_locations({
            {Reference("kernel"), {"tcp:test"}}});

    MockPeerManager::get_peer_dims_table.emplace("kernel", std::vector<int>({20}));
    MockPeerManager::get_peer_endpoint_table.emplace("in[13]",
            std::vector<Endpoint>({Endpoint("kernel", {13}, "out", {})}));
    MockPeerManager::get_peer_endpoint_table.emplace("out[13]",
            std::vector<Endpoint>({Endpoint("kernel", {13}, "in", {})}));

    comm->connect(conduits, peer_dims, peer_locations);
    return std::move(comm);
}

std::unique_ptr<Communicator> connected_communicator3() {
    PortsDescription desc({
            {Operator::O_I, {"out[]"}},
            {Operator::S, {"in[]"}}
            });

    std::unique_ptr<Communicator> comm(new Communicator(
            Reference("kernel"), {}, desc, mock_logger(), mock_profiler()));

    std::vector<Conduit> conduits({
        Conduit("kernel.out", "other.in"),
        Conduit("other.out", "kernel.in")});

    PeerDims peer_dims({{Reference("other"), {}}});

    PeerLocations peer_locations({
            {Reference("other"), {"tcp:test"}}});

    MockPeerManager::get_peer_dims_table.emplace("other", std::vector<int>({}));
    MockPeerManager::get_peer_endpoint_table.emplace("out[13]",
            std::vector<Endpoint>({Endpoint("other", {}, "in", {13})}));
    MockPeerManager::get_peer_endpoint_table.emplace("in[13]",
            std::vector<Endpoint>({Endpoint("other", {}, "out", {13})}));
    MockPeerManager::get_peer_port_table.emplace("out",
            std::vector<Reference>({"other.in"}));
    MockPeerManager::get_peer_port_table.emplace("in",
            std::vector<Reference>({"other.out"}));

    comm->connect(conduits, peer_dims, peer_locations);
    return std::move(comm);
}


TEST(libmuscle_communicator, create_communicator) {
    reset_mocks();
    Communicator comm(
            Reference("kernel"), {13}, {}, mock_logger(), mock_profiler());
    ASSERT_EQ(MockTcpTransportServer::num_constructed, 1);
    ASSERT_EQ(MockMPPClient::num_constructed, 0);
}

TEST(libmuscle_communicator, get_locations) {
    reset_mocks();
    Communicator comm(
            Reference("kernel"), {13}, {}, mock_logger(), mock_profiler());
    ASSERT_EQ(comm.get_locations().size(), 1);
    ASSERT_EQ(comm.get_locations()[0], "tcp:test_location");
}

TEST(libmuscle_communicator, test_connect) {
    reset_mocks();
    Communicator comm(
            Reference("kernel"), {13}, {}, mock_logger(), mock_profiler());

    std::vector<Conduit> conduits({
        Conduit("kernel.out", "other.in"),
        Conduit("other.out", "kernel.in")});
    PeerDims peer_dims({{Reference("other"), {1}}});
    PeerLocations peer_locations({
            {Reference("other"), {"tcp:test"}}});

    MockPeerManager::get_peer_dims_table.emplace("other", std::vector<int>({1}));
    comm.connect(conduits, peer_dims, peer_locations);

    ASSERT_EQ(MockPeerManager::last_constructed_kernel_id, "kernel");
    ASSERT_EQ(MockPeerManager::last_constructed_index, std::vector<int>({13}));

    // check inferred ports
    auto const & ports = TestCommunicator::ports_(comm);

    ASSERT_EQ(ports.at("in").name, "in");
    ASSERT_EQ(ports.at("in").oper, Operator::F_INIT);
    ASSERT_FALSE(ports.at("in").is_vector());

    ASSERT_EQ(ports.at("out").name, "out");
    ASSERT_EQ(ports.at("out").oper, Operator::O_F);
    ASSERT_FALSE(ports.at("out").is_vector());
}

TEST(libmuscle_communicator, test_connect_vector_ports) {
    reset_mocks();

    PortsDescription desc({
            {Operator::F_INIT, {"in[]"}},
            {Operator::O_F, {"out1", "out2[]"}}
            });

    Communicator comm(
            Reference("kernel"), {13}, desc, mock_logger(), mock_profiler());

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

    MockPeerManager::get_peer_port_table.emplace("in",
            std::vector<Reference>({"other1.out"}));
    MockPeerManager::get_peer_port_table.emplace("out1",
            std::vector<Reference>({"other.in"}));
    MockPeerManager::get_peer_port_table.emplace("out2",
            std::vector<Reference>({"other3.in"}));

    MockPeerManager::get_peer_dims_table.emplace("other1", std::vector<int>({20, 7}));
    MockPeerManager::get_peer_dims_table.emplace("other", std::vector<int>({25}));
    MockPeerManager::get_peer_dims_table.emplace("other3", std::vector<int>({20}));

    comm.connect(conduits, peer_dims, peer_locations);

    ASSERT_EQ(MockPeerManager::last_constructed_conduits, conduits);
    ASSERT_EQ(MockPeerManager::last_constructed_peer_dims, peer_dims);
    ASSERT_EQ(MockPeerManager::last_constructed_peer_locations, peer_locations);

    auto const & ports = TestCommunicator::ports_(comm);

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

TEST(libmuscle_communicator, test_connect_multidimensional_ports) {
    reset_mocks();

    PortsDescription desc({
            {Operator::F_INIT, {"in[][]"}}
            });

    Communicator comm(
            Reference("kernel"), {13}, desc, mock_logger(), mock_profiler());

    std::vector<Conduit> conduits({
        Conduit("other.out", "kernel.in")
        });

    PeerDims peer_dims({
            {Reference("other"), {20, 7, 30}}
            });

    PeerLocations peer_locations({
            {Reference("other"), {"tcp:test"}}
            });

    MockPeerManager::get_peer_port_table.emplace("in",
            std::vector<Reference>({"other.out"}));
    MockPeerManager::get_peer_dims_table.emplace("other", std::vector<int>({20, 7, 30}));

    ASSERT_THROW(
            comm.connect(conduits, peer_dims, peer_locations),
            std::invalid_argument);

    ASSERT_EQ(MockPeerManager::last_constructed_conduits, conduits);
    ASSERT_EQ(MockPeerManager::last_constructed_peer_dims, peer_dims);
    ASSERT_EQ(MockPeerManager::last_constructed_peer_locations, peer_locations);
}

TEST(libmuscle_communicator, test_connect_inferred_ports) {
    reset_mocks();

    Communicator comm(
            Reference("kernel"), {13}, {}, mock_logger(), mock_profiler());

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

    MockPeerManager::get_peer_port_table.emplace("in",
            std::vector<Reference>({"other1.out"}));
    MockPeerManager::get_peer_port_table.emplace("out1",
            std::vector<Reference>({"other.in"}));
    MockPeerManager::get_peer_port_table.emplace("out3",
            std::vector<Reference>({"other2.in"}));

    MockPeerManager::get_peer_dims_table.emplace("other1", std::vector<int>({20, 7}));
    MockPeerManager::get_peer_dims_table.emplace("other", std::vector<int>({25}));
    MockPeerManager::get_peer_dims_table.emplace("other2", std::vector<int>());

    comm.connect(conduits, peer_dims, peer_locations);

    ASSERT_EQ(MockPeerManager::last_constructed_conduits, conduits);
    ASSERT_EQ(MockPeerManager::last_constructed_peer_dims, peer_dims);
    ASSERT_EQ(MockPeerManager::last_constructed_peer_locations, peer_locations);

    auto const & ports = TestCommunicator::ports_(comm);

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

TEST(libmuscle_communicator, send_message) {
    reset_mocks();
    auto comm = connected_communicator();

    Message message(0.0, "test", Settings());
    comm->send_message("out", message);

    ASSERT_EQ(MockPostOffice::last_receiver, "other.in[13]");
    ASSERT_EQ(MockPostOffice::last_message->sender, "kernel[13].out");
    ASSERT_EQ(MockPostOffice::last_message->receiver, "other.in[13]");
    ASSERT_EQ(MockPostOffice::last_message->timestamp, 0.0);
    ASSERT_FALSE(MockPostOffice::last_message->next_timestamp.is_set());
    ASSERT_EQ(MockPostOffice::last_message->data.as<std::string>(), "test");
    ASSERT_TRUE(MockPostOffice::last_message->settings_overlay.is_a<Settings>());
}

TEST(libmuscle_communicator, send_on_disconnected_port) {
    reset_mocks();

    auto comm = connected_communicator();

    MockPeerManager::is_connected_return_value = false;

    Message message(0.0, "test", Settings());
    comm->send_message("not_connected", message);
}

TEST(libmuscle_communicator, send_on_invalid_port) {
    reset_mocks();

    auto comm = connected_communicator();
    Message message(0.0, "test", Settings());
    ASSERT_THROW(comm->send_message("[$Invalid_id", message), std::invalid_argument);
}

TEST(libmuscle_communicator, send_msgpack) {
    reset_mocks();
    auto comm = connected_communicator();

    Message message(0.0, Data::dict("test", 17), Settings());
    comm->send_message("out", message);

    ASSERT_EQ(MockPostOffice::last_receiver, "other.in[13]");
    ASSERT_EQ(MockPostOffice::last_message->sender, "kernel[13].out");
    ASSERT_EQ(MockPostOffice::last_message->receiver, "other.in[13]");
    ASSERT_EQ(MockPostOffice::last_message->timestamp, 0.0);
    ASSERT_FALSE(MockPostOffice::last_message->next_timestamp.is_set());
    ASSERT_EQ(MockPostOffice::last_message->data["test"].as<int>(), 17);
    ASSERT_TRUE(MockPostOffice::last_message->settings_overlay.is_a<Settings>());
}

TEST(libmuscle_communicator, send_message_with_slot) {
    reset_mocks();
    auto comm = connected_communicator2();

    Message message(0.0, "test", Settings());
    comm->send_message("out", message, 13);

    ASSERT_EQ(MockPostOffice::last_receiver, "kernel[13].in");
    ASSERT_EQ(MockPostOffice::last_message->sender, "other.out[13]");
    ASSERT_EQ(MockPostOffice::last_message->receiver, "kernel[13].in");
    ASSERT_EQ(MockPostOffice::last_message->timestamp, 0.0);
    ASSERT_FALSE(MockPostOffice::last_message->next_timestamp.is_set());
    ASSERT_EQ(MockPostOffice::last_message->data.as<std::string>(), "test");
    ASSERT_TRUE(MockPostOffice::last_message->settings_overlay.is_a<Settings>());
}

TEST(libmuscle_communicator, send_message_resizable) {
    reset_mocks();
    auto comm = connected_communicator3();
    Message message(0.0, "test", Settings());

    ASSERT_THROW(comm->send_message("out", message, 13), std::runtime_error);

    comm->get_port("out").set_length(20);
    comm->send_message("out", message, 13);

    ASSERT_EQ(MockPostOffice::last_receiver, "other.in[13]");
    ASSERT_EQ(MockPostOffice::last_message->sender, "kernel.out[13]");
    ASSERT_EQ(MockPostOffice::last_message->receiver, "other.in[13]");
    ASSERT_EQ(MockPostOffice::last_message->port_length.get(), 20);
    ASSERT_EQ(MockPostOffice::last_message->timestamp, 0.0);
    ASSERT_FALSE(MockPostOffice::last_message->next_timestamp.is_set());
    ASSERT_EQ(MockPostOffice::last_message->data.as<std::string>(), "test");
    ASSERT_TRUE(MockPostOffice::last_message->settings_overlay.is_a<Settings>());
}

TEST(libmuscle_communicator, send_with_settings) {
    reset_mocks();
    auto comm = connected_communicator();

    Settings settings;
    settings["test2"] = "testing";
    Message message(0.0, "test", settings);
    comm->send_message("out", message);

    ASSERT_EQ(MockPostOffice::last_receiver, "other.in[13]");
    ASSERT_EQ(MockPostOffice::last_message->sender, "kernel[13].out");
    ASSERT_EQ(MockPostOffice::last_message->receiver, "other.in[13]");
    ASSERT_EQ(MockPostOffice::last_message->timestamp, 0.0);
    ASSERT_FALSE(MockPostOffice::last_message->next_timestamp.is_set());
    ASSERT_EQ(MockPostOffice::last_message->data.as<std::string>(), "test");
    ASSERT_TRUE(MockPostOffice::last_message->settings_overlay.is_a<Settings>());
    ASSERT_EQ(MockPostOffice::last_message->settings_overlay.as<Settings>()["test2"], "testing");
}

TEST(libmuscle_communicator, send_settings) {
    reset_mocks();
    auto comm = connected_communicator();

    Settings settings;
    settings["test1"] = "testing";
    Message message(0.0, settings, Settings());
    comm->send_message("out", message);

    ASSERT_EQ(MockPostOffice::last_receiver, "other.in[13]");
    ASSERT_EQ(MockPostOffice::last_message->sender, "kernel[13].out");
    ASSERT_EQ(MockPostOffice::last_message->receiver, "other.in[13]");
    ASSERT_EQ(MockPostOffice::last_message->timestamp, 0.0);
    ASSERT_FALSE(MockPostOffice::last_message->next_timestamp.is_set());
    ASSERT_TRUE(MockPostOffice::last_message->data.is_a<Settings>());
    ASSERT_EQ(MockPostOffice::last_message->data.as<Settings>()["test1"], "testing");
    ASSERT_TRUE(MockPostOffice::last_message->settings_overlay.is_a<Settings>());
}

TEST(libmuscle_communicator, close_port) {
    reset_mocks();
    auto comm = connected_communicator();

    comm->close_port("out");

    ASSERT_EQ(MockPostOffice::last_receiver, "other.in[13]");
    ASSERT_EQ(MockPostOffice::last_message->sender, "kernel[13].out");
    ASSERT_EQ(MockPostOffice::last_message->receiver, "other.in[13]");
    ASSERT_EQ(
            MockPostOffice::last_message->timestamp,
            std::numeric_limits<double>::infinity());
    ASSERT_FALSE(MockPostOffice::last_message->next_timestamp.is_set());
    ASSERT_TRUE(libmuscle::impl::is_close_port(MockPostOffice::last_message->data));
}

TEST(libmuscle_communicator, receive_message) {
    reset_mocks();
    MockMPPClient::next_receive_message.sender = "other.out[13]";
    MockMPPClient::next_receive_message.receiver = "kernel[13].in";

    auto comm = connected_communicator();
    Message msg = comm->receive_message("in");

    ASSERT_EQ(MockMPPClient::last_receiver, "kernel[13].in");
    ASSERT_TRUE(msg.data().is_a_dict());
    ASSERT_EQ(msg.data()["test1"].as<int>(), 12);
}

TEST(libmuscle_communicator, receive_message_default) {
    reset_mocks();
    MockPeerManager::is_connected_return_value = false;

    Message default_msg(3.0, 4.0, "test");
    auto comm = connected_communicator();
    Message msg = comm->receive_message("not_connected", {}, default_msg);

    ASSERT_EQ(msg.timestamp(), 3.0);
    ASSERT_EQ(msg.next_timestamp(), 4.0);
    ASSERT_EQ(msg.data().as<std::string>(), "test");
    ASSERT_FALSE(msg.has_settings());
}

TEST(libmuscle_communicator, receive_message_no_default) {
    reset_mocks();
    MockPeerManager::is_connected_return_value = false;

    auto comm = connected_communicator();
    ASSERT_THROW(comm->receive_message("not_connected"), std::runtime_error);
}

TEST(libmuscle_communicator, receive_on_invalid_port) {
    reset_mocks();

    auto comm = connected_communicator();
    ASSERT_THROW(comm->receive_message("@$Invalid_id"), std::invalid_argument);
}

TEST(libmuscle_communicator, receive_message_with_slot) {
    reset_mocks();
    MockMPPClient::next_receive_message.sender = "kernel[13].out";
    MockMPPClient::next_receive_message.receiver = "other.in[13]";

    auto comm = connected_communicator2();
    Message msg = comm->receive_message("in", 13);

    ASSERT_EQ(MockMPPClient::last_receiver, "other.in[13]");
    ASSERT_TRUE(msg.data().is_a_dict());
    ASSERT_EQ(msg.data()["test1"].as<int>(), 12);
}

TEST(libmuscle_communicator, receive_message_resizable) {
    reset_mocks();
    MockMPPClient::next_receive_message.sender = "other.out[13]";
    MockMPPClient::next_receive_message.receiver = "kernel.in[13]";
    MockMPPClient::next_receive_message.port_length = 20;

    auto comm = connected_communicator3();
    Message msg = comm->receive_message("in", 13);

    ASSERT_EQ(MockMPPClient::last_receiver, "kernel.in[13]");
    ASSERT_TRUE(msg.data().is_a_dict());
    ASSERT_EQ(msg.data()["test1"].as<int>(), 12);
    ASSERT_EQ(comm->get_port("in").get_length(), 20);
}

TEST(libmuscle_communicator, receive_with_settings) {
    reset_mocks();
    MockMPPClient::next_receive_message.sender = "other.out[13]";
    MockMPPClient::next_receive_message.receiver = "kernel[13].in";

    auto comm = connected_communicator();
    Message msg = comm->receive_message("in");

    ASSERT_EQ(MockMPPClient::last_receiver, "kernel[13].in");
    ASSERT_TRUE(msg.data().is_a_dict());
    ASSERT_EQ(msg.data()["test1"].as<int>(), 12);
    ASSERT_EQ(msg.settings().at("test2"), 3.1);
}

TEST(libmuscle_communicator, receive_message_with_slot_and_settings) {
    reset_mocks();
    MockMPPClient::next_receive_message.sender = "kernel[13].out";
    MockMPPClient::next_receive_message.receiver = "other.in[13]";

    auto comm = connected_communicator2();
    Message msg = comm->receive_message("in", 13);

    ASSERT_EQ(MockMPPClient::last_receiver, "other.in[13]");
    ASSERT_TRUE(msg.data().is_a_dict());
    ASSERT_EQ(msg.data()["test1"].as<int>(), 12);
    ASSERT_EQ(msg.settings().at("test2"), 3.1);
}

TEST(libmuscle_communicator, port_message_counts) {
    reset_mocks();
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

TEST(libmuscle_communicator, vector_port_message_counts) {
    reset_mocks();
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

    int i = 0;
    for (int& count : expected_counts)
        count = i++;
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

TEST(libmuscle_communicator, port_count_validation) {
    reset_mocks();
    MockMPPClient::next_receive_message.sender = "other.out[13]";
    MockMPPClient::next_receive_message.receiver = "kernel[13].in";

    auto comm = connected_communicator();
    Message msg = comm->receive_message("in");

    ASSERT_EQ(comm->get_message_counts()["in"], std::vector<int>({1}));

    // the message received has message_number = 0 again
    ASSERT_THROW(comm->receive_message("in"), std::runtime_error);
}

TEST(libmuscle_communicator, port_discard_error_on_resume) {
    reset_mocks();
    MockMPPClient::next_receive_message.sender = "other.out[13]";
    MockMPPClient::next_receive_message.receiver = "kernel[13].in";
    MockMPPClient::next_receive_message.message_number = 1;

    auto comm = connected_communicator();

    comm->restore_message_counts({
            {"out", {0}},
            {"in", {2}},
            {"muscle_settings_in", {0}}});
    auto & ports = TestCommunicator::ports_(*comm);
    for (auto const & port : ports) {
        ASSERT_TRUE(port.second.is_resuming());
    }

    // In the next block, the first message with message_number=1 is discarded.
    // The RuntimeError is raised when 'receiving' the second message with
    // message_number=1
    ASSERT_THROW(comm->receive_message("in"), std::runtime_error);
    // TODO: test that a debug message was logged?
}

TEST(libmuscle_communicator, port_discard_success_on_resume) {
    reset_mocks();
    MockMPPClient::next_receive_message.sender = "other.out[13]";
    MockMPPClient::next_receive_message.receiver = "kernel[13].in";
    MockMPPClient::next_receive_message.message_number = 1;
    MockMPPClient::next_receive_message.timestamp = 1.0;
    MockMPPClient::side_effect = [](){
        // ensure message_number increases after every receive()
        MockMPPClient::next_receive_message.message_number ++;
        MockMPPClient::next_receive_message.timestamp += 1.0;
    };

    auto comm = connected_communicator();

    comm->restore_message_counts({
            {"out", {0}},
            {"in", {2}},
            {"muscle_settings_in", {0}}});
    auto & ports = TestCommunicator::ports_(*comm);
    for (auto const & port : ports) {
        ASSERT_TRUE(port.second.is_resuming());
    }

    auto msg = comm->receive_message("in");
    // TODO: test that a debug message was logged?
    ASSERT_EQ(msg.timestamp(), 2.0);
    ASSERT_EQ(comm->get_message_counts()["in"], std::vector<int>({3}));
}
