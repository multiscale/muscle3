#include "libmuscle/mcp/tcp_transport_server.hpp"

#include "libmuscle/data.hpp"
#include "libmuscle/mcp/transport_server.hpp"
#include "libmuscle/mcp/tcp_util.hpp"

#include <arpa/inet.h>
#include <chrono>
#include <cstring>
#include <ifaddrs.h>
#include <netinet/tcp.h>
#include <poll.h>
#include <thread>
#include <unistd.h>
#include <unordered_map>
#include <sys/types.h>
#include <sys/socket.h>


using namespace std::string_literals;

using libmuscle::impl::DataConstRef;
using libmuscle::impl::mcp::recv_all;
using libmuscle::impl::mcp::send_frame;
using libmuscle::impl::mcp::recv_int64;
using libmuscle::impl::mcp::RequestHandler;


namespace {

/** A worker that handles MCP-over-TCP connections.
 *
 * This class contains a list of connections and a thread that handles them
 * (the worker thread). Operations are synchronised internally, so it's
 * thread-safe. It forwards the requests to a RequestHandler.
 */
class TcpTransportServerWorker {
    public:
        /** Create a TcpTransportServerWorker.
         *
         * @param handler The RequestHandler to delegate requests to
         */
        explicit TcpTransportServerWorker(RequestHandler & handler)
            : handler_(handler)
            , shutting_down_(false)
            , connections_()
            , connections_changed_(false)
            , polled_fds_()
            , polled_fd_types_()
            , mutex_()
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
            return connections_.size();
        }

        /** Add a new active connection to handle.
         *
         * Called by the server thread when a client connects.
         *
         * @param fd The file descriptor of the socket to communicate on.
         */
        void add_connection(int fd) {
            std::lock_guard<std::mutex> lock(mutex_);
            connections_.push_back(fd);
            connections_changed_ = true;
        }

        /** Shut down this worker.
         *
         * This will cause the worker to wait for all clients to disconnect,
         * then shut down. This call will block until the worker has shut
         * down.
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
         * Having a copy allows the server thread to add connections while the
         * worker is handling requests.
         *
         * This readies the polled_fds_ member for calling poll(), and the
         * polled_fd_types_ member for subsequent handling. After this is
         * called, polled_fds_ and polled_fd_types_ correspond index-wise to
         * connections_.
         *
         * Called by the worker thread.
         */
        void update_polled_fds_() {
            std::lock_guard<std::mutex> lock(mutex_);
            if (connections_changed_) {
                polled_fds_.resize(connections_.size());
                polled_fd_types_.resize(connections_.size());
                std::size_t i = 0;
                for (auto & conn: connections_) {
                    if (conn.response_fd != -1) {
                        polled_fds_[i].fd = conn.response_fd;
                        polled_fd_types_[i] = FdType_::response;
                    }
                    else {
                        polled_fds_[i].fd = conn.request_fd;
                        polled_fd_types_[i] = FdType_::request;
                    }
                    polled_fds_[i].events = POLLIN;
                    polled_fds_[i].revents = 0;
                    ++i;
                }
                connections_changed_ = false;
            }
        }

        /* Checks which fds are ready, and handles requests and responses.
         *
         * This takes the results from calling poll(), answers any requests
         * that can be answered immediately, waits for the responses on the
         * rest, and when responses are available, gets them and sends them
         * to the requester.
         *
         * Called by the worker thread.
         */
        void handle_ready_fds_() {
            for (std::size_t i = 0; i < polled_fds_.size(); ++i) {
                auto & polled_fd = polled_fds_[i];
                if (polled_fd.revents & POLLIN) {
                    if (polled_fd_types_[i] == FdType_::request) {
                        try {
                            int64_t length = recv_int64(polled_fd.fd);
                            req_buf_.resize(length);
                            recv_all(polled_fd.fd, req_buf_.data(), length);

                            std::unique_ptr<DataConstRef> res_buf;
                            int res_fd = handler_.handle_request(req_buf_.data(), length, res_buf);
                            if (res_fd < 0) {
                                // got a response immediately, send it
                                send_response_(polled_fd.fd, std::move(res_buf));
                            }
                            else {
                                // response not yet available, wait for it
                                std::lock_guard<std::mutex> lock(mutex_);
                                connections_[i].response_fd = res_fd;
                                connections_changed_ = true;
                            }
                        }
                        catch (std::runtime_error const & e) {
                            // EOF; port was closed, mark as such
                            polled_fd.revents |= POLLHUP;
                        }
                    }
                    else {  // response ready
                        char dummy;
                        read(polled_fd.fd, &dummy, 1);

                        std::unique_ptr<DataConstRef> res_buf;
                        res_buf = handler_.get_response(polled_fd.fd);

                        int fd;
                        {
                            std::lock_guard<std::mutex> lock(mutex_);
                            fd = connections_[i].request_fd;
                            connections_[i].response_fd = -1;
                            connections_changed_ = true;
                        }
                        send_response_(fd, std::move(res_buf));
                    }
                }
            }
        }

