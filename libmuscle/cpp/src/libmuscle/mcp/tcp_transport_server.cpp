#include "libmuscle/mcp/tcp_transport_server.hpp"

#include "libmuscle/data.hpp"
#include "libmuscle/logger.hpp"
#include "libmuscle/mcp/transport_server.hpp"
#include "libmuscle/mcp/tcp_util.hpp"

#include <arpa/inet.h>
#include <chrono>
#include <condition_variable>
#include <cstring>
#include <ifaddrs.h>
#include <limits>
#include <memory>
#include <mutex>
#include <netinet/tcp.h>
#include <poll.h>
#include <thread>
#include <unistd.h>
#include <unordered_map>
#include <sys/types.h>
#include <sys/socket.h>


using namespace std::string_literals;

using libmuscle::_MUSCLE_IMPL_NS::DataConstRef;
using libmuscle::_MUSCLE_IMPL_NS::log_warning;
using libmuscle::_MUSCLE_IMPL_NS::mcp::check_conn;
using libmuscle::_MUSCLE_IMPL_NS::mcp::Disconnect;
using libmuscle::_MUSCLE_IMPL_NS::mcp::recv_all;
using libmuscle::_MUSCLE_IMPL_NS::mcp::recv_int64;
using libmuscle::_MUSCLE_IMPL_NS::mcp::RequestHandler;
using libmuscle::_MUSCLE_IMPL_NS::mcp::RpcState;
using libmuscle::_MUSCLE_IMPL_NS::mcp::send_frame;


namespace {

/** A worker that handles MCP-over-TCP connections.
 *
 * This class contains a list of connections and a thread that handles them (the worker
 * thread). Operations are synchronised internally, so it's thread-safe. It forwards the
 * requests to a RequestHandler.
 */
class TcpTransportServerWorker {
    public:
        /** Create a TcpTransportServerWorker.
         *
         * @param handler The RequestHandler to delegate requests to
         */
        explicit TcpTransportServerWorker(RequestHandler & handler)
            : handler_(handler)
            , mutex_()
            , new_connections_()
            , num_active_connections_(0)
            , shutting_down_(false)
            , connections_()
            , polled_fds_()
            , req_buf_()
            , thread_(worker_thread_, this)
        {}

        /** Return the number of connections handled by this worker.
         *
         * Called by the server thread to get information for load balancing.
         *
         * @returns The number of active connections.
         */
        int count_active_connections() const {
            std::lock_guard<std::mutex> lock(mutex_);
            return num_active_connections_;
        }

        /** Add a new active connection to handle.
         *
         * Called by the server thread when a client connects.
         *
         * @param fd The file descriptor of the socket to communicate on.
         */
        void add_connection(int fd, std::shared_ptr<RpcState> const & rpc_state) {
            std::lock_guard<std::mutex> lock(mutex_);
            new_connections_.emplace_back(fd, rpc_state);
        }

        /** Shut down this worker.
         *
         * This will cause the worker to wait for all clients to disconnect, then shut
         * down. This call will block until the worker has shut down.
         *
         * Called by the server thread on shut down.
         */
        void shutdown() {
            {
                std::lock_guard<std::mutex> lock(mutex_);
                shutting_down_ = true;
            }
            thread_.join();
        }

    private:
        /* Copies the list of managed connections into a poll_fd structure.
         *
         * Having a copy allows the server thread to add connections while the worker is
         * handling requests.
         *
         * This readies the polled_fds_ member for calling poll(), and the next_actions_
         * member for subsequent handling. After this is called, polled_fds_
         * corresponds index-wise to connections_.
         *
         * Called by the worker thread.
         */
        void update_connections_() {
            remove_closed_connections_();

            {
                std::lock_guard<std::mutex> lock(mutex_);

                connections_.insert(
                        connections_.end(), new_connections_.begin(), new_connections_.end());
                new_connections_.clear();
                num_active_connections_ = connections_.size();
            }

            update_polled_fds_();
        }

