#include "libmuscle/mcp/tcp_transport_client.hpp"

#include <libmuscle/mcp/tcp_util.hpp>

#include <algorithm>
#include <cstring>
#include <chrono>
#include <exception>
#include <memory>
#include <stdexcept>
#include <string>
#include <thread>
#include <unistd.h>
#include <vector>

#include <sys/types.h>
#include <sys/socket.h>
#include <errno.h>
#include <fcntl.h>
#include <netdb.h>
#include <netinet/tcp.h>
#include <poll.h>
#include <string.h>
#include <unistd.h>


namespace {

using libmuscle::_MUSCLE_IMPL_NS::time_monotonic;
using libmuscle::_MUSCLE_IMPL_NS::mcp::check_conn;
using libmuscle::_MUSCLE_IMPL_NS::mcp::ConnectionRefused;
using libmuscle::_MUSCLE_IMPL_NS::mcp::do_poll_out;
using std::chrono::duration;


const double connect_timeout = 3.0;                 // seconds
const double connect_timeout_patient = 60.0;        // seconds
const double connect_timeout_patient_step = 3.0;    // seconds
const double reconnect_timeout = 60.0;              // seconds


/* Splits a location string of the form tcp:<address:port>,<address:port>,...
 * into a list of addresses.
 */
std::vector<std::string> split_location(std::string const & location) {
    std::vector<std::string> addresses;

    // start at 4 to skip the initial tcp: bit
    for (auto it = std::next(location.cbegin(), 4); it != location.cend(); ) {
        auto next = std::find(it, location.cend(), ',');
        addresses.emplace_back(it, next);

        it = next;
        if (it != location.cend())
            ++it;
    }

    return addresses;
}


int connect(std::string const & address, bool patient) {
    std::string errors;

    std::size_t split = address.rfind(':');
    std::string host = address.substr(0, split);
    if (host.front() == '[') {
        if (host.back() == ']')
            host = host.substr(1, host.size() - 2);
        else
            throw std::runtime_error("Invalid address");
    }
    std::string port = address.substr(split + 1);

    int err_code;
    const double timeout = patient ? connect_timeout_patient : connect_timeout;
    const double patient_step = connect_timeout_patient_step;

    // collect addresses to connect to
    addrinfo hints;
    memset(&hints, 0, sizeof hints);
    hints.ai_family = AF_UNSPEC;
    hints.ai_socktype = SOCK_STREAM;

    addrinfo *res;
    err_code = getaddrinfo(host.c_str(), port.c_str(), &hints, &res);
    if (err_code != 0)
        throw std::runtime_error("Could not connect to " + host + " on port "
                + port + ": " + gai_strerror(err_code));
    auto address_info = std::unique_ptr<addrinfo, void (*)(addrinfo*)>(res, &freeaddrinfo);

    // try to connect to each in turn until we find one that works
    addrinfo * p;
    for (p = address_info.get(); p != nullptr; p = p->ai_next) {
        int socket_fd = socket(p->ai_family, p->ai_socktype, p->ai_protocol);
        if (socket_fd == -1) continue;

        const double start_time = time_monotonic();
        double time_left = (start_time + timeout) - time_monotonic();

        while (time_left > 0.0) {
            try {
                int flags = fcntl(socket_fd, F_GETFL, 0);
                fcntl(socket_fd, F_SETFL, flags | O_NONBLOCK);

                connect(socket_fd, p->ai_addr, p->ai_addrlen);
                do_poll_out(socket_fd, time_left);

                // check if connect() actually succeeded
                socklen_t len = sizeof(int);
                getsockopt(socket_fd, SOL_SOCKET, SO_ERROR, &err_code, &len);
                check_conn(err_code);

                flags = fcntl(socket_fd, F_GETFL, 0);
                fcntl(socket_fd, F_SETFL, flags & ~O_NONBLOCK);

                return socket_fd;
            }
            catch (ConnectionRefused const & e) {
                if (patient) {
                    // TODO: warning Connection refused, sleeping
                    std::this_thread::sleep_for(duration<double>(patient_step));
                }
                else {
                    // TODO: info Failed to connect to << sockaddr
                    ::close(socket_fd);
                    break;
                }
            }
            catch (std::exception const & e) {
                // TODO: debug Failed to connect socket << e
                ::close(socket_fd);
                break;
            }

            time_left = (start_time + timeout) - time_monotonic();
        }
    }

    throw ConnectionRefused("Could not connect");
}

}


