// Inject mocks

// into the real implementation under test.
#include <ymmsl/ymmsl.hpp>

#include <libmuscle/peer_info.cpp>
#include <libmuscle/port.cpp>
#include <libmuscle/port_manager.cpp>


// Test code dependencies
#include <memory>
#include <numeric>
#include <stdexcept>
#include <map>
#include <gtest/gtest.h>
#include <libmuscle/namespace.hpp>
#include <libmuscle/port.hpp>


int main(int argc, char *argv[]) {
    ::testing::InitGoogleTest(&argc, argv);
    return RUN_ALL_TESTS();
}

using libmuscle::_MUSCLE_IMPL_NS::Optional;
using libmuscle::_MUSCLE_IMPL_NS::PeerDims;
using libmuscle::_MUSCLE_IMPL_NS::PeerInfo;
using libmuscle::_MUSCLE_IMPL_NS::PeerLocations;
using libmuscle::_MUSCLE_IMPL_NS::Port;
using libmuscle::_MUSCLE_IMPL_NS::PortsDescription;
using libmuscle::_MUSCLE_IMPL_NS::PortManager;

using ymmsl::Conduit;
using ymmsl::Identifier;
using ymmsl::Operator;
using ymmsl::Reference;


struct libmuscle_port_manager : ::testing::Test {
    std::vector<int> index_;
    PortManager port_manager_;

    std::vector<int> index2_;
    PortManager port_manager2_;

    libmuscle_port_manager()
        : index_({13})
        , port_manager_(index_, PortsDescription{
                {Operator::O_I, {"out"}},
                {Operator::S, {"in"}}})
        , index2_({})
        , port_manager2_(index2_, PortsDescription{
                {Operator::F_INIT, {"in[]"}},
                {Operator::O_F, {"out[]"}}})
    {
        Reference component_id("other");
        std::vector<Conduit> conduits({
                Conduit("component.out", "other.in"),
                Conduit("other.out", "component.in")});
        PeerDims peer_dims({ {"component", {20}}});
        PeerLocations peer_locations({{"component", {"direct:test"}}});
        PeerInfo peer_info(component_id, index2_, conduits, peer_dims, peer_locations);

        port_manager2_.connect_ports(peer_info);
    }
};


/* Tests */
TEST_F(libmuscle_port_manager, test_connect_ports) {
    Reference component_id("component");
    std::vector<Conduit> conduits({
        Conduit("component.out", "other.in"),
        Conduit("other.settings_out", "component.muscle_settings_in"),
        Conduit("other.out", "component.in")});
    PeerDims peer_dims({{Reference("other"), {}}});
    PeerLocations peer_locations({
            {Reference("other"), {"direct:test"}}});
    PeerInfo peer_info(component_id, index_, conduits, peer_dims, peer_locations);

    port_manager_.connect_ports(peer_info);

    // check automatic ports
    ASSERT_TRUE(port_manager_.settings_in_connected());
    ASSERT_EQ(port_manager_.muscle_settings_in().name, "muscle_settings_in");
    ASSERT_EQ(port_manager_.muscle_settings_in().oper, Operator::F_INIT);
    ASSERT_EQ(port_manager_.muscle_settings_in().length_, -1);

    // check declared ports
    auto const & ports = port_manager_.ports_;

    ASSERT_EQ(ports.at("in").name, "in");
    ASSERT_EQ(ports.at("in").oper, Operator::S);
    ASSERT_EQ(ports.at("in").length_, -1);

    ASSERT_EQ(ports.at("out").name, "out");
    ASSERT_EQ(ports.at("out").oper, Operator::O_I);
    ASSERT_EQ(ports.at("out").length_, -1);
}

