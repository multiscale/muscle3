// Inject mocks
#define LIBMUSCLE_MOCK_MCP_TCP_CLIENT <mocks/mcp/mock_tcp_client.hpp>
#define LIBMUSCLE_MOCK_MCP_TCP_SERVER <mocks/mcp/mock_tcp_server.hpp>
#define LIBMUSCLE_MOCK_PEER_MANAGER <mocks/mock_peer_manager.hpp>
#define LIBMUSCLE_MOCK_POST_OFFICE <mocks/mock_post_office.hpp>

// into the real implementation,
#include <ymmsl/compute_element.cpp>
#include <ymmsl/identity.cpp>
#include <ymmsl/model.cpp>
#include <ymmsl/settings.cpp>

#include <libmuscle/communicator.cpp>
#include <libmuscle/data.cpp>
#include <libmuscle/endpoint.cpp>
#include <libmuscle/operator.cpp>
#include <libmuscle/mcp/data_pack.cpp>
#include <libmuscle/mcp/message.cpp>
#include <libmuscle/mcp/client.cpp>
#include <libmuscle/mcp/server.cpp>
#include <libmuscle/port.cpp>

// then add mock implementations as needed.
#include <mocks/mock_peer_manager.cpp>
#include <mocks/mock_post_office.cpp>
#include <mocks/mcp/mock_tcp_client.cpp>
#include <mocks/mcp/mock_tcp_server.cpp>


// Test code dependencies
#include <memory>
#include <stdexcept>
#include <gtest/gtest.h>
#include <libmuscle/communicator.hpp>
#include <mocks/mcp/mock_tcp_client.hpp>
#include <mocks/mcp/mock_tcp_server.hpp>
#include <mocks/mock_peer_manager.hpp>

using libmuscle::Communicator;
using libmuscle::Data;
using libmuscle::Endpoint;
using libmuscle::Optional;
using libmuscle::PeerDims;
using libmuscle::PeerLocations;
using libmuscle::MockPeerManager;
using libmuscle::MockPostOffice;
using libmuscle::Port;
using libmuscle::PortsDescription;
using libmuscle::Message;
using libmuscle::mcp::MockTcpClient;
using libmuscle::mcp::MockTcpServer;

using ymmsl::Conduit;
using ymmsl::Reference;


int main(int argc, char *argv[]) {
    ::testing::InitGoogleTest(&argc, argv);
    return RUN_ALL_TESTS();
}


// Helpers for accessing internal state
namespace libmuscle {

struct TestCommunicator {
    static std::unordered_map<std::string, Port> const & ports_(
            Communicator const & comm)
    {
        return comm.ports_;
    }
};

}

/* Mocks have internal state, which needs to be reset before each test. This
 * means that the tests are not reentrant, and cannot be run in parallel.
 * It's all fast enough, so that's not a problem.
 */
void reset_mocks() {
    MockPeerManager::reset();
    MockTcpClient::reset();
    MockTcpServer::reset();
}

std::unique_ptr<Communicator> connected_communicator() {
    std::unique_ptr<Communicator> comm(new Communicator(
            Reference("kernel"), {13}, {}, 0));

    std::vector<Conduit> conduits({
        Conduit("kernel.out", "other.in"),
        Conduit("other.out", "kernel.in")});

    PeerDims peer_dims({{Reference("other"), {1}}});

    PeerLocations peer_locations({
            {Reference("other"), {"tcp:test"}}});

    MockPeerManager::get_peer_dims_table.emplace("other", std::vector<int>({1}));
    MockPeerManager::get_peer_endpoint_table.emplace("out", Endpoint("other", {}, "in", {13}));
    MockPeerManager::get_peer_endpoint_table.emplace("in", Endpoint("other", {}, "out", {13}));

    comm->connect(conduits, peer_dims, peer_locations);
    return std::move(comm);
}

