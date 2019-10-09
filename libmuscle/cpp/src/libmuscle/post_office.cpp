#include <libmuscle/post_office.hpp>

#include <chrono>
#include <memory>
#include <thread>


using ymmsl::Reference;
using libmuscle::impl::mcp::Message;


namespace libmuscle { namespace impl {

bool PostOffice::has_message(Reference const & receiver) {
    return !get_outbox_(receiver).is_empty();
}

std::unique_ptr<Message> PostOffice::get_message(Reference const & receiver) {
    auto msg = get_outbox_(receiver).retrieve();
    retrieved_.notify_one();
    return std::move(msg);
}

void PostOffice::deposit(
        Reference const & receiver, std::unique_ptr<Message> message) {
    get_outbox_(receiver).deposit(std::move(message));
}

void PostOffice::wait_for_receivers() const {
    std::unique_lock<std::mutex> lock(outboxes_mutex_);
    for (auto const & ref_outbox : outboxes_)
        while (!ref_outbox.second->is_empty())
            retrieved_.wait(lock);
}

Outbox & PostOffice::get_outbox_(Reference const & receiver) {
    std::unique_lock<std::mutex> lock(outboxes_mutex_);
    if (outboxes_.count(receiver) == 0)
        outboxes_.emplace(receiver, std::make_unique<Outbox>());
    return *outboxes_[receiver].get();
}

} }

