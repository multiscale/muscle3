#include <mocks/mock_post_office.hpp>

namespace libmuscle { namespace impl {

int MockPostOffice::handle_request(
        char const * res_buf, std::size_t res_len,
        std::unique_ptr<DataConstRef> & response) {
    response = std::make_unique<DataConstRef>(
            MPPMessage("test.out", "test2.in", 0, 0.0, 1.0, Data(), 0, Data()).encoded());
    return -1;
}

std::unique_ptr<DataConstRef> MockPostOffice::get_response(int fd) {
    return std::make_unique<DataConstRef>(
            MPPMessage("test.out", "test2.in", 0, 0.0, 1.0, Data(), 0, Data()).encoded());
}

void MockPostOffice::deposit(
        ymmsl::Reference const & receiver,
        std::unique_ptr<DataConstRef> message) {
    last_receiver = receiver;
    last_message = std::make_unique<MPPMessage>(MPPMessage::from_bytes(*message));
}

void MockPostOffice::wait_for_receivers() const {

}

void MockPostOffice::reset() {
    last_receiver = "_none";
    last_message.reset();
}

Reference MockPostOffice::last_receiver("_none");
std::unique_ptr<MPPMessage> MockPostOffice::last_message;

} }

