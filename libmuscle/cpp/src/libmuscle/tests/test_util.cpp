#include "libmuscle/util.hpp"

#include <utility>

#include <gtest/gtest.h>



// Note: do not run in parallel, OptMock has static members that are reused
// between tests, and things will get messed up if you run them simultaneously.

int main(int argc, char *argv[]) {
    ::testing::InitGoogleTest(&argc, argv);
    return RUN_ALL_TESTS();
}


struct OptMock {
    OptMock()
        : default_constructed(true)
        , copy_constructed(false)
        , move_constructed(false)
        , copy_constructed_from(0)
        , move_constructed_from(0)
        , copy_assigned_to(0)
        , move_assigned_to(0)
        , copy_assigned_from(0)
        , move_assigned_from(0)
    {}

    OptMock(OptMock const & rhs)
        : default_constructed(false)
        , copy_constructed(true)
        , move_constructed(false)
        , copy_constructed_from(0)
        , move_constructed_from(0)
        , copy_assigned_to(0)
        , move_assigned_to(0)
        , copy_assigned_from(0)
        , move_assigned_from(0)
    {
        ++rhs.copy_constructed_from;
    }

    OptMock(OptMock && rhs)
        : default_constructed(false)
        , copy_constructed(false)
        , move_constructed(true)
        , copy_constructed_from(0)
        , move_constructed_from(0)
        , copy_assigned_to(0)
        , move_assigned_to(0)
        , copy_assigned_from(0)
        , move_assigned_from(0)
    {
        ++rhs.move_constructed_from;
    }

    OptMock const & operator=(OptMock const & rhs) {
        ++copy_assigned_to;
        ++rhs.copy_assigned_from;
        return *this;
    }

    OptMock const & operator=(OptMock && rhs) {
        ++move_assigned_to;
        ++rhs.move_assigned_from;
        return *this;
    }

    ~OptMock() {
        ++destructed;
    }

    static void reset() {
        destructed = 0;
    }

    bool default_constructed;
    bool copy_constructed;
    bool move_constructed;
    mutable int copy_constructed_from;
    int move_constructed_from;
    int copy_assigned_to;
    int move_assigned_to;
    mutable int copy_assigned_from;
    int move_assigned_from;

    static int destructed;
};


int OptMock::destructed = -32768;       // random weird number


TEST(libmuscle_util, create_unset_optional) {
    OptMock::reset();
    libmuscle::Optional<OptMock> o1;
    ASSERT_FALSE(o1.is_set());
}

TEST(libmuscle_util, create_set_optional) {
    OptMock::reset();
    OptMock mock;
    ASSERT_TRUE(mock.default_constructed);
    libmuscle::Optional<OptMock> o1(mock);
    ASSERT_FALSE(o1.get().default_constructed);
    ASSERT_TRUE(o1.get().copy_constructed);
    ASSERT_EQ(mock.copy_constructed_from, 1);
}

TEST(libmuscle_util, copy_construct_from_unset_optional) {
    OptMock::reset();
    libmuscle::Optional<OptMock> o1;
    libmuscle::Optional<OptMock> o2(o1);
    ASSERT_FALSE(o1.is_set());
    ASSERT_FALSE(o2.is_set());
}

TEST(libmuscle_util, copy_construct_from_set_optional) {
    OptMock::reset();
    OptMock mock;
    libmuscle::Optional<OptMock> o1(mock);
    libmuscle::Optional<OptMock> o2(o1);
    ASSERT_TRUE(o2.get().copy_constructed);
    ASSERT_EQ(o1.get().copy_constructed_from, 1);
}

TEST(libmuscle_util, move_construct_from_unset_optional) {
    OptMock::reset();
    {
        libmuscle::Optional<OptMock> o1;
        libmuscle::Optional<OptMock> o2(std::move(o1));
        ASSERT_FALSE(o2.is_set());
    }
    ASSERT_EQ(OptMock::destructed, 0);
}

TEST(libmuscle_util, move_construct_from_set_optional) {
    OptMock::reset();
    {
        OptMock mock;
        libmuscle::Optional<OptMock> o1(mock);
        libmuscle::Optional<OptMock> o2(std::move(o1));
        ASSERT_EQ(o1.get().move_constructed_from, 1);
        ASSERT_TRUE(o2.get().move_constructed);
    }
    ASSERT_EQ(OptMock::destructed, 3);
}

