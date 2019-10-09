#include <gtest/gtest.h>
#include <msgpack.hpp>

#include "libmuscle/mcp/message.hpp"

#include "libmuscle/data.hpp"
#include "libmuscle/util.hpp"
#include "ymmsl/identity.hpp"

#include <utility>


using libmuscle::impl::Data;
using libmuscle::impl::mcp::Message;
using ymmsl::Reference;


int main(int argc, char *argv[]) {
    ::testing::InitGoogleTest(&argc, argv);
    return RUN_ALL_TESTS();
}

TEST(test_mcp_message, create_mcp_message) {
    Data test("test");
    Data abc("abc");

    Message m(
            Reference("sender.port"), Reference("receiver.port"),
            10,
            100.1, 101.0,
            test, abc
            );

    ASSERT_EQ(m.sender, "sender.port");
    ASSERT_EQ(m.receiver, "receiver.port");
    ASSERT_EQ(m.port_length, 10);
    ASSERT_EQ(m.timestamp, 100.1);
    ASSERT_EQ(m.next_timestamp, 101.0);
    ASSERT_EQ(m.settings_overlay.as<std::string>(), "test");
    ASSERT_EQ(m.data.as<std::string>(), "abc");
}

TEST(test_mcp_message, create_mcp_message_minimal) {
    Data test, abc;

    Message m(
            Reference("sender.port"), Reference("receiver.port"),
            {},
            100.1, {},
            test, abc
            );

    ASSERT_EQ(m.sender, "sender.port");
    ASSERT_EQ(m.receiver, "receiver.port");
    ASSERT_FALSE(m.port_length.is_set());
    ASSERT_EQ(m.timestamp, 100.1);
    ASSERT_FALSE(m.next_timestamp.is_set());
    ASSERT_TRUE(m.settings_overlay.is_nil());
    ASSERT_TRUE(m.data.is_nil());
}