        /* Send contents of response buffer to the given fd.
         *
         * This saves some duplication in the code above. Takes ownership of
         * res_buf and discards it after sending.
         *
         * @param fd The fd to send the data on
         */
        void send_response_(int fd, std::unique_ptr<DataConstRef> res_buf) {
            send_frame(fd, res_buf->as_byte_array(), res_buf->size());
        }

        /* Detects ports that have closed and removes those connections.
         *
         * This cleans up the internal administration when clients disconnect.
         * After this procedure has been called, connections_ and polled_fds_
         * no longer correspond one-on-one to each other.
         *
         * Called by the worker thread.
         */
        void remove_closed_ports_() {
            for (std::size_t i = polled_fds_.size(); i > 0u; --i) {
                std::size_t j = i - 1;
                if (polled_fd_types_[j] == FdType_::request) {
                    auto const & polled_fd = polled_fds_[j];
                    if (polled_fd.revents & POLLHUP) {
                        ::close(polled_fd.fd);
                        std::lock_guard<std::mutex> lock(mutex_);
                        connections_.erase(connections_.begin() + j);
                        connections_changed_ = true;
                    }
                }
            }
        }

        /* The main function for the worker thread.
         *
         * This is static since I'm not sure if std::thread works with a
         * thiscall. Probably with some adaptor, but this works too.
         *
         * This runs in a loop until shutdown() is called by the server
         * thread.
         *
         * @param self The TcpTransportServerWorker this thread belongs to.
         */
        static void worker_thread_(TcpTransportServerWorker * self) {
            while (true) {
                self->update_polled_fds_();
                if (!self->polled_fds_.empty()) {
                    poll(self->polled_fds_.data(), self->polled_fds_.size(), 100);
                    self->handle_ready_fds_();
                    self->remove_closed_ports_();
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

        struct Connection_ {
            int request_fd, response_fd;

            Connection_(int request_fd)
                : request_fd(request_fd)
                , response_fd(-1)
            {}
        };

        enum class FdType_ {
            request,
            response
        };

        RequestHandler & handler_;
        bool shutting_down_;
        std::vector<Connection_> connections_;
        bool connections_changed_;

        std::vector<pollfd> polled_fds_;
        std::vector<FdType_> polled_fd_types_;

        mutable std::vector<char> req_buf_;

        // mutex before thread, it needs to be initialised before the thread
        // is started.
        mutable std::mutex mutex_;
        std::thread thread_;
};

}


namespace libmuscle { namespace impl { namespace mcp {

TcpTransportServer::TcpTransportServer(RequestHandler & handler)
    : TransportServer(handler)
{
    pipe(control_pipe_);
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
    ::write(control_pipe_[1], &dummy, 1);
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

TcpTransportServer::AddrInfoList_ TcpTransportServer::get_address_info_(
        std::string const & address) const
{
    int err = 0;

    addrinfo hints;
    memset(&hints, 0, sizeof hints);
    hints.ai_family = AF_UNSPEC;
    hints.ai_socktype = SOCK_STREAM;
    hints.ai_flags = AI_PASSIVE;

    addrinfo *servinfo;
    if ((err = getaddrinfo(address.c_str(), "0", &hints, &servinfo)) != 0)
        throw std::runtime_error(
                "Could not get address information: "s
                + gai_strerror(err));

    return AddrInfoList_(servinfo, &freeaddrinfo);
}

std::vector<int> TcpTransportServer::create_sockets_(addrinfo const * addresses) const {
    // TODO: just listen on 0.0.0.0
    std::vector<int> result;
    for (addrinfo const *p = addresses; p != nullptr; p = p->ai_next) {
        int sockfd;
        if ((sockfd = socket(p->ai_family, p->ai_socktype, p->ai_protocol)) == -1)
            continue;

        int err = 0;
        if ((err = bind(sockfd, p->ai_addr, p->ai_addrlen)) == -1) {
            ::close(sockfd);
            continue;
        }

        const int backlog = 10;
        if ((err = listen(sockfd, backlog)) == -1)
            throw std::runtime_error("Failed to listen on TCP socket");

        result.push_back(sockfd);
    }
    return result;
}

std::string TcpTransportServer::get_address_string_(int sockfd) const {
    std::string location;

    sockaddr_storage bound_addr;
    socklen_t addr_len = sizeof bound_addr;
    getsockname(sockfd, reinterpret_cast<sockaddr*>(&bound_addr), &addr_len);

    char addr_buf[INET6_ADDRSTRLEN];

    auto family = reinterpret_cast<sockaddr*>(&bound_addr)->sa_family;
    if (family == AF_INET) {
        auto ipv4_addr = reinterpret_cast<sockaddr_in*>(&bound_addr);
        inet_ntop(AF_INET, &(ipv4_addr->sin_addr), addr_buf, INET6_ADDRSTRLEN);
        int port = ntohs(ipv4_addr->sin_port);
        location = std::string(addr_buf) + ":" + std::to_string(port);
    }
    else if (family == AF_INET6) {
        auto ipv6_addr = reinterpret_cast<sockaddr_in6*>(&bound_addr);
        inet_ntop(AF_INET6, &(ipv6_addr->sin6_addr), addr_buf, INET6_ADDRSTRLEN);
        int port = ntohs(ipv6_addr->sin6_port);
        location = "[" + std::string(addr_buf) + "]:" + std::to_string(port);
    }
    else
        throw std::runtime_error("Unknown address family");

    return location;
}

void TcpTransportServer::set_location_(std::string const & location) {
    std::lock_guard<std::mutex> lock(mutex_);
    location_ = location;
    location_set_.notify_all();
}

std::vector<int> TcpTransportServer::set_up_sockets_() {
    std::vector<int> all_fds;

    auto interfaces = get_interfaces_();
    for (auto const & interface: interfaces) {
        AddrInfoList_ addrinfos = get_address_info_(interface);
        auto fds = create_sockets_(addrinfos.get());
        all_fds.insert(all_fds.end(), fds.cbegin(), fds.cend());
    }

    std::string addresses;
    for (int fd : all_fds) {
        if (addresses.empty())
            addresses += get_address_string_(fd);
        else
            addresses += "," + get_address_string_(fd);
    }

    set_location_("tcp:" + addresses);
    return all_fds;
}

void TcpTransportServer::server_thread_(TcpTransportServer * self) {
    std::vector<std::unique_ptr<TcpTransportServerWorker>> workers;
    workers.emplace_back(new TcpTransportServerWorker(self->handler_));
    std::vector<int> socket_fds = self->set_up_sockets_();

    while (true) {
        // poll on control pipe and socket
        std::vector<pollfd> poll_fds(socket_fds.size() + 1u);
        poll_fds[0].fd = self->control_pipe_[0];
        poll_fds[0].events = POLLIN;

        std::size_t i = 1u;
        for (int socket_fd: socket_fds) {
            poll_fds[i].fd = socket_fd;
            poll_fds[i].events = POLLIN;
            ++i;
        }

        poll(poll_fds.data(), poll_fds.size(), -1);

        if (poll_fds[0].revents & POLLIN) {
            char dummy;
            read(poll_fds[0].fd, &dummy, 1);
            break;
        }

        // TODO: get peer info and log it
        for (std::size_t i = 1u; i < poll_fds.size(); ++i) {
            if (poll_fds[i].revents & POLLIN) {
                int new_fd = accept(poll_fds[i].fd, nullptr, nullptr);
                int flags;
                setsockopt(new_fd, SOL_TCP, TCP_NODELAY, &flags, sizeof(flags));
                setsockopt(new_fd, SOL_TCP, TCP_QUICKACK, &flags, sizeof(flags));

                // TODO: there's a trait<size_t>::max, isn't there?
                std::size_t min_size = static_cast<std::size_t>(-1);
                std::size_t selected_worker = 0u;
                for (std::size_t j = 0u; j < workers.size(); ++j) {
                    std::size_t cur_size = workers[j]->count_active_connections();
                    if (cur_size < min_size) {
                        min_size = cur_size;
                        selected_worker = j;
                    }
                }

                workers[selected_worker]->add_connection(new_fd);
            }
        }
    }

    for (int socket_fd: socket_fds)
        ::close(socket_fd);

    for (auto & worker: workers)
        worker->shutdown();
}

} } }

