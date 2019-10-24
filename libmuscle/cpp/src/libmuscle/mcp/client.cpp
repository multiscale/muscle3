#include <libmuscle/mcp/client.hpp>

#include <ymmsl/ymmsl.hpp>


namespace libmuscle { namespace impl {

namespace mcp {

bool Client::can_connect_to(std::string const & location) {
    return false;
}

void Client::shutdown(::ymmsl::Reference const & instance_id) {}

Client::Client(::ymmsl::Reference const & instance_id,
               std::string const & location)
{}

Client::~Client() {}

}   // namespace mcp

} }   // namespace libmuscle::impl

