#include <stdexcept>

#include <gtest/gtest.h>

#include <libmuscle/port.hpp>
#include <muscle_manager_protocol/muscle_manager_protocol.pb.h>
#include <ymmsl/identity.hpp>


namespace mmp = muscle_manager_protocol;

using libmuscle::impl::Port;
using ymmsl::Identifier;
using ymmsl::Operator;


int main(int argc, char *argv[]) {
    ::testing::InitGoogleTest(&argc, argv);
    return RUN_ALL_TESTS();
}

TEST(libmuscle_port, test_create_port) {
    auto port = Port("out", Operator::O_I, false, true, 0, {});
    ASSERT_EQ(port.name, Identifier("out"));
    ASSERT_EQ(port.oper, Operator::O_I);
    ASSERT_FALSE(port.is_vector());
    ASSERT_FALSE(port.is_resizable());
    ASSERT_TRUE(port.is_connected());
}

TEST(libmuscle_port, test_port_properties) {
    auto port = Port("out", Operator::O_F, false, false, 0, {});

    ASSERT_FALSE(port.is_vector());
    ASSERT_FALSE(port.is_resizable());
    ASSERT_FALSE(port.is_connected());
    ASSERT_THROW(port.get_length(), std::runtime_error);
    ASSERT_THROW(port.set_length(3), std::runtime_error);

    port = Port("out", Operator::O_F, true, true, 0, {10});
    ASSERT_TRUE(port.is_vector());
    ASSERT_FALSE(port.is_resizable());
    ASSERT_EQ(port.get_length(), 10);
    ASSERT_THROW(port.set_length(3), std::runtime_error);

    port = Port("out", Operator::O_F, false, true, 1, {10});
    ASSERT_FALSE(port.is_vector());
    ASSERT_FALSE(port.is_resizable());
    ASSERT_THROW(port.get_length(), std::runtime_error);
    ASSERT_THROW(port.set_length(4), std::runtime_error);

    port = Port("out", Operator::O_F, true, true, 1, {10, 20});
    ASSERT_TRUE(port.is_vector());
    ASSERT_FALSE(port.is_resizable());
    ASSERT_EQ(port.get_length(), 20);
    ASSERT_THROW(port.set_length(5), std::runtime_error);

    port = Port("out", Operator::O_F, false, true, 2, {12});
    ASSERT_FALSE(port.is_vector());
    ASSERT_FALSE(port.is_resizable());
    ASSERT_THROW(port.get_length(), std::runtime_error);
    ASSERT_THROW(port.set_length(9), std::runtime_error);

    port = Port("out", Operator::O_F, true, true, 1, {13});
    ASSERT_TRUE(port.is_vector());
    ASSERT_TRUE(port.is_resizable());
    ASSERT_EQ(port.get_length(), 0);
    port.set_length(27);
    ASSERT_EQ(port.get_length(), 27);
}