std::unique_ptr<Communicator> connected_communicator2() {
    std::unique_ptr<Communicator> comm(new Communicator(
            Reference("other"), {}, {}, 0));

    std::vector<Conduit> conduits({
        Conduit("kernel.out", "other.in"),
        Conduit("other.out", "kernel.in")});

    PeerDims peer_dims({{Reference("kernel"), {20}}});

    PeerLocations peer_locations({
            {Reference("kernel"), {"tcp:test"}}});

    MockPeerManager::get_peer_dims_table.emplace("kernel", std::vector<int>({20}));
    MockPeerManager::get_peer_endpoint_table.emplace("in[13]", Endpoint("kernel", {13}, "out", {}));
    MockPeerManager::get_peer_endpoint_table.emplace("out[13]", Endpoint("kernel", {13}, "in", {}));

    comm->connect(conduits, peer_dims, peer_locations);
    return std::move(comm);
}

std::unique_ptr<Communicator> connected_communicator3() {
    PortsDescription desc({
            {Operator::O_I, {"out[]"}},
            {Operator::S, {"in[]"}}
            });

    std::unique_ptr<Communicator> comm(new Communicator(
            Reference("kernel"), {}, desc, 0));

    std::vector<Conduit> conduits({
        Conduit("kernel.out", "other.in"),
        Conduit("other.out", "kernel.in")});

    PeerDims peer_dims({{Reference("other"), {}}});

    PeerLocations peer_locations({
            {Reference("other"), {"tcp:test"}}});

    MockPeerManager::get_peer_dims_table.emplace("other", std::vector<int>({}));
    MockPeerManager::get_peer_endpoint_table.emplace("out[13]", Endpoint("other", {}, "in", {13}));
    MockPeerManager::get_peer_endpoint_table.emplace("in[13]", Endpoint("other", {}, "out", {13}));
    MockPeerManager::get_peer_port_table.emplace("out", "other.in");
    MockPeerManager::get_peer_port_table.emplace("in", "other.out");

    comm->connect(conduits, peer_dims, peer_locations);
    return std::move(comm);
}


TEST(libmuscle_communicator, create_communicator) {
    reset_mocks();
    Communicator comm(
            Reference("kernel"), {13}, {}, 0);
    ASSERT_EQ(MockTcpServer::num_constructed, 1);
    ASSERT_EQ(MockTcpServer::last_instance_id, "kernel[13]");
    ASSERT_EQ(MockTcpClient::num_constructed, 0);
}

TEST(libmuscle_communicator, get_locations) {
    reset_mocks();
    Communicator comm(
            Reference("kernel"), {13}, {}, 0);
    ASSERT_EQ(comm.get_locations().size(), 1);
    ASSERT_EQ(comm.get_locations()[0], "tcp:test_location");
}

