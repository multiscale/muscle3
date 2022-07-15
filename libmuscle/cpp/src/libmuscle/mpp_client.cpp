#include "libmuscle/mpp_client.hpp"

#include "libmuscle/data.hpp"
#include "libmuscle/mcp/protocol.hpp"
#include "libmuscle/mcp/data_pack.hpp"
#include "libmuscle/mcp/tcp_transport_client.hpp"

#include <memory>
#include <stdexcept>


using libmuscle::impl::Data;
using libmuscle::impl::DataConstRef;
using libmuscle::impl::mcp::TcpTransportClient;
using ymmsl::Reference;


namespace libmuscle { namespace impl {

MPPClient::MPPClient(std::vector<std::string> const & locations) {
    try_connect_<TcpTransportClient>(locations);
    if (!transport_client_)
        throw std::runtime_error("Could not connect to peer");
}

DataConstRef MPPClient::receive(Reference const & receiver) {
    auto request = Data::list(
            static_cast<int>(RequestType::get_next_message),
            std::string(receiver));

    msgpack::sbuffer sbuf;
    // TODO: can we put in an 8-byte dummy value here, which we
    // can then overwrite after encoding with the length?
    msgpack::pack(sbuf, request);

    return transport_client_->call(sbuf.data(), sbuf.size());
}

void MPPClient::close() {
    transport_client_->close();
}


template <class ClientType> void MPPClient::try_connect_(
        std::vector<std::string> const & locations
) {
    for (auto const & location : locations) {
        if (ClientType::can_connect_to(location)) {
            try {
                transport_client_ = std::make_unique<ClientType>(location);
                break;
            }
            catch (std::runtime_error const & e) {}
        }
    }
}

} }

