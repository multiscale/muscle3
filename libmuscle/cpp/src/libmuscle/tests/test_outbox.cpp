#include "libmuscle/outbox.hpp"

#include <memory>

#include <gtest/gtest.h>

#include "libmuscle/util.hpp"
#include "libmuscle/mcp/data.hpp"
#include "libmuscle/mcp/message.hpp"
#include <ymmsl/identity.hpp>


using libmuscle::mcp::DataConstRef;
using libmuscle::Optional;
using libmuscle::Outbox;
using libmuscle::mcp::Message;
using ymmsl::Reference;


int main(int argc, char *argv[]) {
    ::testing::InitGoogleTest(&argc, argv);
    return RUN_ALL_TESTS();
}

TEST(libmuscle_outbox, test_create_outbox) {
    Outbox box;

    ASSERT_TRUE(box.is_empty());
}

TEST(libmuscle_outbox, test_deposit_retrieve_message) {
    Outbox box;

    auto message = std::make_unique<Message>(
            Reference("sender.out"), Reference("receiver.in"),
            Optional<int>(),
            0.0, 1.0,
            DataConstRef(),
            DataConstRef("testing"));

    auto msg_ptr = message.get();

    box.deposit(std::move(message));
    ASSERT_FALSE(box.is_empty());

    auto message2 = box.retrieve();
    ASSERT_TRUE(box.is_empty());
    ASSERT_EQ(message2.get(), msg_ptr);
}

