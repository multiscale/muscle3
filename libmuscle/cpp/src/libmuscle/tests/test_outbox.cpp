#include "libmuscle/outbox.hpp"

#include <memory>

#include <gtest/gtest.h>

#include <libmuscle/util.hpp>
#include <libmuscle/data.hpp>
#include <libmuscle/mpp_message.hpp>
#include <ymmsl/ymmsl.hpp>


using libmuscle::impl::DataConstRef;
using libmuscle::impl::Optional;
using libmuscle::impl::Outbox;
using libmuscle::impl::MPPMessage;
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

    MPPMessage message(
            Reference("sender.out"), Reference("receiver.in"),
            Optional<int>(),
            0.0, 1.0,
            DataConstRef(),
            DataConstRef("testing"));

    auto message_data = std::make_unique<DataConstRef>(message.encoded());

    auto msg_ptr = message_data.get();

    box.deposit(std::move(message_data));
    ASSERT_FALSE(box.is_empty());

    auto message2 = box.retrieve();
    ASSERT_TRUE(box.is_empty());
    ASSERT_EQ(message2.get(), msg_ptr);
}

