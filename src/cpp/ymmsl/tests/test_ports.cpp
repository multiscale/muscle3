#include <gtest/gtest.h>

#include "ymmsl/component.hpp"
#include "ymmsl/identity.hpp"
#include "ymmsl/ports.hpp"


using ymmsl::impl::Identifier;
using ymmsl::impl::Operator;
using ymmsl::impl::Port;
using ymmsl::impl::Timeline;


TEST(ymmsl_timeline, string_round_trip) {
    ASSERT_EQ(static_cast<std::string>(Timeline("")), "");
    ASSERT_EQ(static_cast<std::string>(Timeline(":A1:A2")), ":A1:A2");
}

TEST(ymmsl_timeline, equality_by_value) {
    ASSERT_EQ(Timeline(":A1"), Timeline(":A1"));
    ASSERT_FALSE(Timeline(":A1") == Timeline("A1"));
}

TEST(ymmsl_timeline, hash_consistent_with_equality) {
    std::hash<Timeline> hasher;
    ASSERT_EQ(hasher(Timeline(":A1")), hasher(Timeline(":A1")));
}

TEST(ymmsl_timeline, size) {
    ASSERT_EQ(Timeline("").size(), 0);
    ASSERT_EQ(Timeline(":").size(), 0);
    ASSERT_EQ(Timeline("a").size(), 1);
    ASSERT_EQ(Timeline(":a").size(), 1);
    ASSERT_EQ(Timeline("a:b").size(), 2);
    ASSERT_EQ(Timeline(":a:b").size(), 2);
}

TEST(ymmsl_port, test_port) {
    auto ep1 = Port(Identifier("test_in"), Operator::F_INIT);

    ASSERT_EQ(ep1.name, "test_in");
    ASSERT_EQ(ep1.oper, Operator::F_INIT);
    ASSERT_EQ(ep1.timeline, Timeline(""));
}

TEST(ymmsl_port, test_port_with_timeline) {
    auto ep1 = Port(Identifier("out_a1"), Operator::O_I, Timeline(":A1"));

    ASSERT_EQ(ep1.timeline, Timeline(":A1"));
}
