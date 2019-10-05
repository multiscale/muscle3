#include <libmuscle/mcp/tcp_server.hpp>

#include <libmuscle/data.hpp>
#include <libmuscle/mcp/data_pack.hpp>
#include <libmuscle/mcp/tcp_util.hpp>

#include <ifaddrs.h>
#include <poll.h>
#include <unistd.h>


using namespace std::string_literals;

using libmuscle::Data;
using libmuscle::PostOffice;
using libmuscle::mcp::recv_all;
using libmuscle::mcp::send_all;
using libmuscle::mcp::recv_int64;
using libmuscle::mcp::send_int64;

using ymmsl::Reference;


namespace {

/** A worker that handles requests for messages.
 *
 * This class contains a list of connections and a thread that handles them
 * (the worker thread). Operations are synchronised internally, so it's
 * thread-safe.
 */
class TcpServerWorker {
    public:
        /** Create a TcpServerWorker.
         *
         * @param post_office The PostOffice to get messages from.
         */
        TcpServerWorker(PostOffice & post_office)
            : post_office_(post_office)
            , shutting_down_(false)
            , connections_()
            , connections_changed_(false)
            , requests_()
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
        /* Remove a connection.
         *
         * Called by the worker thread when a client has disconnected.
         */
        void remove_connection_(int fd) {
            {
                std::lock_guard<std::mutex> lock(mutex_);
                auto it = std::find(connections_.begin(), connections_.end(), fd);
                connections_.erase(it);
                connections_changed_ = true;
            }
            if (requests_.count(fd))
                requests_.erase(fd);
        }

        /* Copies the list of managed connections into a poll_fd structure.
         *
         * Having a copy allows the server thread to add connections while the
         * worker is handling requests.
         *
         * This readies the polled_fds_ member for calling poll().
         *
         * Called by the worker thread.
         */
        void update_polled_fds_() {
            std::lock_guard<std::mutex> lock(mutex_);
            if (connections_changed_) {
                polled_fds_.resize(connections_.size());
                std::size_t i = 0;
                for (auto & conn: connections_) {
                    polled_fds_[i].fd = conn;
                    polled_fds_[i].events = POLLIN;
                    polled_fds_[i].revents = 0;
                    ++i;
                }
                connections_changed_ = false;
            }
        }

        /* Checks which clients sent a request, and receives those requests.
         *
         * This takes the results from calling poll(), receives requests,
         * and stores them in requests_.
         *
         * Called by the worker thread.
         */
        void get_requests_() {
            for (auto & polled_fd: polled_fds_)
                if (polled_fd.revents & (POLLIN | POLLHUP)) {
                    try {
                        int64_t length = recv_int64(polled_fd.fd);
                        std::vector<char> reqbuf(length);
                        recv_all(polled_fd.fd, reqbuf.data(), length);
                        requests_[polled_fd.fd] = std::string(reqbuf.cbegin(), reqbuf.cend());
                    }
                    catch (std::runtime_error const & e) {
                        // EOF; port was closed, mark as such
                        polled_fd.revents |= POLLHUP;
                    }
                }
        }

        /* Sends responses to clients that made a request.
         *
         * This takes requests from requests_ and fulfills them by sending
         * messages from the PostOffice, if any are available. Skips sending
         * if there is no message yet, it doesn't block.
         *
         * Called by the worker thread.
         */
        void send_responses_() {
            for (auto & req: requests_) {
                if (!req.second.empty()) {
                    if (post_office_.has_message(req.second)) {
                        auto msg = post_office_.get_message(req.second);

                        Data port_length;
                        if (msg->port_length.is_set())
                            port_length = msg->port_length.get();

                        Data next_timestamp;
                        if (msg->next_timestamp.is_set())
                            next_timestamp = msg->next_timestamp.get();

                        Data msg_dict = Data::dict(
                                "sender", std::string(msg->sender),
                                "receiver", std::string(msg->receiver),
                                "port_length", port_length,
                                "timestamp", msg->timestamp,
                                "next_timestamp", next_timestamp,
                                "settings_overlay", msg->settings_overlay,
                                "data", msg->data
                                );

                        msgpack::sbuffer sbuf;
                        msgpack::pack(sbuf, msg_dict);
                        send_int64(req.first, sbuf.size());
                        send_all(req.first, sbuf.data(), sbuf.size());

                        req.second.clear();
                    }
                }
            }
        }

