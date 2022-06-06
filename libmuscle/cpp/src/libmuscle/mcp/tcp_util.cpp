#include <libmuscle/mcp/tcp_util.hpp>

#include <stdexcept>

#include <sys/socket.h>


namespace libmuscle { namespace impl { namespace mcp {

ssize_t send_all(int fd, char const * data, ssize_t length) {
    for (ssize_t sent = 0; sent < length; ) {
        ssize_t sent_now = send(fd, data + sent, length - sent, MSG_NOSIGNAL);
        if (sent_now == -1)
            return -1;
        sent += sent_now;
    }
    return length;
}

ssize_t recv_all(int fd, char * data, ssize_t length) {
    for (ssize_t recvd = 0; recvd < length; ) {
        ssize_t recvd_now = recv(fd, data + recvd, length - recvd, 0);
        if (recvd_now == 0)
            throw std::runtime_error("Socket closed while receiving");
        if (recvd_now == -1)
            return -1;
        recvd += recvd_now;
    }
    return length;
}

void send_int64(int fd, int64_t data) {
    ssize_t err = send_all(fd, reinterpret_cast<char*>(&data), 8);
    if (err != 8)
        throw std::runtime_error("Error sending data on socket");
}

int64_t recv_int64(int fd) {
    int64_t data;
    ssize_t err = recv_all(fd, reinterpret_cast<char*>(&data), 8);
    if (err != 8)
        throw std::runtime_error("Error receiving data on socket");
    return data;
}

} } }

