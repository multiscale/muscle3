#include <mocks/mcp/mock_tcp_server.hpp>

#include <ymmsl/identity.hpp>

namespace libmuscle { namespace impl {

namespace mcp {

MockTcpServer::MockTcpServer(ymmsl::Reference const & instance_id, PostOffice & post_office)
    : Server(instance_id, post_office)
{
    ++num_constructed;
    last_instance_id = instance_id;
}

MockTcpServer::~MockTcpServer() {}

std::string MockTcpServer::get_location() const {
    return "tcp:test_location";
}

void MockTcpServer::close() {}


void MockTcpServer::reset() {
    num_constructed = 0;
    last_instance_id = "_none";
}

int MockTcpServer::num_constructed = 0;

ymmsl::Reference MockTcpServer::last_instance_id("_none");

}

} }

