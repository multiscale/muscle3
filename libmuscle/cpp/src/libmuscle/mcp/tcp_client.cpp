#include "libmuscle/mcp/tcp_client.hpp"
#include "libmuscle/mcp/data_pack.hpp"

#include <iostream>
#include <ostream>
#include <memory>
#include <string>
#include <string.h>
#include <unistd.h>

#include <nng/nng.h>
#include <nng/protocol/reqrep0/req.h>

#include <msgpack.hpp>

#include <ymmsl/identity.hpp>


namespace libmuscle { namespace mcp {

bool TcpClient::can_connect_to(std::string const & location) {
    return location.compare(0u, 4u, "tcp:") == 0;
}

TcpClient::TcpClient(ymmsl::Reference const & instance_id, std::string const & location)
    : Client(instance_id, location)
{
    int err_code;

    std::string peer_loc = "tcp://" + location.substr(4);

    if ((err_code = nng_req0_open(&socket_)) != 0)
        throw std::runtime_error("Error opening socket for address " + peer_loc
                + ": " + nng_strerror(err_code));

    if ((err_code = nng_dial(socket_, peer_loc.c_str(), NULL, 0)) != 0)
        throw std::runtime_error("Could not connect to " + peer_loc + ": "
                + nng_strerror(err_code));
}

TcpClient::~TcpClient() {
    close();
}

Message TcpClient::receive(::ymmsl::Reference const & receiver) {
    int err_code = 0;

    // Send receiver to get a message for
    std::string receiver_str = static_cast<std::string>(receiver);
    char const * receiver_data = receiver_str.data();
    ssize_t data_size = static_cast<ssize_t>(receiver_str.size());

    if ((err_code = nng_send(socket_, (void*)receiver_data, data_size, 0)) != 0)
        throw std::runtime_error(std::string("Error requesting message from peer: ")
                + nng_strerror(err_code));

    // receive data
    char * recv_buf = nullptr;
    std::size_t length;
    if ((err_code = nng_recv(socket_, &recv_buf, &length, NNG_FLAG_ALLOC)) != 0)
        throw std::runtime_error(std::string("Error receiving message from peer: ")
                + nng_strerror(err_code));

    auto zone = std::make_shared<msgpack::zone>();
    char * buf = static_cast<char *>(zone->allocate_align(length, 8u));
    memcpy(buf, recv_buf, length);
    nng_free(recv_buf, length);

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
    nng_close(socket_);
}


} }

