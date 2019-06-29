#include "ymmsl/compute_element.hpp"
#include "gtest/gtest.h"


using ymmsl::Operator;


int main(int argc, char *argv[]) {
    ::testing::InitGoogleTest(&argc, argv);
    return RUN_ALL_TESTS();
}

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

