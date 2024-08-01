#include <libmuscle/mcp/transport_server.hpp>


namespace libmuscle { namespace _MUSCLE_IMPL_NS {namespace mcp {


RequestHandler::~RequestHandler() {}

TransportServerBase::TransportServerBase(RequestHandler & handler)
    : handler_(handler)
{}


} } }

