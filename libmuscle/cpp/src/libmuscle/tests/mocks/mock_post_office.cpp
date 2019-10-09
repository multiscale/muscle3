#include <mocks/mock_post_office.hpp>

namespace libmuscle { namespace impl {

bool MockPostOffice::has_message(ymmsl::Reference const & receiver) {
    return false;
}

std::unique_ptr<mcp::Message> MockPostOffice::get_message(
        ymmsl::Reference const & receiver) {
    return std::make_unique<mcp::Message>(
            "test.out", "test2.in", 0, 0.0, 1.0, Data(), Data());
}

void MockPostOffice::deposit(
        ymmsl::Reference const & receiver,
        std::unique_ptr<mcp::Message> message) {
    last_receiver = receiver;
    last_message = std::move(message);
}

void MockPostOffice::wait_for_receivers() const {

}

void MockPostOffice::reset() {
    last_receiver = "_none";
    last_message.reset();
}

Reference MockPostOffice::last_receiver("_none");
std::unique_ptr<mcp::Message> MockPostOffice::last_message;

} }

