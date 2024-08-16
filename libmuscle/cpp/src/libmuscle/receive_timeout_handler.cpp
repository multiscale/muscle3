#include "receive_timeout_handler.hpp"

namespace libmuscle { namespace _MUSCLE_IMPL_NS {

ReceiveTimeoutHandler::ReceiveTimeoutHandler(
        MMPClient& manager, std::string const& peer_instance,
        std::string const& port_name, Optional<int> slot, double timeout)
    : manager_(manager)
    , peer_instance_(peer_instance)
    , port_name_(port_name)
    , slot_(slot)
    , timeout_(timeout) {}

double ReceiveTimeoutHandler::get_timeout()
{
    return timeout_;
}

void ReceiveTimeoutHandler::on_timeout()
{
    manager_.waiting_for_receive(peer_instance_, port_name_, slot_);
}

void ReceiveTimeoutHandler::on_receive()
{
    manager_.waiting_for_receive_done(peer_instance_, port_name_, slot_);
}

} }