TEST(libmuscle_communicator, test_connect) {
    reset_mocks();
    Communicator comm(
            Reference("kernel"), {13}, {}, 0);

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
    auto const & ports = libmuscle::TestCommunicator::ports_(comm);

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
            Reference("kernel"), {13}, desc, 0);

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

    MockPeerManager::get_peer_port_table.emplace("in", "other1.out");
    MockPeerManager::get_peer_port_table.emplace("out1", "other.in");
    MockPeerManager::get_peer_port_table.emplace("out2", "other3.in");

    MockPeerManager::get_peer_dims_table.emplace("other1", std::vector<int>({20, 7}));
    MockPeerManager::get_peer_dims_table.emplace("other", std::vector<int>({25}));
    MockPeerManager::get_peer_dims_table.emplace("other3", std::vector<int>({20}));

    comm.connect(conduits, peer_dims, peer_locations);

    ASSERT_EQ(MockPeerManager::last_constructed_conduits, conduits);
    ASSERT_EQ(MockPeerManager::last_constructed_peer_dims, peer_dims);
    ASSERT_EQ(MockPeerManager::last_constructed_peer_locations, peer_locations);

    auto const & ports = libmuscle::TestCommunicator::ports_(comm);

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
            Reference("kernel"), {13}, desc, 0);

    std::vector<Conduit> conduits({
        Conduit("other.out", "kernel.in")
        });

    PeerDims peer_dims({
            {Reference("other"), {20, 7, 30}}
            });

    PeerLocations peer_locations({
            {Reference("other"), {"tcp:test"}}
            });

    MockPeerManager::get_peer_port_table.emplace("in", "other.out");
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
            Reference("kernel"), {13}, {}, 0);

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

    MockPeerManager::get_peer_port_table.emplace("in", "other1.out");
    MockPeerManager::get_peer_port_table.emplace("out1", "other.in");
    MockPeerManager::get_peer_port_table.emplace("out3", "other2.in");

    MockPeerManager::get_peer_dims_table.emplace("other1", std::vector<int>({20, 7}));
    MockPeerManager::get_peer_dims_table.emplace("other", std::vector<int>({25}));
    MockPeerManager::get_peer_dims_table.emplace("other2", std::vector<int>());

    comm.connect(conduits, peer_dims, peer_locations);

    ASSERT_EQ(MockPeerManager::last_constructed_conduits, conduits);
    ASSERT_EQ(MockPeerManager::last_constructed_peer_dims, peer_dims);
    ASSERT_EQ(MockPeerManager::last_constructed_peer_locations, peer_locations);

    auto const & ports = libmuscle::TestCommunicator::ports_(comm);

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

    Message message(0.0, "test");
    comm->send_message("out", message);

    ASSERT_EQ(MockPostOffice::last_receiver, "other.in[13]");
    ASSERT_EQ(MockPostOffice::last_message->sender, "kernel[13].out");
    ASSERT_EQ(MockPostOffice::last_message->receiver, "other.in[13]");
    ASSERT_EQ(MockPostOffice::last_message->timestamp, 0.0);
    ASSERT_FALSE(MockPostOffice::last_message->next_timestamp.is_set());
    ASSERT_EQ(MockPostOffice::last_message->data.as<std::string>(), "test");
    ASSERT_TRUE(MockPostOffice::last_message->parameter_overlay.is_a<Settings>());
}

TEST(libmuscle_communicator, send_on_disconnected_port) {
    reset_mocks();

    auto comm = connected_communicator();

    MockPeerManager::is_connected_return_value = false;

    Message message(0.0, "test");
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
    ASSERT_TRUE(MockPostOffice::last_message->parameter_overlay.is_a<Settings>());
}

TEST(libmuscle_communicator, send_message_with_slot) {
    reset_mocks();
    auto comm = connected_communicator2();

    Message message(0.0, "test");
    comm->send_message("out", message, 13);

    ASSERT_EQ(MockPostOffice::last_receiver, "kernel[13].in");
    ASSERT_EQ(MockPostOffice::last_message->sender, "other.out[13]");
    ASSERT_EQ(MockPostOffice::last_message->receiver, "kernel[13].in");
    ASSERT_EQ(MockPostOffice::last_message->timestamp, 0.0);
    ASSERT_FALSE(MockPostOffice::last_message->next_timestamp.is_set());
    ASSERT_EQ(MockPostOffice::last_message->data.as<std::string>(), "test");
    ASSERT_TRUE(MockPostOffice::last_message->parameter_overlay.is_a<Settings>());
}

TEST(libmuscle_communicator, send_message_resizable) {
    reset_mocks();
    auto comm = connected_communicator3();
    Message message(0.0, "test");

    ASSERT_THROW(comm->send_message("out", message, 13), std::runtime_error);

    comm->get_port("out").set_length(20);
    comm->send_message("out", message, 13);

    std::cerr << "rec: " << MockPostOffice::last_receiver;
    ASSERT_EQ(MockPostOffice::last_receiver, "other.in[13]");
    ASSERT_EQ(MockPostOffice::last_message->sender, "kernel.out[13]");
    ASSERT_EQ(MockPostOffice::last_message->receiver, "other.in[13]");
    ASSERT_EQ(MockPostOffice::last_message->port_length.get(), 20);
    ASSERT_EQ(MockPostOffice::last_message->timestamp, 0.0);
    ASSERT_FALSE(MockPostOffice::last_message->next_timestamp.is_set());
    ASSERT_EQ(MockPostOffice::last_message->data.as<std::string>(), "test");
    ASSERT_TRUE(MockPostOffice::last_message->parameter_overlay.is_a<Settings>());
}

