#include "libmuscle/outbox.hpp"

#include <memory>

#include <gtest/gtest.h>

#include <libmuscle/util.hpp>
#include <libmuscle/data.hpp>
#include <libmuscle/mpp_message.hpp>
#include <ymmsl/ymmsl.hpp>


using libmuscle::_MUSCLE_IMPL_NS::DataConstRef;
using libmuscle::_MUSCLE_IMPL_NS::Optional;
using libmuscle::_MUSCLE_IMPL_NS::Outbox;
using libmuscle::_MUSCLE_IMPL_NS::MPPMessage;
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
            0, 1.0,
            DataConstRef("testing"));

    auto message_data = std::make_unique<DataConstRef>(message.encoded());

    auto msg_ptr = message_data.get();

    box.deposit(std::move(message_data));
    ASSERT_FALSE(box.is_empty());

    auto message2 = box.retrieve();
    ASSERT_TRUE(box.is_empty());
    ASSERT_EQ(message2.get(), msg_ptr);
}

