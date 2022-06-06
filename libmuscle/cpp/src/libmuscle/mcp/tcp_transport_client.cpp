#include "libmuscle/mcp/tcp_transport_client.hpp"

#include "libmuscle/data.hpp"
#include "libmuscle/mcp/tcp_util.hpp"

#include <algorithm>
#include <cstring>
#include <memory>
#include <string>
#include <unistd.h>

#include <sys/types.h>
#include <sys/socket.h>
#include <netdb.h>


namespace {

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

        err_code = connect(socket_fd, p->ai_addr, p->ai_addrlen);
        if (err_code == -1) {
            ::close(socket_fd);
            continue;
        }
        return socket_fd;
    }

    throw std::runtime_error("Could not connect to " + host + " on port "
            + port);
}

}


namespace libmuscle { namespace impl { namespace mcp {

bool TcpTransportClient::can_connect_to(std::string const & location) {
    return location.compare(0u, 4u, "tcp:") == 0;
}

TcpTransportClient::TcpTransportClient(std::string const & location)
    : socket_fd_(-1)
{
    std::string errors;
    auto addresses = split_location(location);

    for (auto const & address: addresses)
        try {
            socket_fd_ = connect(address);
            break;
        }
        catch (std::runtime_error const & e) {
            errors += std::string(e.what()) + "\n";
            continue;
        }

    if (socket_fd_ == -1)
        throw std::runtime_error(
                "Could not connect to any server at locations " + location
                + ": " + errors);
}

TcpTransportClient::~TcpTransportClient() {
    if (socket_fd_ != -1)
        close();
}

DataConstRef TcpTransportClient::call(
        char const * req_buf, std::size_t req_len
) const {
    send_int64(socket_fd_, req_len);
    send_all(socket_fd_, req_buf, req_len);

    int64_t length = recv_int64(socket_fd_);
    auto result = Data::byte_array(length);
    recv_all(socket_fd_, result.as_byte_array(), result.size());
    return result;
}

void TcpTransportClient::close() {
    ::close(socket_fd_);
    socket_fd_ = -1;
}

} } }