TEST(libmuscle_util, copy_assign_from_unset_to_unset_optional) {
    OptMock::reset();
    libmuscle::Optional<OptMock> o1;
    libmuscle::Optional<OptMock> o2;
    o2 = o1;
    ASSERT_FALSE(o2.is_set());
}

TEST(libmuscle_util, copy_assign_from_set_to_unset_optional) {
    OptMock::reset();
    OptMock mock;
    libmuscle::Optional<OptMock> o1(mock);
    ASSERT_EQ(mock.copy_constructed_from, 1);
    ASSERT_TRUE(o1.get().copy_constructed);

    libmuscle::Optional<OptMock> o2;
    o2 = o1;
    ASSERT_TRUE(o2.get().copy_constructed);
    ASSERT_EQ(o1.get().copy_constructed_from, 1);
}

TEST(libmuscle_util, copy_assign_from_set_to_set_optional) {
    OptMock::reset();
    {
        OptMock mock;
        libmuscle::Optional<OptMock> o1(mock);
        libmuscle::Optional<OptMock> o2(mock);
        ASSERT_TRUE(o2.get().copy_constructed);

        o2 = o1;
        ASSERT_TRUE(o2.get().copy_constructed);
        ASSERT_EQ(o1.get().copy_assigned_from, 1);
        ASSERT_EQ(o2.get().copy_assigned_to, 1);
    }
    ASSERT_EQ(OptMock::destructed, 3);
}

TEST(libmuscle_util, copy_assign_from_unset_to_set_optional) {
    OptMock::reset();
    {
        OptMock mock;
        libmuscle::Optional<OptMock> o1;
        libmuscle::Optional<OptMock> o2(mock);
        ASSERT_TRUE(o2.get().copy_constructed);

        o2 = o1;
        ASSERT_FALSE(o2.is_set());
    }
    ASSERT_EQ(OptMock::destructed, 2);
}

TEST(libmuscle_util, move_assign_from_unset_to_unset_optional) {
    OptMock::reset();
    {
        libmuscle::Optional<OptMock> o1;
        libmuscle::Optional<OptMock> o2;
        o2 = std::move(o1);
        ASSERT_FALSE(o1.is_set());
        ASSERT_FALSE(o2.is_set());
    }
    ASSERT_EQ(OptMock::destructed, 0);
}

TEST(libmuscle_util, move_assign_from_set_to_unset_optional) {
    OptMock::reset();
    {
        OptMock mock;
        libmuscle::Optional<OptMock> o1(mock);
        libmuscle::Optional<OptMock> o2;
        o2 = std::move(o1);
        ASSERT_TRUE(o1.get().copy_constructed);
        ASSERT_EQ(o1.get().move_constructed_from, 1);
        ASSERT_TRUE(o2.get().move_constructed);
    }
    ASSERT_EQ(OptMock::destructed, 3);
}

TEST(libmuscle_util, move_assign_from_set_to_set_optional) {
    OptMock::reset();
    {
        OptMock mock;
        libmuscle::Optional<OptMock> o1(mock);
        libmuscle::Optional<OptMock> o2(mock);
        o2 = std::move(o1);
        ASSERT_EQ(o2.get().move_assigned_to, 1);
        ASSERT_EQ(o1.get().move_assigned_from, 1);
    }
    ASSERT_EQ(OptMock::destructed, 3);
}

TEST(libmuscle_util, equality_comparison) {
    libmuscle::Optional<int> o1, o2, o3(10), o4(10), o5(11);
    ASSERT_TRUE(o1 == o2);
    ASSERT_FALSE(o1 == o3);
    ASSERT_FALSE(o3 == o1);
    ASSERT_TRUE(o3 == o4);
    ASSERT_FALSE(o3 == o5);
}

TEST(libmuscle_util, inequality_comparison) {
    libmuscle::Optional<int> o1, o2, o3(10), o4(10), o5(11);
    ASSERT_FALSE(o1 != o2);
    ASSERT_TRUE(o1 != o3);
    ASSERT_TRUE(o3 != o1);
    ASSERT_FALSE(o3 != o4);
    ASSERT_TRUE(o3 != o5);
}



