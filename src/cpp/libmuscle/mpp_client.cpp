#include "libmuscle/mpp_client.hpp"

#include "libmuscle/data.hpp"
#include "libmuscle/mcp/protocol.hpp"
#include "libmuscle/mcp/data_pack.hpp"
#include "libmuscle/mcp/tcp_transport_client.hpp"

#include <memory>
#include <stdexcept>
#include <vector>


using libmuscle::_MUSCLE_IMPL_NS::Data;
using libmuscle::_MUSCLE_IMPL_NS::DataConstRef;
using libmuscle::_MUSCLE_IMPL_NS::mcp::ProfileData;
using libmuscle::_MUSCLE_IMPL_NS::mcp::TcpTransportClient;
using ymmsl::Reference;


namespace libmuscle { namespace _MUSCLE_IMPL_NS {

MPPClient::MPPClient(std::vector<std::string> const & locations) {
    try_connect_<TcpTransportClient>(locations);
    if (!transport_client_)
        throw std::runtime_error("Could not connect to peer");
}

std::tuple<std::vector<char>, ProfileData> MPPClient::receive(
        Reference const & receiver, mcp::TimeoutHandler *timeout_handler)
{
    auto request = Data::list(
            static_cast<int>(RequestType::get_next_message),
            std::string(receiver));

    msgpack::sbuffer sbuf;
    // TODO: can we put in an 8-byte dummy value here, which we
    // can then overwrite after encoding with the length?
    msgpack::pack(sbuf, request);

    return transport_client_->call(sbuf.data(), sbuf.size(), timeout_handler);
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

