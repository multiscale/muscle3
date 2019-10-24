#include <mocks/mcp/mock_tcp_client.hpp>

#include <libmuscle/data.hpp>
#include <libmuscle/mcp/data_pack.hpp>

#include <cstring>


namespace libmuscle { namespace impl {

namespace mcp {

MockTcpClient::MockTcpClient(::ymmsl::Reference const & instance_id, std::string const & location)
    : Client(instance_id, location)
{
    ++num_constructed;
}

MockTcpClient::~MockTcpClient() {}

bool MockTcpClient::can_connect_to(std::string const & location) {
    return true;
}

void MockTcpClient::shutdown(::ymmsl::Reference const & instance_id) {}

DataConstRef MockTcpClient::receive(::ymmsl::Reference const & receiver) {
    last_receiver = receiver;

    return next_receive_message.encoded();
}

void MockTcpClient::close() {}


void MockTcpClient::reset() {
    num_constructed = 0;
    next_receive_message.sender = "test.out";
    next_receive_message.receiver = "test2.in";
    next_receive_message.port_length = 0;
    next_receive_message.timestamp = 0.0;
    next_receive_message.next_timestamp = 1.0;
    last_receiver = "_none";
}

int MockTcpClient::num_constructed = 0;

Settings MockTcpClient::make_overlay_() {
    Settings s;
    s["test2"] = 3.1;
    return s;
}

Message MockTcpClient::next_receive_message(
        "test.out", "test2.in", 0, 0.0, 1.0, make_overlay_(), Data::dict("test1", 12));

Reference MockTcpClient::last_receiver("_none");

}

} }

