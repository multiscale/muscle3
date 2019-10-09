#include <libmuscle/outbox.hpp>
#include <libmuscle/util.hpp>

#include <mutex>


namespace libmuscle { namespace impl {

bool Outbox::is_empty() const {
    std::unique_lock<std::mutex> lock(mutex_);
    return queue_.empty();
}

void Outbox::deposit(std::unique_ptr<mcp::Message> message) {
    {
        std::unique_lock<std::mutex> lock(mutex_);
        queue_.insert(queue_.begin(), std::move(message));
    }
    deposited_.notify_one();
}

std::unique_ptr<mcp::Message> Outbox::retrieve() {
    std::unique_lock<std::mutex> lock(mutex_);
    while (queue_.empty())
        deposited_.wait(lock);
    auto result = std::move(queue_.back());
    queue_.pop_back();
    return result;
}

} }

