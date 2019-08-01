#include "libmuscle/mcp/tcp_client.hpp"
#include "libmuscle/mcp/data_pack.hpp"

#include <iostream>
#include <ostream>
#include <memory>
#include <string>
#include <unistd.h>

#include <sys/types.h>
#include <sys/socket.h>
#include <netdb.h>

#include <msgpack.hpp>

#include <ymmsl/identity.hpp>


namespace libmuscle { namespace mcp {

bool TcpClient::can_connect_to(std::string const & location) {
    return location.compare(0u, 4u, "tcp:") == 0;
}

TcpClient::TcpClient(ymmsl::Reference const & instance_id, std::string const & location)
    : Client(instance_id, location)
{
    std::size_t host_pos = location.find(':') + 1;
    std::size_t port_pos = location.find(':', host_pos) + 1;
    std::string host = location.substr(host_pos, port_pos - host_pos - 1);
    std::string port = location.substr(port_pos);

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
        socket_fd_ = socket(p->ai_family, p->ai_socktype, p->ai_protocol);
        if (socket_fd_ == -1) continue;
        err_code = connect(socket_fd_, p->ai_addr, p->ai_addrlen);
        if (err_code == -1) {
            ::close(socket_fd_);
            socket_fd_ = -1;
            continue;
        }
        break;
    }

    if (p == nullptr)
        throw std::runtime_error("Could not connect to " + host + " on port "
                + port);
}

TcpClient::~TcpClient() {
    if (socket_fd_ != -1)
        close();
}

Message TcpClient::receive(::ymmsl::Reference const & receiver) {
    // Send receiver to get a message for
    std::string receiver_str = static_cast<std::string>(receiver);
    char const * receiver_data = receiver_str.data();
    ssize_t data_size = static_cast<ssize_t>(receiver_str.size());

    for (ssize_t sent = 0; sent < data_size; )
        sent += send(socket_fd_,
                receiver_data + sent, data_size - sent, 0);

    // receive data length
    unsigned char lenbuf[8];
    recv(socket_fd_, lenbuf, 8, 0);
    int64_t length = 0;
    for (int i = 0; i < 8; ++i)
        length += static_cast<int64_t>(lenbuf[i]) << (i * 8);

    // receive data
    auto zone = std::make_shared<msgpack::zone>();
    char * buf = static_cast<char *>(zone->allocate_align(length, 8u));
    for (ssize_t received = 0; received < length; )
        received += recv(socket_fd_,
                buf + received, length - received, 0);

    // decode
    DataConstRef data = unpack_data(zone, buf, length);

    // create message
    libmuscle::Optional<int> port_length;
    if (data["port_length"].is_a<int>())
        port_length = data["port_length"].as<int>();

    libmuscle::Optional<double> next_timestamp;
    if (data["next_timestamp"].is_a<double>())
        next_timestamp = data["next_timestamp"].as<double>();

    return Message(
            data["sender"].as<std::string>(),
            data["receiver"].as<std::string>(),
            port_length,
            data["timestamp"].as<double>(),
            next_timestamp,
            data["parameter_overlay"],
            data["data"]);
}


void TcpClient::close() {
    ::close(socket_fd_);
}


} }

