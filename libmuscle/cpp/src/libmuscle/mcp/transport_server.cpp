#include <libmuscle/mcp/transport_server.hpp>


namespace libmuscle { namespace impl {namespace mcp {

TransportServer::TransportServer(RequestHandler & handler)
    : handler_(handler)
{}


} } }