namespace libmuscle { namespace _MUSCLE_IMPL_NS { namespace mcp {

bool TcpTransportClient::can_connect_to(std::string const & location) {
    return location.compare(0u, 4u, "tcp:") == 0;
}

TcpTransportClient::TcpTransportClient(std::string const & location)
    : socket_fd_(-1)
    , session_(0)
    , cur_request_(0)
{
    addresses_ = split_location(location);
    reconnect_(false);
}

TcpTransportClient::~TcpTransportClient() {
    if (socket_fd_ != -1)
        close();
}

std::tuple<std::vector<char>, ProfileData> TcpTransportClient::call(
        char const * req_buf, std::size_t req_len,
        TimeoutHandler* timeout_handler
) {
    ++cur_request_;
    Retrier retrier(reconnect_timeout);

    double start_time = time_monotonic();

    bool did_timeout = false;
    while (true) {
        try {
            ProfileTimestamp start_wait;
            send_int64(socket_fd_, cur_request_);
            send_frame(socket_fd_, req_buf, req_len);

            if (timeout_handler != nullptr) {
                pollfd socket_poll_fd;
                socket_poll_fd.fd = socket_fd_;
                socket_poll_fd.events = POLLIN;
                while (poll_retry_eintr(&socket_poll_fd, 1, timeout_handler->get_timeout()) == 0) {
                    timeout_handler->on_timeout();
                    did_timeout = true;
                }
                if (did_timeout) {
                    // We call this to give the manager a chance to tell us about a
                    // deadlock if the poll ended because of a disconnect because the
                    // peer crashed due to that deadlock.
                    timeout_handler->on_timeout();

                    timeout_handler->on_receive();
                    did_timeout = false;
                }
            }

            ProfileTimestamp start_transfer;
            std::vector<char> result = recv_frame(socket_fd_);
            ProfileTimestamp stop_transfer;
            return std::make_tuple(
                    std::move(result),
                    std::make_tuple(start_wait, start_transfer, stop_transfer));
        }
        catch (Disconnect const & e) {
            handle_disconnect_(retrier);
        }
    }
}

void TcpTransportClient::close() {
    ::close(socket_fd_);
    socket_fd_ = -1;
}

/** Handles a broken network connection.
 *
 * @param retrier A Retries that keeps track of timing any retries
 */
void TcpTransportClient::handle_disconnect_(Retrier & retrier) {
    // TODO: warning The TCP network connection with << addresses << was lost
    // unexpectedly.

    try {
        close();
    }
    catch (Disconnect const & e) {}

    if (retrier.should_give_up()) {
        // TODO: warning I am unable to reconnect to << addresses << despite repeated
        // attempts, and I am giving up. Please check your network.
        throw;
    }

    retrier.sleep();
    // TODO: warning Trying to reconnect to << addresses
    reconnect_();
}


/** (Re)connect to the server and resume the current session
 *
 * @param re True if this is a reconnect rather than an initial connect
 */
void TcpTransportClient::reconnect_(bool re) {
    try {
        make_connection_();
        send_int64(socket_fd_, session_);
        session_ = recv_int64(socket_fd_);

        if (re) {
            // TODO: warning Reconnected to << addresses << , continuing the simulation
        }
    }
    catch (Disconnect const & e) {
        close();
        // TODO: warning Failed to reconnect to << addresses << , will retry later
    }
}


/** Connect to the server
 *
 * Uses addresses_ and creates a new socket_fd_ if successful.
 */
void TcpTransportClient::make_connection_() {
    std::string errors;
    int sock_fd = -1;

    for (auto const & address: addresses_)
        try {
            sock_fd = connect(address, false);
            break;
        }
        catch (std::runtime_error const & e) {
            errors += std::string(e.what()) + "\n";
        }

    if (sock_fd == -1) {
        // None of our quick connection attempts worked. Either there's a network
        // problem, or the server is very busy. Let's try again with more patience.
        // TODO: warning Could not immediately connect to << addresses << , trying again
        // with more patience. Please report this if it happens frequently.

        for (auto const & address: addresses_)
            try {
                // TODO debug Trying to connect to << address << patiently
                sock_fd = connect(address, true);
                break;
            }
            catch (std::runtime_error const & e) {
                errors += std::string(e.what()) + "\n";
            }
    }

    if (sock_fd == -1) {
        // TODO: error Failed to connect also on the second try to << addresses
        std::string location("[");
        for (auto const & address: addresses_) {
            if (location.size() > 1u)
                location += ", ";
            location += address;
        }
        throw std::runtime_error(
                "Could not connect to any server at locations " + location
                + ": " + errors);
    }

    int flags = 0;
#ifdef __linux
    setsockopt(sock_fd, SOL_TCP, TCP_NODELAY, &flags, sizeof(flags));
    setsockopt(sock_fd, SOL_TCP, TCP_QUICKACK, &flags, sizeof(flags));
#elif __APPLE__
    setsockopt(sock_fd, IPPROTO_TCP, TCP_NODELAY, &flags, sizeof(flags));
    // macOS doesn't have quickack unfortunately
#endif

    socket_fd_ = sock_fd;
}


} } }

