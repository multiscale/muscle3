#include "libmuscle/mcp/tcp_transport_client.hpp"

#include <libmuscle/logger.hpp>
#include <libmuscle/mcp/tcp_util.hpp>

#include <algorithm>
#include <cassert>
#include <cstring>
#include <chrono>
#include <cmath>
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

using libmuscle::_MUSCLE_IMPL_NS::log_debug;
using libmuscle::_MUSCLE_IMPL_NS::log_info;
using libmuscle::_MUSCLE_IMPL_NS::log_warning;
using libmuscle::_MUSCLE_IMPL_NS::time_monotonic;
using libmuscle::_MUSCLE_IMPL_NS::mcp::check_conn;
using libmuscle::_MUSCLE_IMPL_NS::mcp::ConnectionRefused;
using libmuscle::_MUSCLE_IMPL_NS::mcp::do_poll_out;
using std::chrono::duration;


const double connect_timeout = 3.0;                 // seconds
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


int connect(std::string const & address) {
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
        double time_left = (start_time + connect_timeout) - time_monotonic();

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
                log_info("Failed to connect to ", host);
                ::close(socket_fd);
                break;
            }
            catch (std::exception const & e) {
                log_debug("Failed to connect socket ", e.what());
                ::close(socket_fd);
                break;
            }

            time_left = (start_time + connect_timeout) - time_monotonic();
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
    : location_(location)
    , socket_fd_(-1)
    , session_(0)
    , cur_request_(0)
{
    addresses_ = split_location(location);
    reconnect_(false);
}

TcpTransportClient::~TcpTransportClient() {
    if (socket_fd_ != -1) {
        end_session_();
        close_connection_();
    }
}

std::tuple<std::vector<char>, ProfileData> TcpTransportClient::call(
        char const * req_buf, std::size_t req_len, TimeoutHandler* timeout_handler
) {
    ++cur_request_;
    Retrier retrier(reconnect_timeout);
    double deadline = std::numeric_limits<double>::infinity();
    bool did_timeout = false;

    while (true) {
        try {
            if (deadline < time_monotonic()) {
                timeout_handler->on_timeout();
                deadline += timeout_handler->get_timeout();
                did_timeout = true;
            }

            if (socket_fd_ == -1)
                throw Disconnect("No connection could be established");

            ProfileTimestamp start_wait;
            send_request_(cur_request_, req_buf, req_len);

            if (timeout_handler != nullptr) {
                if (std::isinf(deadline))
                    deadline = time_monotonic() + timeout_handler->get_timeout();

                pollfd socket_poll_fd;
                socket_poll_fd.fd = socket_fd_;
                socket_poll_fd.events = POLLIN;
                while (poll_retry_eintr(
                            &socket_poll_fd, 1, deadline - time_monotonic()) == 0) {
                    timeout_handler->on_timeout();
                    deadline += timeout_handler->get_timeout();
                    did_timeout = true;
                }

                if (did_timeout) {
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
    end_session_();
    close_connection_();
}

/** Sends a request in a single send call.
 *
 * This is an optimisation, we could just send_int64() the request_nr and then
 * send_frame() the data, but that causes short messages to be split across two packets,
 * with a 40ms delay in between. So we combine them here.
 */
void TcpTransportClient::send_request_(
        int64_t request_nr, char const * req_buf, std::size_t req_len)
{
    static_assert(sizeof(ssize_t) == 8, "MUSCLE3 needs a 64-bit machine/OS to compile");

    const ssize_t length = static_cast<ssize_t>(req_len);

    assert(length + 16 < std::numeric_limits<ssize_t>::max());

    const char * req_nr_data = reinterpret_cast<char*>(&request_nr);
    const char * len_data = reinterpret_cast<const char*>(&length);

    std::vector<char> buf(length + 16);
    std::copy(req_nr_data, req_nr_data + 8, buf.data());
    std::copy(len_data, len_data + 8, buf.data() + 8);
    std::copy(req_buf, req_buf + length, buf.data() + 16);

    send_all(socket_fd_, buf.data(), length + 16);
}

/** Handles a broken network connection.
 *
 * @param retrier A Retries that keeps track of timing any retries
 */
void TcpTransportClient::handle_disconnect_(Retrier & retrier) {
    log_warning("The TCP network connection with ", location_, " was lost unexpectedly.");

    try {
        close_connection_();
    }
    catch (Disconnect const & e) {}

    if (retrier.should_give_up()) {
        log_warning(
                "I am unable to reconnect to ", location_, " despite repeated",
                " attempts, and I am giving up. Please check your network.");
        throw;
    }

    retrier.sleep();
    log_warning("Trying to reconnect to ", location_);
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
            log_warning("Reconnected to ", location_, ", continuing the simulation");
        }
    }
    catch (Disconnect const & e) {
        close_connection_();
        log_warning("Failed to reconnect to ", location_,  ", will retry later");
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
            sock_fd = connect(address);
            break;
        }
        catch (std::runtime_error const & e) {
            errors += std::string(e.what()) + "\n";
        }

    if (sock_fd == -1) {
        throw Disconnect("Failed to connect");
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


/** Tell the server we want to end our session
 *
 * We ignore errors here and rely on the server to time out if we don't manage to send.
 */
void TcpTransportClient::end_session_() {
    // End session
    try {
        send_int64(socket_fd_, 0);
    }
    catch (Disconnect const &) {
        log_warning(
                "Disconnected while trying to end session, shutdown will take longer",
                " than usual because of this.");
    }
}


/** Close the network connection and reset the socket fd
 */
void TcpTransportClient::close_connection_() {
    ::close(socket_fd_);
    socket_fd_ = -1;
}


} } }

