#include <gtest/gtest.h>
#include <msgpack.hpp>

#include "libmuscle/mcp/message.hpp"
#include "libmuscle/util.hpp"
#include "ymmsl/identity.hpp"

#include <utility>


using libmuscle::mcp::Message;
using ymmsl::Reference;


int main(int argc, char *argv[]) {
    ::testing::InitGoogleTest(&argc, argv);
    return RUN_ALL_TESTS();
}

TEST(test_mcp_message, create_mcp_message) {
    msgpack::sbuffer test, abc;
    test.write("test", 5);
    abc.write("abc", 4);

    Message m(
            Reference("sender.port"), Reference("receiver.port"),
            10,
            100.1, 101.0,
            std::move(test), std::move(abc)
            );

    ASSERT_EQ(m.sender, "sender.port");
    ASSERT_EQ(m.receiver, "receiver.port");
    ASSERT_EQ(m.port_length, 10);
    ASSERT_EQ(m.timestamp, 100.1);
    ASSERT_EQ(m.next_timestamp, 101.0);
    ASSERT_STREQ(m.parameter_overlay.data(), "test");
    ASSERT_STREQ(m.data.data(), "abc");
}

TEST(test_mcp_message, create_mcp_message_minimal) {
    msgpack::sbuffer test, abc;

    Message m(
            Reference("sender.port"), Reference("receiver.port"),
            ::libmuscle::Optional<int>(),
            100.1, ::libmuscle::Optional<double>(),
            std::move(test), std::move(abc)
            );

    ASSERT_EQ(m.sender, "sender.port");
    ASSERT_EQ(m.receiver, "receiver.port");
    ASSERT_FALSE(m.port_length.is_set());
    ASSERT_EQ(m.timestamp, 100.1);
    ASSERT_FALSE(m.next_timestamp.is_set());
    ASSERT_EQ(m.parameter_overlay.size(), 0);
    ASSERT_EQ(m.data.size(), 0);
}

