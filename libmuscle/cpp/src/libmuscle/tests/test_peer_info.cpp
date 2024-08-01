#include "libmuscle/peer_info.hpp"

#include <libmuscle/namespace.hpp>
#include <ymmsl/ymmsl.hpp>

#include <memory>

#include <gtest/gtest.h>


using libmuscle::_MUSCLE_IMPL_NS::PeerDims;
using libmuscle::_MUSCLE_IMPL_NS::PeerLocations;
using libmuscle::_MUSCLE_IMPL_NS::PeerInfo;
using ymmsl::Conduit;
using ymmsl::Reference;


int main(int argc, char *argv[]) {
    ::testing::InitGoogleTest(&argc, argv);
    return RUN_ALL_TESTS();
}


PeerInfo peer_info() {
    Reference kernel("kernel");
    std::vector<int> index({13});

    std::vector<Conduit> conduits({
        Conduit("kernel.out", "other.in"),
        Conduit("other.out", "kernel.in")});

    PeerDims peer_dims({{Reference("other"), {}}});

    PeerLocations peer_locations({
            {Reference("other"), {"tcp:other"}}});

    return PeerInfo(kernel, index, conduits, peer_dims, peer_locations);
}

PeerInfo peer_info2() {
    Reference kernel("other");
    std::vector<int> index;

    std::vector<Conduit> conduits({
        Conduit("kernel.out", "other.in"),
        Conduit("other.out", "kernel.in")});

    PeerDims peer_dims({{Reference("kernel"), {20}}});

    PeerLocations peer_locations({
            {Reference("kernel"), {"tcp:kernel"}}});

    return PeerInfo(kernel, index, conduits, peer_dims, peer_locations);
}

PeerInfo peer_info3() {
    Reference kernel("kernel");
    std::vector<int> index;

    std::vector<Conduit> conduits({
        Conduit("kernel.out", "other.in"),
        Conduit("other.out", "kernel.in")});

    PeerDims peer_dims({{Reference("other"), {}}});

    PeerLocations peer_locations({
            {Reference("other"), {"tcp:other"}}});

    return PeerInfo(kernel, index, conduits, peer_dims, peer_locations);
}

TEST(libmuscle_peer_info, create_peer_info) {
    peer_info();
}

TEST(libmuscle_peer_info, is_connected) {
    auto pi = peer_info();

    ASSERT_TRUE(pi.is_connected("out"));
    ASSERT_TRUE(pi.is_connected("in"));
    ASSERT_FALSE(pi.is_connected("not_connected"));
}

TEST(libmuscle_peer_info, get_peer_port) {
    auto pi = peer_info();
    ASSERT_EQ(pi.get_peer_ports("out"), std::vector<Reference>({"other.in"}));
    ASSERT_EQ(pi.get_peer_ports("in"), std::vector<Reference>({"other.out"}));

    auto pi2 = peer_info2();
    ASSERT_EQ(pi2.get_peer_ports("out"), std::vector<Reference>({"kernel.in"}));
    ASSERT_EQ(pi2.get_peer_ports("in"), std::vector<Reference>({"kernel.out"}));

    auto pi3 = peer_info3();
    ASSERT_EQ(pi3.get_peer_ports("out"), std::vector<Reference>({"other.in"}));
    ASSERT_EQ(pi3.get_peer_ports("in"), std::vector<Reference>({"other.out"}));
}

TEST(libmuscle_peer_info, get_peer_dims) {
    auto pi = peer_info();
    ASSERT_EQ(pi.get_peer_dims("other"), std::vector<int>({}));

    auto pi2 = peer_info2();
    ASSERT_EQ(pi2.get_peer_dims("kernel"), std::vector<int>({20}));

    auto pi3 = peer_info3();
    ASSERT_EQ(pi3.get_peer_dims("other"), std::vector<int>({}));
}

TEST(libmuscle_peer_info, get_peer_locations) {
    auto pi = peer_info();
    ASSERT_EQ(pi.get_peer_locations("other"),
            std::vector<std::string>({"tcp:other"}));

    auto pi2 = peer_info2();
    ASSERT_EQ(pi2.get_peer_locations("kernel"),
            std::vector<std::string>({"tcp:kernel"}));

    auto pi3 = peer_info3();
    ASSERT_EQ(pi3.get_peer_locations("other"),
            std::vector<std::string>({"tcp:other"}));
}

TEST(libmuscle_peer_info, get_peer_endpoint) {
    auto pi = peer_info();
    ASSERT_EQ(std::string(pi.get_peer_endpoints("out", {})[0]), "other.in[13]");
    ASSERT_EQ(std::string(pi.get_peer_endpoints("in", {})[0]), "other.out[13]");

    auto pi2 = peer_info2();
    ASSERT_EQ(std::string(pi2.get_peer_endpoints("out", {11})[0]), "kernel[11].in");
    ASSERT_EQ(std::string(pi2.get_peer_endpoints("in", {11})[0]), "kernel[11].out");

    auto pi3 = peer_info3();
    ASSERT_EQ(std::string(pi3.get_peer_endpoints("out", {42})[0]), "other.in[42]");
    ASSERT_EQ(std::string(pi3.get_peer_endpoints("in", {42})[0]), "other.out[42]");
}

