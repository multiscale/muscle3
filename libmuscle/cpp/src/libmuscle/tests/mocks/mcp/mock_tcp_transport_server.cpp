#include <mocks/mcp/mock_tcp_transport_server.hpp>

#include <ymmsl/ymmsl.hpp>

namespace libmuscle { namespace impl {

namespace mcp {

MockTcpTransportServer::MockTcpTransportServer(RequestHandler & handler)
    : TransportServer(handler)
{
    ++num_constructed;
}

MockTcpTransportServer::~MockTcpTransportServer() {}

std::string MockTcpTransportServer::get_location() const {
    return "tcp:test_location";
}

void MockTcpTransportServer::close() {}


void MockTcpTransportServer::reset() {
    num_constructed = 0;
}

int MockTcpTransportServer::num_constructed = 0;

}

} }