TEST_F(libmuscle_port_manager, test_connect_vector_ports) {
    PortsDescription declared_ports({
            {Operator::F_INIT, {"in[]"}},
            {Operator::O_F, {"out1", "out2[]"}}
            });

    PortManager port_manager(index_, declared_ports);

    Reference component_id("component");
    std::vector<Conduit> conduits({
        Conduit("other1.out", "component.in"),
        Conduit("component.out1", "other.in"),
        Conduit("component.out2", "other3.in")
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
    PeerInfo peer_info(component_id, index_, conduits, peer_dims, peer_locations);

    port_manager.connect_ports(peer_info);

    auto const & ports = port_manager.ports_;

    ASSERT_EQ(ports.at("in").name, "in");
    ASSERT_EQ(ports.at("in").oper, Operator::F_INIT);
    ASSERT_TRUE(ports.at("in").is_vector());
    ASSERT_EQ(ports.at("in").length_, 7);
    ASSERT_FALSE(ports.at("in").is_resizable_);

    ASSERT_EQ(ports.at("out1").name, "out1");
    ASSERT_EQ(ports.at("out1").oper, Operator::O_F);
    ASSERT_EQ(ports.at("out1").length_, -1);

    ASSERT_EQ(ports.at("out2").name, "out2");
    ASSERT_EQ(ports.at("out2").oper, Operator::O_F);
    ASSERT_EQ(ports.at("out2").length_, 0);
    ASSERT_TRUE(ports.at("out2").is_resizable_);
}

TEST_F(libmuscle_port_manager, test_connect_multidimensional_ports) {
    PortsDescription declared_ports({
            {Operator::F_INIT, {"in[][]"}}
            });

    PortManager port_manager(index_, declared_ports);

    Reference component_id("component");
    std::vector<Conduit> conduits({
        Conduit("other.out", "component.in")
        });
    PeerDims peer_dims({
            {Reference("other"), {20, 7, 30}}
            });
    PeerLocations peer_locations({
            {Reference("other"), {"direct:test"}}
            });
    PeerInfo peer_info(component_id, index_, conduits, peer_dims, peer_locations);

    ASSERT_THROW(
            port_manager.connect_ports(peer_info), std::invalid_argument);
}

TEST_F(libmuscle_port_manager, test_connect_inferred_ports) {
    PortManager port_manager(index_, {});

    Reference component_id("component");
    std::vector<Conduit> conduits({
        Conduit("other1.out", "component.in"),
        Conduit("component.out1", "other.in"),
        Conduit("component.out3", "other2.in")
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
    PeerInfo peer_info(component_id, index_, conduits, peer_dims, peer_locations);

    port_manager.connect_ports(peer_info);

    auto const & ports = port_manager.ports_;

    ASSERT_EQ(ports.at("in").name, "in");
    ASSERT_EQ(ports.at("in").oper, Operator::F_INIT);
    ASSERT_EQ(ports.at("in").length_, 7);
    ASSERT_FALSE(ports.at("in").is_resizable_);

    ASSERT_EQ(ports.at("out1").name, "out1");
    ASSERT_EQ(ports.at("out1").oper, Operator::O_F);
    ASSERT_EQ(ports.at("out1").length_, -1);

    ASSERT_EQ(ports.at("out3").name, "out3");
    ASSERT_EQ(ports.at("out3").oper, Operator::O_F);
    ASSERT_EQ(ports.at("out3").length_, -1);
}

TEST_F(libmuscle_port_manager, test_port_message_counts) {
    port_manager_.connect_ports(PeerInfo("component", {}, {}, {}, {}));

    auto msg_counts = port_manager_.get_message_counts();
    ASSERT_EQ(msg_counts.size(), 3);
    ASSERT_EQ(msg_counts["in"], std::vector<int>({0}));
    ASSERT_EQ(msg_counts["out"], std::vector<int>({0}));
    ASSERT_EQ(msg_counts["muscle_settings_in"], std::vector<int>({0}));

    port_manager_.get_port("in").increment_num_messages();

    auto msg_counts2 = port_manager_.get_message_counts();
    ASSERT_EQ(msg_counts2.size(), 3);
    ASSERT_EQ(msg_counts2["in"], std::vector<int>({1}));
    ASSERT_EQ(msg_counts2["out"], std::vector<int>({0}));
    ASSERT_EQ(msg_counts2["muscle_settings_in"], std::vector<int>({0}));

    port_manager_.get_port("out").increment_num_messages();
    port_manager_.get_port("out").increment_num_messages();

    auto msg_counts3 = port_manager_.get_message_counts();
    ASSERT_EQ(msg_counts3.size(), 3);
    ASSERT_EQ(msg_counts3["in"], std::vector<int>({1}));
    ASSERT_EQ(msg_counts3["out"], std::vector<int>({2}));
    ASSERT_EQ(msg_counts3["muscle_settings_in"], std::vector<int>({0}));

    port_manager_.muscle_settings_in().increment_num_messages();

    auto msg_counts4 = port_manager_.get_message_counts();
    ASSERT_EQ(msg_counts4.size(), 3);
    ASSERT_EQ(msg_counts4["in"], std::vector<int>({1}));
    ASSERT_EQ(msg_counts4["out"], std::vector<int>({2}));
    ASSERT_EQ(msg_counts4["muscle_settings_in"], std::vector<int>({1}));

    port_manager_.restore_message_counts(msg_counts);

    auto msg_counts5 = port_manager_.get_message_counts();
    ASSERT_EQ(msg_counts5["in"], std::vector<int>({0}));
    ASSERT_EQ(msg_counts5["out"], std::vector<int>({0}));
    ASSERT_EQ(msg_counts5["muscle_settings_in"], std::vector<int>({0}));

    ASSERT_THROW(
            port_manager_.restore_message_counts({{"x?invalid_port", {3}}}),
            std::runtime_error);
}

TEST_F(libmuscle_port_manager, test_vector_port_message_counts) {
    auto msg_counts = port_manager2_.get_message_counts();
    ASSERT_EQ(msg_counts.size(), 3);
    std::vector<int> expected_counts(20);  // 20 zeros
    ASSERT_EQ(msg_counts["out"], expected_counts);
    ASSERT_EQ(msg_counts["in"], expected_counts);
    ASSERT_EQ(msg_counts["muscle_settings_in"], std::vector<int>({0}));

    port_manager2_.get_port("out").increment_num_messages(13);

    msg_counts = port_manager2_.get_message_counts();
    ASSERT_EQ(msg_counts.size(), 3);
    ASSERT_EQ(msg_counts["in"], expected_counts);
    ASSERT_EQ(msg_counts["muscle_settings_in"], std::vector<int>({0}));
    expected_counts[13] = 1;
    ASSERT_EQ(msg_counts["out"], expected_counts);

    std::iota(expected_counts.begin(), expected_counts.end(), 0);
    port_manager2_.restore_message_counts({
            {"out", expected_counts},
            {"in", expected_counts},
            {"muscle_settings_in", {4}}});

    port_manager2_.get_port("out").increment_num_messages(13);

    msg_counts = port_manager2_.get_message_counts();
    ASSERT_EQ(msg_counts.size(), 3);
    ASSERT_EQ(msg_counts["in"], expected_counts);
    ASSERT_EQ(msg_counts["muscle_settings_in"], std::vector<int>({4}));
    expected_counts[13] = 14;
    ASSERT_EQ(msg_counts["out"], expected_counts);
}

