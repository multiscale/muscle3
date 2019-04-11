#include "tooling.hpp"
#include "gtest/gtest.h"


int main(int argc, char *argv[]) {
    ::testing::InitGoogleTest(&argc, argv);
    return RUN_ALL_TESTS();
}

TEST(example, great_answer) {
    Tooling tooling;

    ASSERT_EQ(tooling.get_test_variable(), 42);
}

