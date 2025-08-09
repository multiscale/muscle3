#include <libmuscle/mcp/tcp_util.hpp>
#include <libmuscle/util.hpp>
#include <libmuscle/mark.hpp>

#include <algorithm>
#include <cassert>
#include <cstring>
#include <limits>
#include <poll.h>
#include <stdexcept>
#include <utility>
#include <vector>

#include <sys/socket.h>


namespace {
    auto const connection_errors = {
        EBADF, ECONNABORTED, ECONNREFUSED, ECONNRESET, ENOTCONN, EPIPE, ETIMEDOUT
    };

    /* This weird thing is the easiest way I could find to avoid an unused return value
     * warning when calling strerror_r below. Note that in this case, ignoring the
     * return value is actually reasonable: if something goes wrong and we can't make an
     * error message (which is very unlikely anyway), then we'll use an empty one.
     *
     * - there's no standard way of disabling a warning in the code that works across
     *   compilers
     * - strerror_r returns char* on GNU systems, int on POSIX-compliant systems
     * - to make a GNU system provide the POSIX-standard int version, you need to unset
     *   _GNU_SOURCE, but that breaks libstdc++
     * - using auto err = strerror_r(...) gives a warning unless err is used
     * - in case of no error, you get a valid pointer, or the value 0, so we can't just
     *   compare the result to 0 and rely on ugly implicit conversion
     * - defining two overloads use(int) and use(char*) gives a warning because one will
     *   be unused
     */
    void use(decltype(strerror_r(0, std::declval<char*>(), 0u))) {};
}


namespace libmuscle { namespace _MUSCLE_IMPL_NS { namespace mcp {

ssize_t check_conn(ssize_t result) {
    if (result == -1) {
        if (errno == ECONNREFUSED) {
            throw ConnectionRefused("Connection refused");
        }
        for (int i: ::connection_errors) {
            if (errno == i) {
                throw Disconnect("Connection was lost");
            }
        }
        std::vector<char> err_str(1024);
        use(strerror_r(errno, &err_str[0], err_str.size()));
        throw std::runtime_error(&err_str[0]);
    }
    return result;
}

int poll_retry_eintr(pollfd *fds, nfds_t nfds, double timeout) {
    const double deadline = time_monotonic() + timeout;
    while (true) {
        int poll_result = poll(fds, nfds, static_cast<int>(timeout * 1000.0));

        if (poll_result >= 0)
            return poll_result;

        if (errno != EINTR)
            throw std::runtime_error(
                    "Unexpected error during poll(): " +
                    std::string(std::strerror(errno)));
        // poll() was interrupted by a signal: retry with re-calculated timeout
        timeout = deadline - time_monotonic();
    }
}

int do_poll_out(int socket_fd, double timeout) {
    struct pollfd pollfds;
    pollfds.fd = socket_fd;
    pollfds.events = POLLOUT;
    pollfds.revents = 0;
    return poll_retry_eintr(&pollfds, 1, timeout);
}

ssize_t send_all(int fd, char const * data, ssize_t length) {
    for (ssize_t sent = 0; sent < length; ) {
        mark::before_tcp_send(fd);
        ssize_t sent_now = check_conn(
                send(fd, data + sent, length - sent, MSG_NOSIGNAL));
        sent += sent_now;
    }
    return length;
}

ssize_t recv_all(int fd, char * data, ssize_t length) {
    for (ssize_t recvd = 0; recvd < length; ) {
        mark::before_tcp_receive(fd);
        ssize_t recvd_now = check_conn(recv(fd, data + recvd, length - recvd, 0));
        if (recvd_now == 0)
            throw Disconnect("Socket closed while receiving");
        recvd += recvd_now;
    }
    return length;
}

void send_int64(int fd, int64_t data) {
    mark::before_tcp_send(fd);
    send_all(fd, reinterpret_cast<char*>(&data), 8);
}

int64_t recv_int64(int fd) {
    mark::before_tcp_receive(fd);
    int64_t data;
    recv_all(fd, reinterpret_cast<char*>(&data), 8);
    return data;
}

ssize_t send_frame(int fd, char const * data, ssize_t length) {
    static_assert(sizeof(ssize_t) == 8, "MUSCLE3 needs a 64-bit machine/OS to compile");

    assert(length >= 0);
    assert(length + 8 < std::numeric_limits<ssize_t>::max());

    char * len_data = reinterpret_cast<char*>(&length);

    std::vector<char> buf(length + 8);
    std::copy(len_data, len_data + 8, buf.data());
    std::copy(data, data + length, buf.data() + 8);

    send_all(fd, buf.data(), length + 8);
    return length;
}

std::vector<char> recv_frame(int fd) {
    ssize_t length = recv_int64(fd);
    std::vector<char> result(length);
    recv_all(fd, &result[0], length);
    return result;
}

} } }

