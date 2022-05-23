#include <libmuscle/outbox.hpp>
#include <libmuscle/util.hpp>

#include <mutex>

#include <unistd.h>


namespace libmuscle { namespace impl {

Outbox::Outbox()
    : notification_fd_(-1)
{}

std::unique_lock<std::mutex> Outbox::lock() {
    return std::unique_lock<std::mutex>(mutex_);
}

bool Outbox::is_empty() const {
    return queue_.empty();
}

void Outbox::deposit(std::unique_ptr<DataConstRef> message) {
    queue_.insert(queue_.begin(), std::move(message));
    if (queue_.size() == 1u && notification_fd_ != -1) {
        char dummy = '\0';
        write(notification_fd_, &dummy, 1);
    }
}

std::unique_ptr<DataConstRef> Outbox::retrieve() {
    if (queue_.empty())
        throw std::runtime_error("Trying to retrieve from an empty outbox");

    auto result = std::move(queue_.back());
    queue_.pop_back();
    return result;
}

void Outbox::set_notification_fd(int fd) {
    notification_fd_ = fd;
}

int Outbox::return_notification_fd() {
    int old_fd = notification_fd_;
    notification_fd_ = -1;
    return old_fd;
}

} }

