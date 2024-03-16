#include <libmuscle/post_office.hpp>

#include <libmuscle/mcp/data_pack.hpp>
#include <libmuscle/mcp/protocol.hpp>

#include <chrono>
#include <memory>
#include <thread>
#include <unistd.h>
#include <vector>

#include <msgpack.hpp>


using ymmsl::Reference;


namespace libmuscle { namespace _MUSCLE_IMPL_NS {

Pipe::Pipe() {
    int pipe_fds[2];
    int err = pipe(pipe_fds);
    if (err != 0)
        throw std::runtime_error("Error creating pipe");

    sending_fd = pipe_fds[1];
    receiving_fd = pipe_fds[0];
}

Pipe::Pipe(int sending_fd, int receiving_fd)
    : sending_fd(sending_fd)
    , receiving_fd(receiving_fd)
{}

void Pipe::close() {
    ::close(sending_fd);
    ::close(receiving_fd);
}


PostOffice::~PostOffice() {
    for (auto & pipe : pipes_)
        pipe.close();
}

int PostOffice::handle_request(
        char const * req_buf, std::size_t req_len,
        std::vector<char> & res_buf
) {
    auto zone = std::make_shared<msgpack::zone>();
    auto request = mcp::unpack_data(zone, req_buf, req_len);
    if (
            !request.is_a_list() || request.size() != 2 ||
            (request[0].as<int>() != static_cast<int>(RequestType::get_next_message)))
        throw std::runtime_error(
                "Invalid request type. Did the streams get crossed?");

    Reference receiver(request[1].as<std::string>());
    auto & outbox = get_outbox_(receiver);

    auto lock = outbox.lock();
    if (!outbox.is_empty()) {
        res_buf = outbox.retrieve();
        retrieved_.notify_one();
        return -1;
    }
    else {
        auto pipe = get_pipe_();
        outbox.set_notification_fd(pipe.sending_fd);
        pending_outboxes_[pipe.receiving_fd] = &outbox;
        return pipe.receiving_fd;
    }
}

std::vector<char> PostOffice::get_response(int fd) {
    Outbox * outbox = nullptr;
    {
        std::lock_guard<std::mutex> lock(outboxes_mutex_);
        auto outbox_it = pending_outboxes_.find(fd);
        outbox = outbox_it->second;
        pending_outboxes_.erase(outbox_it);
    }

    int sending_fd;
    std::vector<char> result;
    {
        auto lock = outbox->lock();
        sending_fd = outbox->return_notification_fd();
        result = outbox->retrieve();
    }

    return_pipe_(Pipe(sending_fd, fd));
    retrieved_.notify_one();
    return result;
}

void PostOffice::deposit(
        Reference const & receiver, std::vector<char> && message) {
    Outbox & outbox = get_outbox_(receiver);
    auto lock = outbox.lock();
    outbox.deposit(std::move(message));
}

void PostOffice::wait_for_receivers() const {
    std::unique_lock<std::mutex> lock(outboxes_mutex_);
    while (true) {
        bool done = true;
        for (auto const & ref_outbox : outboxes_) {
            auto & outbox = ref_outbox.second;
            {
                auto outbox_lock = outbox->lock();
                done &= outbox->is_empty();
            }
        }
        if (done) break;
        retrieved_.wait(lock);
    }
}

Outbox & PostOffice::get_outbox_(Reference const & receiver) {
    std::unique_lock<std::mutex> lock(outboxes_mutex_);
    if (outboxes_.count(receiver) == 0)
        outboxes_.emplace(receiver, std::make_unique<Outbox>());
    return *outboxes_[receiver].get();
}

Pipe PostOffice::get_pipe_() {
    std::lock_guard<std::mutex> lock(pipes_mutex_);
    if (pipes_.empty())
        return Pipe();
    else {
        Pipe result(pipes_.back());
        pipes_.pop_back();
        return result;
    }
}

void PostOffice::return_pipe_(Pipe const & pipe) {
    std::lock_guard<std::mutex> lock(pipes_mutex_);
    pipes_.push_back(pipe);
}

} }

