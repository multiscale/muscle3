#include "libmuscle/peer_manager.hpp"

#include <ymmsl/ymmsl.hpp>

#include <memory>

#include <gtest/gtest.h>


using libmuscle::_MUSCLE_IMPL_NS::PeerDims;
using libmuscle::_MUSCLE_IMPL_NS::PeerLocations;
using libmuscle::_MUSCLE_IMPL_NS::PeerManager;
using ymmsl::Conduit;
using ymmsl::Reference;


int main(int argc, char *argv[]) {
    ::testing::InitGoogleTest(&argc, argv);
    return RUN_ALL_TESTS();
}


PeerManager peer_manager() {
    Reference kernel("kernel");
    std::vector<int> index({13});

    std::vector<Conduit> conduits({
        Conduit("kernel.out", "other.in"),
        Conduit("other.out", "kernel.in")});

    PeerDims peer_dims({{Reference("other"), {}}});

    PeerLocations peer_locations({
            {Reference("other"), {"tcp:other"}}});

    return PeerManager(kernel, index, conduits, peer_dims, peer_locations);
}

PeerManager peer_manager2() {
    Reference kernel("other");
    std::vector<int> index;

    std::vector<Conduit> conduits({
        Conduit("kernel.out", "other.in"),
        Conduit("other.out", "kernel.in")});

    PeerDims peer_dims({{Reference("kernel"), {20}}});

    PeerLocations peer_locations({
            {Reference("kernel"), {"tcp:kernel"}}});

    return PeerManager(kernel, index, conduits, peer_dims, peer_locations);
}

PeerManager peer_manager3() {
    Reference kernel("kernel");
    std::vector<int> index;

    std::vector<Conduit> conduits({
        Conduit("kernel.out", "other.in"),
        Conduit("other.out", "kernel.in")});

    PeerDims peer_dims({{Reference("other"), {}}});

    PeerLocations peer_locations({
            {Reference("other"), {"tcp:other"}}});

    return PeerManager(kernel, index, conduits, peer_dims, peer_locations);
}

TEST(libmuscle_peer_manager, create_peer_manager) {
    peer_manager();
}

TEST(libmuscle_peer_manager, is_connected) {
    auto pm = peer_manager();

    ASSERT_TRUE(pm.is_connected("out"));
    ASSERT_TRUE(pm.is_connected("in"));
    ASSERT_FALSE(pm.is_connected("not_connected"));
}

TEST(libmuscle_peer_manager, get_peer_port) {
    auto pm = peer_manager();
    ASSERT_EQ(pm.get_peer_ports("out"), std::vector<Reference>({"other.in"}));
    ASSERT_EQ(pm.get_peer_ports("in"), std::vector<Reference>({"other.out"}));

    auto pm2 = peer_manager2();
    ASSERT_EQ(pm2.get_peer_ports("out"), std::vector<Reference>({"kernel.in"}));
    ASSERT_EQ(pm2.get_peer_ports("in"), std::vector<Reference>({"kernel.out"}));

    auto pm3 = peer_manager3();
    ASSERT_EQ(pm3.get_peer_ports("out"), std::vector<Reference>({"other.in"}));
    ASSERT_EQ(pm3.get_peer_ports("in"), std::vector<Reference>({"other.out"}));
}

TEST(libmuscle_peer_manager, get_peer_dims) {
    auto pm = peer_manager();
    ASSERT_EQ(pm.get_peer_dims("other"), std::vector<int>({}));

    auto pm2 = peer_manager2();
    ASSERT_EQ(pm2.get_peer_dims("kernel"), std::vector<int>({20}));

    auto pm3 = peer_manager3();
    ASSERT_EQ(pm3.get_peer_dims("other"), std::vector<int>({}));
}

TEST(libmuscle_peer_manager, get_peer_locations) {
    auto pm = peer_manager();
    ASSERT_EQ(pm.get_peer_locations("other"),
            std::vector<std::string>({"tcp:other"}));

    auto pm2 = peer_manager2();
    ASSERT_EQ(pm2.get_peer_locations("kernel"),
            std::vector<std::string>({"tcp:kernel"}));

    auto pm3 = peer_manager3();
    ASSERT_EQ(pm3.get_peer_locations("other"),
            std::vector<std::string>({"tcp:other"}));
}

TEST(libmuscle_peer_manager, get_peer_endpoint) {
    auto pm = peer_manager();
    ASSERT_EQ(std::string(pm.get_peer_endpoints("out", {})[0]), "other.in[13]");
    ASSERT_EQ(std::string(pm.get_peer_endpoints("in", {})[0]), "other.out[13]");

    auto pm2 = peer_manager2();
    ASSERT_EQ(std::string(pm2.get_peer_endpoints("out", {11})[0]), "kernel[11].in");
    ASSERT_EQ(std::string(pm2.get_peer_endpoints("in", {11})[0]), "kernel[11].out");

    auto pm3 = peer_manager3();
    ASSERT_EQ(std::string(pm3.get_peer_endpoints("out", {42})[0]), "other.in[42]");
    ASSERT_EQ(std::string(pm3.get_peer_endpoints("in", {42})[0]), "other.out[42]");

}

