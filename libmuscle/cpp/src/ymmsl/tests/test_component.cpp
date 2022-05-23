#include <gtest/gtest.h>

#include "ymmsl/component.hpp"
#include "ymmsl/identity.hpp"


using ymmsl::impl::Identifier;
using ymmsl::impl::Operator;
using ymmsl::impl::Port;


TEST(ymmsl_component, operator_allows_sending) {
    Operator f_init = Operator::F_INIT;
    Operator o_i = Operator::O_I;

    ASSERT_EQ(allows_sending(f_init), false);
    ASSERT_EQ(allows_sending(o_i), true);
}

TEST(ymmsl_component, operator_allows_receiving) {
    Operator s = Operator::S;
    Operator o_f = Operator::O_F;

    ASSERT_EQ(allows_receiving(s), true);
    ASSERT_EQ(allows_receiving(o_f), false);
}

TEST(ymmsl_component, test_port) {
    auto ep1 = Port(Identifier("test_in"), Operator::F_INIT);

    ASSERT_EQ(ep1.name, "test_in");
    ASSERT_EQ(ep1.oper, Operator::F_INIT);
}

