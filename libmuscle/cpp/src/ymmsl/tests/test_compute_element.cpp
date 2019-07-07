#include <gtest/gtest.h>

#include "ymmsl/compute_element.hpp"


using ymmsl::Operator;


TEST(ymmsl_compute_element, operator_allows_sending) {
    Operator f_init = Operator::F_INIT;
    Operator o_i = Operator::O_I;

    ASSERT_EQ(allows_sending(f_init), false);
    ASSERT_EQ(allows_sending(o_i), true);
}

TEST(ymmsl_compute_element, operator_allows_receiving) {
    Operator s = Operator::S;
    Operator o_f = Operator::O_F;

    ASSERT_EQ(allows_receiving(s), true);
    ASSERT_EQ(allows_receiving(o_f), false);
}

