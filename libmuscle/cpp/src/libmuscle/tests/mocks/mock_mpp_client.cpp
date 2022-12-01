#include <mocks/mock_mpp_client.hpp>

#include <libmuscle/data.hpp>
#include <libmuscle/mcp/data_pack.hpp>
#include <libmuscle/timestamp.hpp>

#include <cstring>
#include <string>
#include <tuple>
#include <vector>


namespace libmuscle { namespace impl {

MockMPPClient::MockMPPClient(std::vector<std::string> const & locations) {
    ++num_constructed;
}

MockMPPClient::~MockMPPClient() {}

std::tuple<DataConstRef, ProfileData> MockMPPClient::receive(
        ::ymmsl::Reference const & receiver) {
    last_receiver = receiver;

    return std::make_tuple(
            next_receive_message.encoded(), std::make_tuple(
                Timestamp(1.0), Timestamp(2.0), Timestamp(3.0)));
}

void MockMPPClient::close() {}


void MockMPPClient::reset() {
    num_constructed = 0;
    next_receive_message.sender = "test.out";
    next_receive_message.receiver = "test2.in";
    next_receive_message.port_length = 0;
    next_receive_message.timestamp = 0.0;
    next_receive_message.next_timestamp = 1.0;
    last_receiver = "_none";
}

int MockMPPClient::num_constructed = 0;

Settings MockMPPClient::make_overlay_() {
    Settings s;
    s["test2"] = 3.1;
    return s;
}

MPPMessage MockMPPClient::next_receive_message(
        "test.out", "test2.in", 0, 0.0, 1.0, make_overlay_(),0, 9.0,
        Data::dict("test1", 12));

Reference MockMPPClient::last_receiver("_none");

} }