        /* Detects sockets that have closed and removes those connections.
         *
         * This cleans up the internal administration when clients disconnect. It
         * invalidates polled_fds_.
         *
         * @return True iff any changes were made
         *
         * Called by the worker thread.
         */
        void remove_closed_connections_() {
            for (std::size_t i = connections_.size(); i > 0u; --i) {
                std::size_t j = i - 1;
                if (connections_[j].next_action == Action_::receive_request) {
                    auto const & polled_fd = polled_fds_[j];
                    if (polled_fd.revents & POLLHUP) {
                        ::close(connections_[j].request_fd);
                        connections_.erase(connections_.begin() + j);
                    }
                }
            }
        }

        /* Update the polled_fds_ vector from connections_.
         *
         * Called by the worker thread
         */
        void update_polled_fds_() {
            polled_fds_.resize(connections_.size());

            std::size_t i = 0;
            for (auto & conn: connections_) {
                switch (conn.next_action) {
                    case Action_::receive_request:
                        polled_fds_[i].fd = conn.request_fd;
                        break;
                    case Action_::receive_response:
                        polled_fds_[i].fd = conn.response_fd;
                        break;
                    case Action_::send_response:
                        // poll() ignores negative values
                        polled_fds_[i].fd = -1;
                        break;
                }

                polled_fds_[i].events = POLLIN;
                polled_fds_[i].revents = 0;

                ++i;
            }
        }

        /* Checks which fds are ready, and handles requests and responses.
         *
         * This takes the results from calling poll(), answers any requests that can be
         * answered immediately, requests responses on the rest, and when responses are
         * available, gets them and sends them to the requester.
         *
         * Called by the worker thread.
         */
        void handle_ready_fds_() {
            for (std::size_t i = 0; i < polled_fds_.size(); ++i) {
                try {
                    if (polled_fds_[i].revents & POLLIN) {
                        if (connections_[i].next_action == Action_::receive_request)
                            handle_request_(i);
                        else
                            handle_response_(i);
                    }
                }
                catch (Disconnect const & e) {
                    polled_fds_[i].revents |= POLLHUP;
                }
            }
        }

        /* Receive a newly available request, and process and send as needed.
         *
         * @param i Index of the current connection
         */
        void handle_request_(std::size_t i) {
            auto & conn = connections_[i];
            int64_t request_nr = receive_request_(conn.request_fd);

            bool should_process, should_send;
            std::tie(should_process, should_send) = conn.rpc_state->triage_request(request_nr);

            if (should_process) {
                std::shared_ptr<std::vector<char>> res_buf = std::make_shared<std::vector<char>>();
                int res_fd = handler_.handle_request(req_buf_.data(), req_buf_.size(), *res_buf);

                if (res_fd < 0) {
                    // got a response immediately, share it
                    conn.rpc_state->set_response(res_buf);
                }
                else {
                    // response not yet available, pick it up on the next poll
                    conn.response_fd = res_fd;
                    conn.next_action = Action_::receive_response;
                    return;
                }
            }

            if (should_send) {
                conn.next_action = Action_::send_response;
            }
        }

        /* Receive the next request and return the request number.
         *
         * The request is received into req_buf_, which is reused as an optimisation.
         *
         * @param fd The socket fd to receive on
         */
        int64_t receive_request_(int fd) {
            int64_t request_nr = recv_int64(fd);
            int64_t length = recv_int64(fd);
            req_buf_.resize(length);
            recv_all(fd, req_buf_.data(), length);
            return request_nr;
        }

        /* Get a newly available response, and share it.
         *
         * @param i Index of the current connection
         */
        void handle_response_(std::size_t i) {
            auto & conn = connections_[i];

            char dummy;
            check_conn(read(conn.response_fd, &dummy, 1));

            std::shared_ptr<std::vector<char>> res_buf = std::make_shared<std::vector<char>>();
            *res_buf = handler_.get_response(conn.response_fd);

            conn.rpc_state->set_response(res_buf);

            conn.next_action = Action_::send_response;
            conn.response_fd = -1;
        }

