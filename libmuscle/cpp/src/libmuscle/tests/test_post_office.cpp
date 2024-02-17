#include "libmuscle/post_office.hpp"

#include <memory>
#include <thread>
#include <vector>
#include <unistd.h>
#include <fcntl.h>

#include <gtest/gtest.h>

#include <libmuscle/util.hpp>
#include <libmuscle/data.hpp>
#include <libmuscle/mcp/data_pack.hpp>
#include <libmuscle/mcp/protocol.hpp>
#include <libmuscle/mpp_message.hpp>
#include <libmuscle/namespace.hpp>
#include <ymmsl/ymmsl.hpp>


using libmuscle::_MUSCLE_IMPL_NS::Data;
using libmuscle::_MUSCLE_IMPL_NS::DataConstRef;
using libmuscle::_MUSCLE_IMPL_NS::Optional;
using libmuscle::_MUSCLE_IMPL_NS::Outbox;
using libmuscle::_MUSCLE_IMPL_NS::PostOffice;
using libmuscle::_MUSCLE_IMPL_NS::RequestType;
using libmuscle::_MUSCLE_IMPL_NS::MPPMessage;
using ymmsl::Reference;


int main(int argc, char *argv[]) {
    ::testing::InitGoogleTest(&argc, argv);
    return RUN_ALL_TESTS();
}

std::vector<char> make_message() {
    MPPMessage msg(
            "test_sender.port", "test_receiver.port",
            Optional<int>(),
            0.0, 1.0,
            DataConstRef(), 0, 5.0, DataConstRef());
    return msg.encoded();
}

std::unique_ptr<msgpack::sbuffer> make_request(std::string const & receiver) {
    auto request = Data::list(
            static_cast<int>(RequestType::get_next_message),
            receiver);
    auto sbuf = std::make_unique<msgpack::sbuffer>();
    msgpack::pack(*sbuf, request);
    return sbuf;
}

TEST(libmuscle_post_office, test_deposit_get_message) {
    PostOffice po;
    auto msg = make_message();
    auto msg_addr = msg.data();
    po.deposit("test_receiver.port", std::move(msg));

    auto request = make_request("test_receiver.port");
    std::vector<char> msg2;
    int fd = po.handle_request(request->data(), request->size(), msg2);
    ASSERT_EQ(fd, -1);
    ASSERT_EQ(msg2.data(), msg_addr);
}


TEST(libmuscle_post_office, test_individual_slots) {
    PostOffice po;
    auto msg1 = make_message();
    auto msg1_addr = msg1.data();
    po.deposit("test_receiver1.port", std::move(msg1));
    auto msg2 = make_message();
    auto msg2_addr = msg2.data();
    po.deposit("test_receiver2.port", std::move(msg2));

    auto request1 = make_request("test_receiver1.port");
    auto request2 = make_request("test_receiver2.port");
    po.handle_request(request1->data(), request1->size(), msg1);
    po.handle_request(request2->data(), request2->size(), msg2);
    ASSERT_EQ(msg1.data(), msg1_addr);
    ASSERT_EQ(msg2.data(), msg2_addr);
}


TEST(libmuscle_post_office, test_get_before_deposit) {
    PostOffice po;

    auto request = make_request("test_receiver.port");
    std::vector<char> msg_out;
    int fd = po.handle_request(request->data(), request->size(), msg_out);
    ASSERT_NE(fd, -1);
    ASSERT_TRUE(msg_out.empty());

    auto msg = make_message();
    auto msg_addr = msg.data();
    po.deposit("test_receiver.port", std::move(msg));

    int flags = fcntl(fd, F_GETFL, 0);
    fcntl(fd, F_SETFL, flags | O_NONBLOCK);
    std::vector<char> buf(10);
    ssize_t num_read = read(fd, buf.data(), buf.size());
    perror("Read error");
    ASSERT_EQ(num_read, 1);

    auto response = po.get_response(fd);
    ASSERT_EQ(response.data(), msg_addr);
}


void get_messages(
        PostOffice * po,
        std::string receiver,
        std::vector<char*> const & expected)
{
    auto request = make_request(receiver);
    for (int i = 0; i < 10; ++i) {
        std::vector<char> msg;
        int fd = po->handle_request(request->data(), request->size(), msg);
        ASSERT_EQ(fd, -1);
        ASSERT_EQ(msg.data(), expected[i]);
        std::this_thread::sleep_for(std::chrono::milliseconds(10));
    }
}


TEST(libmuscle_post_office, test_wait_for_receivers) {
    PostOffice po;
    std::vector<char*> expected1, expected2;
    for (int i = 0; i < 10; ++i) {
        auto msg1 = make_message();
        expected1.push_back(msg1.data());
        po.deposit("test_receiver1.port", std::move(msg1));
        auto msg2 = make_message();
        expected2.push_back(msg2.data());
        po.deposit("test_receiver2.port", std::move(msg2));
    }

    std::thread thread1(get_messages, &po, "test_receiver1.port", expected1);
    std::thread thread2(get_messages, &po, "test_receiver2.port", expected2);
    po.wait_for_receivers();
    thread1.join();
    thread2.join();
}

