#include <libmuscle/mpp_server.hpp>

#include <libmuscle/mcp/protocol.hpp>
#include <libmuscle/mcp/tcp_transport_server.hpp>
#include <libmuscle/namespace.hpp>
#include <libmuscle/post_office.hpp>
#include <ymmsl/ymmsl.hpp>


using libmuscle::_MUSCLE_IMPL_NS::mcp::TcpTransportServer;
using ymmsl::Reference;


namespace libmuscle { namespace _MUSCLE_IMPL_NS {


MPPRequestHandler::MPPRequestHandler(PostOffice & post_office)
    : post_office_(post_office)
{}

int MPPRequestHandler::handle_request(
        char const * req_buf, std::size_t req_len,
        std::vector<char> & res_buf
) {
    auto zone = std::make_shared<msgpack::zone>();
    auto request = mcp::unpack_data(zone, req_buf, req_len);
    if (
            !request.is_a_list() || request.size() != 2 ||
            (request[0].as<int>() != static_cast<int>(RequestType::get_next_message)))
        throw std::runtime_error(
                "Invalid request type. Did the streams get crossed?");

    Reference receiver(request[1].as<std::string>());
    return post_office_.try_retrieve(receiver, res_buf);
}

std::vector<char> MPPRequestHandler::get_response(int fd) {
    return post_office_.get_message(fd);
}

MPPServer::MPPServer()
    : post_office_()
    , handler_(post_office_)
    , servers_()
{
    servers_.emplace_back(new TcpTransportServer(handler_));
}

std::vector<std::string> MPPServer::get_locations() const {
    std::vector<std::string> result;
    for (auto const & server : servers_)
        result.emplace_back(server->get_location());
    return result;
}

void MPPServer::deposit(
        ymmsl::Reference const & receiver,
        std::vector<char> && message
) {
    post_office_.deposit(receiver, std::move(message));
}

void MPPServer::wait_for_receivers() const {
    post_office_.wait_for_receivers();
}

void MPPServer::shutdown() {
    for (auto & server : servers_)
        server->close();
}

} }

