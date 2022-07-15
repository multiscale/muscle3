#include <libmuscle/mcp/transport_client.hpp>


namespace libmuscle { namespace impl {

namespace mcp {

bool TransportClient::can_connect_to(std::string const & location) {
    return false;
}

TransportClient::~TransportClient() {}

}   // namespace mcp

} }   // namespace libmuscle::impl

