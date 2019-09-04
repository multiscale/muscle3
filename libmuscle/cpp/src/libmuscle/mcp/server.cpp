#include <libmuscle/mcp/server.hpp>


using ymmsl::Reference;


namespace libmuscle { namespace mcp {

Server::Server(
        Reference const & instance_id, PostOffice & post_office)
    : instance_id_(instance_id)
    , post_office_(post_office)
{}


} }

