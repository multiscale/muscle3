#include <gtest/gtest.h>

#include "libmuscle/operator.hpp"
#include "muscle_manager_protocol/muscle_manager_protocol.pb.h"
#include <ymmsl/ymmsl.hpp>


namespace mmp = muscle_manager_protocol;


int main(int argc, char *argv[]) {
    ::testing::InitGoogleTest(&argc, argv);
    return RUN_ALL_TESTS();
}

TEST(libmuscle_operator, operator_from_grpc) {
    mmp::Operator mmp_op1 = mmp::OPERATOR_F_INIT;

    ASSERT_EQ(libmuscle::impl::operator_from_grpc(mmp_op1), ymmsl::Operator::F_INIT);
}

TEST(libmuscle_operator, operator_to_grpc) {
    auto op = ymmsl::Operator::S;

    ASSERT_EQ(libmuscle::impl::operator_to_grpc(op), mmp::OPERATOR_S);
}