        void send_responses_() {
            for (std::size_t i = 0; i < connections_.size(); ++i) {
                auto & conn = connections_[i];
                if (conn.next_action == Action_::send_response) {
                    auto response_to_send = conn.rpc_state->get_response();
                    if (response_to_send) {
                        conn.next_action = Action_::receive_request;

                        try {
                            send_frame(conn.request_fd, response_to_send->data(), response_to_send->size());
                        }
                        catch (Disconnect const & e) {
                            polled_fds_[i].revents |= POLLHUP;
                        }
                    }
                }
            }
        }

        /* The main function for the worker thread.
         *
         * This is static since I'm not sure if std::thread works with a thiscall.
         * Probably with some adaptor, but this works too.
         *
         * This runs in a loop until shutdown() is called by the server thread.
         *
         * @param self The TcpTransportServerWorker this thread belongs to.
         */
        static void worker_thread_(TcpTransportServerWorker * self) {
            while (true) {
                self->update_connections_();
                if (!self->polled_fds_.empty()) {
                    poll(self->polled_fds_.data(), self->polled_fds_.size(), 100);
                    self->handle_ready_fds_();
                    self->send_responses_();
                }
                else {
                    // Avoid blocking the CPU while waiting for clients to
                    // connect.
                    std::this_thread::sleep_for(std::chrono::milliseconds(100));
                }
                {
                    std::lock_guard<std::mutex> lock(self->mutex_);
                    if (self->connections_.empty() && self->shutting_down_)
                        break;
                }
            }
        }

        /* Next action needed for a given connection.
         */
        enum class Action_ {
            // receive the next request from the client
            receive_request,
            // receive the response from the handler and share it
            receive_response,
            // get the shared response and send it to the client
            send_response
        };

        /* Data associated with a TCP network connection.
         *
         * The request_fd is always the fd of the socket to the client.
         *
         * If next_action is receive_request or send_response, then response_fd is -1.
         *
         * If next_action is receive_response, then response_fd is the fd of the pipe
         * from the handler signalling that a response is available.
         */
        struct Connection_ {
            // State of the session
            std::shared_ptr<RpcState> rpc_state;
            // State of the connection
            Action_ next_action;
            // File descriptor of the socket connecting us to the client
            int request_fd;
            // File descriptor signalling that a response is available
            int response_fd;

            Connection_(int request_fd, std::shared_ptr<RpcState> const & rpc_state)
                : rpc_state(rpc_state)
                , next_action(Action_::receive_request)
                , request_fd(request_fd)
                , response_fd(-1)
            {}
        };

        RequestHandler & handler_;

        // the mutex protects the following three member variables
        mutable std::mutex mutex_;
        std::vector<Connection_> new_connections_;
        std::size_t num_active_connections_;
        bool shutting_down_;

        std::vector<Connection_> connections_;

        std::vector<pollfd> polled_fds_;
        mutable std::vector<char> req_buf_;

        // This needs to be after mutex_, which needs to be initialised before the
        // thread is started.
        std::thread thread_;
};

}


