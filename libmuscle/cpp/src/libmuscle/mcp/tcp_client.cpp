#include <libmuscle/mcp/tcp_client.hpp>

#include <libmuscle/mcp/data_pack.hpp>
#include <libmuscle/mcp/tcp_util.hpp>

#include <memory>
#include <string>
#include <unistd.h>

#include <sys/types.h>
#include <sys/socket.h>
#include <netdb.h>

#include <msgpack.hpp>

#include <ymmsl/ymmsl.hpp>


using ymmsl::Reference;

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
    auto address_info = std::unique_ptr<addrinfo, void (*)(addrinfo*)>(res, &freeaddrinfo);
    if (err_code != 0)
        throw std::runtime_error("Could not connect to " + host + " on port "
                + port + ": " + gai_strerror(err_code));

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

bool TcpClient::can_connect_to(std::string const & location) {
    return location.compare(0u, 4u, "tcp:") == 0;
}

void TcpClient::shutdown(Reference const & instance_id) {}

TcpClient::TcpClient(ymmsl::Reference const & instance_id, std::string const & location)
    : Client(instance_id, location)
    , socket_fd_(-1)
{
    auto addresses = split_location(location);

    for (auto const & address: addresses)
        try {
            socket_fd_ = connect(address);
            break;
        }
        catch (std::runtime_error const & e) {
            continue;
        }

    if (socket_fd_ == -1)
        throw std::runtime_error("Could not connect to the server at location " + location);
}

TcpClient::~TcpClient() {
    if (socket_fd_ != -1)
        close();
}

DataConstRef TcpClient::receive(::ymmsl::Reference const & receiver) {
    // Send receiver to get a message for
    std::string receiver_str = static_cast<std::string>(receiver);
    send_int64(socket_fd_, receiver_str.length());
    send_all(socket_fd_, receiver_str.data(), receiver_str.length());

    // receive data length
    int64_t length = recv_int64(socket_fd_);

    // receive data
    Data buf = Data::byte_array(length);
    recv_all(socket_fd_, buf.as_byte_array(), length);

    return buf;
}


void TcpClient::close() {
    ::close(socket_fd_);
    socket_fd_ = -1;
}

} } }