        /* Detects ports that have closed and removes those connections.
         *
         * This cleans up the internal administration when clients disconnect.
         *
         * Called by the worker thread.
         */
        void remove_closed_ports_() {
            for (auto const & polled_fd: polled_fds_)
                if (polled_fd.revents & POLLHUP) {
                    ::close(polled_fd.fd);
                    remove_connection_(polled_fd.fd);
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
         * @param self The TcpServerWorker this thread belongs to.
         */
        static void worker_thread_(TcpServerWorker * self) {
            while (true) {
                self->update_polled_fds_();
                poll(self->polled_fds_.data(), self->polled_fds_.size(), 5);

                self->get_requests_();
                self->send_responses_();
                self->remove_closed_ports_();

                {
                    std::lock_guard<std::mutex> lock(self->mutex_);
                    if (self->connections_.empty() && self->shutting_down_)
                        break;
                }
            }
        }

        PostOffice & post_office_;
        bool shutting_down_;
        std::vector<int> connections_;
        bool connections_changed_;
        std::unordered_map<int, std::string> requests_;
        std::vector<pollfd> polled_fds_;
        // mutex before thread, it needs to be initialised before the thread
        // is started.
        mutable std::mutex mutex_;
        std::thread thread_;
};

}


namespace libmuscle { namespace mcp {

TcpServer::TcpServer(Reference const & instance_id, PostOffice & post_office)
    : Server(instance_id, post_office)
{
    pipe(control_pipe_);
    thread_ = std::thread(server_thread_, this);
}

TcpServer::~TcpServer() {
    if (thread_.joinable())
        close();
}

std::string TcpServer::get_location() const {
    std::unique_lock<std::mutex> lock(mutex_);
    while (location_.empty())
        location_set_.wait(lock);
    return location_;
}

void TcpServer::close() {
    char dummy = 0;
    ::write(control_pipe_[1], &dummy, 1);
    thread_.join();
}

std::vector<std::string> TcpServer::get_interfaces_() const {
    std::vector<std::string> addresses;
    ifaddrs * interfaces;
    int err_code = 0;
    if ((err_code = getifaddrs(&interfaces)) != 0)
        throw std::runtime_error("Error enumerating network interfaces");

    for (ifaddrs * p = interfaces; p != nullptr; p = p->ifa_next) {
        auto addr = reinterpret_cast<sockaddr_in *>(p->ifa_addr);
        int family = p->ifa_addr->sa_family;
        if ((family == AF_INET) || (family == AF_INET6)) {
            char addr_buf[INET6_ADDRSTRLEN];
            inet_ntop(family, &(addr->sin_addr), addr_buf, INET6_ADDRSTRLEN);
            addresses.push_back(addr_buf);
        }
    }
    freeifaddrs(interfaces);
    return addresses;
}

TcpServer::AddrInfoList_ TcpServer::get_address_info_(
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

std::vector<int> TcpServer::create_sockets_(addrinfo const * addresses) const {
    std::vector<int> result;
    int err = 0;
    for (addrinfo const *p = addresses; p != nullptr; p = p->ai_next) {
        int sockfd;
        if ((sockfd = socket(p->ai_family, p->ai_socktype, p->ai_protocol)) == -1)
            continue;

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

std::string TcpServer::get_address_string_(int sockfd) const {
    std::string location;

    sockaddr_storage bound_addr;
    socklen_t addr_len = sizeof bound_addr;
    getsockname(sockfd, reinterpret_cast<sockaddr*>(&bound_addr), &addr_len);

    char addr_buf[INET6_ADDRSTRLEN];
    int port = 0;

    auto family = reinterpret_cast<sockaddr*>(&bound_addr)->sa_family;
    if (family == AF_INET) {
        auto ipv4_addr = reinterpret_cast<sockaddr_in*>(&bound_addr);
        inet_ntop(AF_INET, &(ipv4_addr->sin_addr), addr_buf, INET6_ADDRSTRLEN);
        port = ntohs(ipv4_addr->sin_port);
        location = std::string(addr_buf) + ":" + std::to_string(port);
    }
    else if (family == AF_INET6) {
        auto ipv6_addr = reinterpret_cast<sockaddr_in6*>(&bound_addr);
        inet_ntop(AF_INET6, &(ipv6_addr->sin6_addr), addr_buf, INET6_ADDRSTRLEN);
        port = ntohs(ipv6_addr->sin6_port);
        location = "[" + std::string(addr_buf) + "]:" + std::to_string(port);
    }
    else
        throw std::runtime_error("Unknown address family");

    return location;
}

void TcpServer::set_location_(std::string const & location) {
    std::lock_guard<std::mutex> lock(mutex_);
    location_ = location;
    location_set_.notify_all();
}

std::vector<int> TcpServer::set_up_sockets_() {
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

void TcpServer::server_thread_(TcpServer * self) {
    std::vector<std::unique_ptr<TcpServerWorker>> workers;
    workers.emplace_back(new TcpServerWorker(self->post_office_));
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

} }

