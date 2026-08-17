#include <gtest/gtest.h>
#include <msgpack.hpp>

#include <libmuscle/mpp_message.hpp>

#include <libmuscle/data.hpp>
#include <libmuscle/mcp/data_pack.hpp>
#include <libmuscle/namespace.hpp>
#include <libmuscle/util.hpp>
#include <ymmsl/ymmsl.hpp>

#include <utility>


using libmuscle::_MUSCLE_IMPL_NS::Data;
using libmuscle::_MUSCLE_IMPL_NS::IterationCount;
using libmuscle::_MUSCLE_IMPL_NS::MPPMessage;
using ymmsl::Reference;


int main(int argc, char *argv[]) {
    ::testing::InitGoogleTest(&argc, argv);
    return RUN_ALL_TESTS();
}

TEST(test_mcp_message, create_mcp_message) {
    Data test("test");
    Data abc("abc");

    MPPMessage m(
            Reference("sender.port"), Reference("receiver.port"),
            10,
            100.1, 101.0,
            test, 0, abc, {}
            );

    ASSERT_EQ(m.sender, "sender.port");
    ASSERT_EQ(m.receiver, "receiver.port");
    ASSERT_EQ(m.port_length, 10);
    ASSERT_EQ(m.timestamp, 100.1);
    ASSERT_EQ(m.next_timestamp, 101.0);
    ASSERT_EQ(m.settings_overlay.as<std::string>(), "test");
    ASSERT_EQ(m.message_number, 0);
    ASSERT_EQ(m.data.as<std::string>(), "abc");
}

TEST(test_mcp_message, create_mcp_message_minimal) {
    Data test, abc;

    MPPMessage m(
            Reference("sender.port"), Reference("receiver.port"),
            {},
            100.1, {},
            test, 0, abc, {}
            );

    ASSERT_EQ(m.sender, "sender.port");
    ASSERT_EQ(m.receiver, "receiver.port");
    ASSERT_FALSE(m.port_length.is_set());
    ASSERT_EQ(m.timestamp, 100.1);
    ASSERT_FALSE(m.next_timestamp.is_set());
    ASSERT_TRUE(m.settings_overlay.is_nil());
    ASSERT_EQ(m.message_number, 0);
    ASSERT_TRUE(m.data.is_nil());
}

TEST(test_mcp_message, from_bytes) {
    Data msg_dict = Data::dict(
            "sender", "sender.port",
            "receiver", "receiver.port",
            "port_length", Data(),
            "timestamp", 100.1,
            "next_timestamp", Data(),
            "settings_overlay", Data(),
            "message_number", 0,
            "data", Data(),
            "iteration", Data::list()
            );

    msgpack::sbuffer sbuf;
    msgpack::pack(sbuf, msg_dict);

    Data msg_bytes = Data::byte_array(sbuf.data(), sbuf.size());

    auto m = MPPMessage::from_bytes(msg_bytes);

    ASSERT_EQ(m.sender, "sender.port");
    ASSERT_EQ(m.receiver, "receiver.port");
    ASSERT_FALSE(m.port_length.is_set());
    ASSERT_EQ(m.timestamp, 100.1);
    ASSERT_FALSE(m.next_timestamp.is_set());
    ASSERT_TRUE(m.settings_overlay.is_nil());
    ASSERT_EQ(m.message_number, 0);
    ASSERT_TRUE(m.data.is_nil());
}

TEST(test_mcp_message, iteration_roundtrip) {
    Data settings, data(42);

    MPPMessage m(
            Reference("sender.port"), Reference("receiver.port"),
            {},
            0.0, {},
            settings, 0, data,
            IterationCount({0, 2})
            );

    auto m_out = MPPMessage::from_bytes(m.encoded());
    ASSERT_EQ(m_out.iteration.get(), IterationCount({0, 2}));
}
