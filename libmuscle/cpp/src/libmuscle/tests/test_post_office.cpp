#include "libmuscle/post_office.hpp"

#include <memory>
#include <thread>
#include <vector>

#include <gtest/gtest.h>

#include "libmuscle/util.hpp"
#include "libmuscle/mcp/data.hpp"
#include "libmuscle/mcp/message.hpp"
#include <ymmsl/identity.hpp>


using libmuscle::mcp::DataConstRef;
using libmuscle::Optional;
using libmuscle::Outbox;
using libmuscle::PostOffice;
using libmuscle::mcp::Message;
using ymmsl::Reference;


int main(int argc, char *argv[]) {
    ::testing::InitGoogleTest(&argc, argv);
    return RUN_ALL_TESTS();
}

std::unique_ptr<Message> make_message() {
    return std::make_unique<Message>(
            "test_sender.port", "test_receiver.port",
            Optional<int>(),
            0.0, 1.0,
            DataConstRef(), DataConstRef());
}

TEST(libmuscle_post_office, test_deposit_get_message) {
    PostOffice po;
    auto msg = make_message();
    auto msg_addr = msg.get();
    po.deposit("test_receiver.port", std::move(msg));
    auto msg2 = po.get_message("test_receiver.port");
    ASSERT_EQ(msg2.get(), msg_addr);
}


TEST(libmuscle_post_office, test_individual_slots) {
    PostOffice po;
    auto msg1 = make_message();
    auto msg1_addr = msg1.get();
    po.deposit("test_receiver1.port", std::move(msg1));
    auto msg2 = make_message();
    auto msg2_addr = msg2.get();
    po.deposit("test_receiver2.port", std::move(msg2));

    msg1 = po.get_message("test_receiver1.port");
    msg2 = po.get_message("test_receiver2.port");
    ASSERT_EQ(msg1.get(), msg1_addr);
    ASSERT_EQ(msg2.get(), msg2_addr);
}


void get_message(PostOffice * po) {
    auto msg = po->get_message("test_receiver.port");
    ASSERT_EQ(msg->sender, "test_sender.port");
}


TEST(libmuscle_post_office, test_get_before_deposit) {
    PostOffice po;
    auto msg = make_message();
    std::thread thread(get_message, &po);
    std::this_thread::sleep_for(std::chrono::milliseconds(50));
    po.deposit("test_receiver.port", std::move(msg));
    thread.join();
}


void get_messages(
        PostOffice * po,
        std::string receiver,
        std::vector<Message*> const & expected)
{
    for (int i = 0; i < 10; ++i) {
        auto msg = po->get_message(receiver);
        ASSERT_EQ(msg.get(), expected[i]);
        std::this_thread::sleep_for(std::chrono::milliseconds(10));
    }
}


TEST(libmuscle_post_office, test_wait_for_receivers) {
    PostOffice po;
    std::vector<Message*> expected1, expected2;
    for (int i = 0; i < 10; ++i) {
        auto msg1 = make_message();
        expected1.push_back(msg1.get());
        po.deposit("test_receiver1.port", std::move(msg1));
        auto msg2 = make_message();
        expected2.push_back(msg2.get());
        po.deposit("test_receiver2.port", std::move(msg2));
    }

    std::thread thread1(get_messages, &po, "test_receiver1.port", expected1);
    std::thread thread2(get_messages, &po, "test_receiver2.port", expected2);
    po.wait_for_receivers();
    thread1.join();
    thread2.join();
}