TEST(libmuscle_communicator, send_with_parameters) {
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
    ASSERT_TRUE(MockPostOffice::last_message->parameter_overlay.is_a<Settings>());
    ASSERT_EQ(MockPostOffice::last_message->parameter_overlay.as<Settings>()["test2"], "testing");
}

TEST(libmuscle_communicator, send_settings) {
    reset_mocks();
    auto comm = connected_communicator();

    Settings settings;
    settings["test1"] = "testing";
    Message message(0.0, settings);
    comm->send_message("out", message);

    ASSERT_EQ(MockPostOffice::last_receiver, "other.in[13]");
    ASSERT_EQ(MockPostOffice::last_message->sender, "kernel[13].out");
    ASSERT_EQ(MockPostOffice::last_message->receiver, "other.in[13]");
    ASSERT_EQ(MockPostOffice::last_message->timestamp, 0.0);
    ASSERT_FALSE(MockPostOffice::last_message->next_timestamp.is_set());
    ASSERT_TRUE(MockPostOffice::last_message->data.is_a<Settings>());
    ASSERT_EQ(MockPostOffice::last_message->data.as<Settings>()["test1"], "testing");
    ASSERT_TRUE(MockPostOffice::last_message->parameter_overlay.is_a<Settings>());
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
    ASSERT_TRUE(libmuscle::is_close_port(MockPostOffice::last_message->data));
}

TEST(libmuscle_communicator, receive_message) {
    reset_mocks();
    MockTcpClient::next_receive_message.sender = "other.out[13]";
    MockTcpClient::next_receive_message.receiver = "kernel[13].in";

    auto comm = connected_communicator();
    Message msg = comm->receive_message("in");

    ASSERT_EQ(MockTcpClient::last_receiver, "kernel[13].in");
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
    ASSERT_TRUE(msg.settings().empty());
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
    MockTcpClient::next_receive_message.sender = "kernel[13].out";
    MockTcpClient::next_receive_message.receiver = "other.in[13]";

    auto comm = connected_communicator2();
    Message msg = comm->receive_message("in", 13);

    ASSERT_EQ(MockTcpClient::last_receiver, "other.in[13]");
    ASSERT_TRUE(msg.data().is_a_dict());
    ASSERT_EQ(msg.data()["test1"].as<int>(), 12);
}

TEST(libmuscle_communicator, receive_message_resizable) {
    reset_mocks();
    MockTcpClient::next_receive_message.sender = "other.out[13]";
    MockTcpClient::next_receive_message.receiver = "kernel.in[13]";
    MockTcpClient::next_receive_message.port_length = 20;

    auto comm = connected_communicator3();
    Message msg = comm->receive_message("in", 13);

    ASSERT_EQ(MockTcpClient::last_receiver, "kernel.in[13]");
    ASSERT_TRUE(msg.data().is_a_dict());
    ASSERT_EQ(msg.data()["test1"].as<int>(), 12);
    ASSERT_EQ(comm->get_port("in").get_length(), 20);
}

TEST(libmuscle_communicator, receive_with_parameters) {
    reset_mocks();
    MockTcpClient::next_receive_message.sender = "other.out[13]";
    MockTcpClient::next_receive_message.receiver = "kernel[13].in";

    auto comm = connected_communicator();
    Message msg = comm->receive_message("in");

    ASSERT_EQ(MockTcpClient::last_receiver, "kernel[13].in");
    ASSERT_TRUE(msg.data().is_a_dict());
    ASSERT_EQ(msg.data()["test1"].as<int>(), 12);
    ASSERT_EQ(msg.settings().at("test2"), 3.1);
}

TEST(libmuscle_communicator, receive_message_with_slot_and_parameters) {
    reset_mocks();
    MockTcpClient::next_receive_message.sender = "kernel[13].out";
    MockTcpClient::next_receive_message.receiver = "other.in[13]";

    auto comm = connected_communicator2();
    Message msg = comm->receive_message("in", 13);

    ASSERT_EQ(MockTcpClient::last_receiver, "other.in[13]");
    ASSERT_TRUE(msg.data().is_a_dict());
    ASSERT_EQ(msg.data()["test1"].as<int>(), 12);
    ASSERT_EQ(msg.settings().at("test2"), 3.1);
}