namespace libmuscle { namespace _MUSCLE_IMPL_NS { namespace mcp {


TcpTransportServer::TcpTransportServer(RequestHandler & handler)
    : TransportServerBase(handler)
    , next_session_(1)
{
    throw_on_error(pipe(control_pipe_));
    thread_ = std::thread(server_thread_, this);
}

TcpTransportServer::~TcpTransportServer() {
    if (thread_.joinable())
        close();
}

std::string TcpTransportServer::get_location() const {
    std::unique_lock<std::mutex> lock(mutex_);
    while (location_.empty())
        location_set_.wait(lock);
    return location_;
}

void TcpTransportServer::close() {
    char dummy = 0;
    throw_on_error(::write(control_pipe_[1], &dummy, 1));
    thread_.join();
}

std::vector<std::string> TcpTransportServer::get_interfaces_() const {
    std::vector<std::string> addresses;
    ifaddrs * interfaces;
    int err_code = 0;
    if ((err_code = getifaddrs(&interfaces)) != 0)
        throw std::runtime_error("Error enumerating network interfaces");

    for (ifaddrs * p = interfaces; p != nullptr; p = p->ifa_next) {
        auto addr = reinterpret_cast<sockaddr_in *>(p->ifa_addr);
        if (addr) {
            int family = addr->sin_family;
            if ((family == AF_INET) || (family == AF_INET6)) {
                char addr_buf[INET6_ADDRSTRLEN];
                inet_ntop(family, &(addr->sin_addr), addr_buf, INET6_ADDRSTRLEN);
                std::string addr_str(addr_buf);
                if (addr_str.rfind("127.", 0) == 0)
                    continue;
                if (addr_str == "[::1]")
                    continue;
                addresses.push_back(std::move(addr_str));
            }
        }
    }
    freeifaddrs(interfaces);
    return addresses;
}

int TcpTransportServer::create_socket_() const {
    const int backlog = 10;
    int sockfd;
    int reuse = 1;

    // try dual IPv6/IPv4
    if ((sockfd = socket(AF_INET6, SOCK_STREAM, 0)) != -1) {
        setsockopt(
                sockfd, SOL_SOCKET, SO_REUSEADDR,
                reinterpret_cast<char*>(&reuse), sizeof(reuse));

        struct sockaddr_in6 addr;
        memset(&addr, 0, sizeof(addr));
        addr.sin6_family = AF_INET6;
        addr.sin6_addr = in6addr_any;
        addr.sin6_port = htons(0);

        int err = 0;
        if ((err = bind(sockfd, reinterpret_cast<sockaddr*>(&addr), sizeof(addr))) == -1) {
            ::close(sockfd);
            throw std::runtime_error("Failed to bind TCP6 socket");
        }

        if ((err = listen(sockfd, backlog)) == -1)
            throw std::runtime_error("Failed to listen on TCP6 socket");
    }
    else {
        // IPv4 only
        if ((sockfd = socket(AF_INET, SOCK_STREAM, 0)) == -1)
            throw std::runtime_error("Failed to create TCP socket");

        setsockopt(
                sockfd, SOL_SOCKET, SO_REUSEADDR,
                reinterpret_cast<char*>(&reuse), sizeof(reuse));

        struct sockaddr_in addr;
        memset(&addr, 0, sizeof(addr));
        addr.sin_family = AF_INET;
        addr.sin_addr.s_addr = INADDR_ANY;
        addr.sin_port = htons(0);

        int err = 0;
        if ((err = bind(sockfd, reinterpret_cast<sockaddr*>(&addr), sizeof(addr))) == -1) {
            ::close(sockfd);
            throw std::runtime_error("Failed to bind TCP4 socket");
        }

        if ((err = listen(sockfd, backlog)) == -1)
            throw std::runtime_error("Failed to listen on TCP4 socket");
    }
    return sockfd;
}

std::string TcpTransportServer::get_port_string_(int sockfd) const {
    int port = -1;

    sockaddr_storage bound_addr;
    socklen_t addr_len = sizeof bound_addr;
    getsockname(sockfd, reinterpret_cast<sockaddr*>(&bound_addr), &addr_len);

    auto family = reinterpret_cast<sockaddr*>(&bound_addr)->sa_family;
    if (family == AF_INET) {
        auto ipv4_addr = reinterpret_cast<sockaddr_in*>(&bound_addr);
        port = ntohs(ipv4_addr->sin_port);
    }
    else if (family == AF_INET6) {
        auto ipv6_addr = reinterpret_cast<sockaddr_in6*>(&bound_addr);
        port = ntohs(ipv6_addr->sin6_port);
    }
    else
        throw std::runtime_error("Unknown address family");

    return std::to_string(port);
}

void TcpTransportServer::set_location_(std::string const & location) {
    std::lock_guard<std::mutex> lock(mutex_);
    location_ = location;
    location_set_.notify_all();
}

int TcpTransportServer::set_up_socket_() {
    int sockfd = create_socket_();

    std::string port = get_port_string_(sockfd);

    std::string addresses;
    for (auto const & interface: get_interfaces_()) {
        if (!addresses.empty())
            addresses += ",";
        addresses += interface + ":" + port;
    }

    set_location_("tcp:" + addresses);
    return sockfd;
}

std::tuple<int64_t, std::shared_ptr<RpcState>> TcpTransportServer::start_session_(int socket_fd) {
    std::shared_ptr<RpcState> rpc_state;

    int64_t req_session_id = recv_int64(socket_fd);

    int64_t session_id;
    if (req_session_id == 0) {
        session_id = next_session_++;
        rpc_state = std::make_shared<RpcState>();
        session_store_[session_id] = rpc_state;

        send_int64(socket_fd, session_id);
    }
    else {
        log_warning("The TCP network connection for session ", req_session_id, " was lost");
        if (session_store_.count(req_session_id) == 0) {
            throw std::runtime_error(
                    "Unknown session " + std::to_string(req_session_id) +
                    " requested");
        }
        session_id = req_session_id;

        rpc_state = session_store_[session_id];
        send_int64(socket_fd, session_id);
        log_warning("Resuming session ", session_id);
    }

    return std::make_tuple(session_id, rpc_state);
}

void TcpTransportServer::server_thread_(TcpTransportServer * self) {
    std::vector<std::unique_ptr<TcpTransportServerWorker>> workers;
    workers.emplace_back(new TcpTransportServerWorker(self->handler_));
    int socket_fd = self->set_up_socket_();

    while (true) {
        // poll on control pipe and socket
        std::vector<pollfd> poll_fds(2u);
        poll_fds[0].fd = self->control_pipe_[0];
        poll_fds[0].events = POLLIN;
        poll_fds[1].fd = socket_fd;
        poll_fds[1].events = POLLIN;

        poll(poll_fds.data(), poll_fds.size(), -1);

        if (poll_fds[0].revents & POLLIN) {
            char dummy;
            throw_on_error(read(poll_fds[0].fd, &dummy, 1));
            break;
        }

        // TODO: get peer info and log it
        if (poll_fds[1].revents & POLLIN) {
            int new_fd = -1;
            try {
                new_fd = check_conn(accept(poll_fds[1].fd, nullptr, nullptr));
                int flags = 0;
#ifdef __linux
                setsockopt(new_fd, SOL_TCP, TCP_NODELAY, &flags, sizeof(flags));
                setsockopt(new_fd, SOL_TCP, TCP_QUICKACK, &flags, sizeof(flags));
#elif __APPLE__
                setsockopt(new_fd, IPPROTO_TCP, TCP_NODELAY, &flags, sizeof(flags));
                // macOS doesn't have quickack unfortunately
#endif
                int64_t session_id;
                std::shared_ptr<RpcState> rpc_state;
                std::tie(session_id, rpc_state) = self->start_session_(new_fd);

                if (self->worker_for_session_.count(session_id) == 0) {
                    std::size_t selected_worker = 0u;
                    std::size_t min_size = std::numeric_limits<std::size_t>::max();
                    for (std::size_t j = 0u; j < workers.size(); ++j) {
                        std::size_t cur_size = workers[j]->count_active_connections();
                        if (cur_size < min_size) {
                            min_size = cur_size;
                            selected_worker = j;
                        }
                    }
                    self->worker_for_session_[session_id] = selected_worker;
                }

                std::size_t selected_worker = self->worker_for_session_[session_id];
                workers[selected_worker]->add_connection(new_fd, rpc_state);
            }
            catch (Disconnect const & e) {
                if (new_fd != -1) {
                    ::close(new_fd);
                }
            }
        }
    }

    ::close(socket_fd);

    for (auto & worker: workers)
        worker->shutdown();
}

} } }

