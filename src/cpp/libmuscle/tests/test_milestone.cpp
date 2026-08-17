#include <stdexcept>

#include <gtest/gtest.h>
#include <msgpack.hpp>

#include "libmuscle/data.hpp"
#include "libmuscle/mcp/data_pack.hpp"
#include <libmuscle/namespace.hpp>
#include <libmuscle/milestone.hpp>
#include <ymmsl/ymmsl.hpp>


using libmuscle::_MUSCLE_IMPL_NS::Milestone;
using libmuscle::_MUSCLE_IMPL_NS::is_milestone;
using libmuscle::_MUSCLE_IMPL_NS::IterationCount;
using libmuscle::_MUSCLE_IMPL_NS::mcp::unpack_data;
using libmuscle::_MUSCLE_IMPL_NS::Data;
using libmuscle::_MUSCLE_IMPL_NS::DataConstRef;


int main(int argc, char *argv[]) {
    ::testing::InitGoogleTest(&argc, argv);
    return RUN_ALL_TESTS();
}

TEST(libmuscle_milestone, test_create_final_milestone) {
    auto milestone = Milestone(IterationCount({}));

    ASSERT_EQ(milestone.iteration().size(), 0);
    ASSERT_TRUE(milestone.is_final_milestone());
}

TEST(libmuscle_milestone, test_create_milestone) {
    auto milestone = Milestone(IterationCount({1, 2}));

    ASSERT_EQ(milestone.iteration(), IterationCount({1, 2}));
    ASSERT_FALSE(milestone.is_final_milestone());
}

TEST(libmuscle_milestone, test_is_milestone) {
    Data d;
    ASSERT_FALSE(is_milestone(d));

    Data d2 = Data::list();
    ASSERT_FALSE(is_milestone(d2));

    ASSERT_THROW(Milestone milestone(d), std::runtime_error);
    ASSERT_THROW(Milestone milestone(d2), std::runtime_error);
}

TEST(libmuscle_milestone, test_encode_decode_final_milestone) {
    auto milestone = Milestone(IterationCount({}));

    msgpack::sbuffer buf;
    msgpack::pack(buf, DataConstRef(milestone));

    auto zone = std::make_shared<msgpack::zone>();
    Data d2(unpack_data(zone, buf.data(), buf.size()));

    ASSERT_TRUE(is_milestone(d2));

    Milestone const * m2 = reinterpret_cast<Milestone const*>(&d2);
    ASSERT_EQ(m2->iteration(), IterationCount());
    ASSERT_TRUE(m2->is_final_milestone());
}

TEST(libmuscle_milestone, test_encode_decode_milestone) {
    auto milestone = Milestone(IterationCount({1, 2}));

    msgpack::sbuffer buf;
    msgpack::pack(buf, DataConstRef(milestone));

    auto zone = std::make_shared<msgpack::zone>();
    Data d2(unpack_data(zone, buf.data(), buf.size()));

    ASSERT_TRUE(is_milestone(d2));

    Milestone const * m2 = reinterpret_cast<Milestone const*>(&d2);
    ASSERT_EQ(m2->iteration(), IterationCount({1, 2}));
    ASSERT_FALSE(m2->is_final_milestone());
}
