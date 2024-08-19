#include "receive_timeout_handler.hpp"

#include <cmath>

namespace libmuscle { namespace _MUSCLE_IMPL_NS {

ReceiveTimeoutHandler::ReceiveTimeoutHandler(
        MMPClient& manager, std::string const& peer_instance,
        std::string const& port_name, Optional<int> slot, double timeout)
    : manager_(manager)
    , peer_instance_(peer_instance)
    , port_name_(port_name)
    , slot_(slot)
    , timeout_(timeout)
    , num_timeout_(0) {}

double ReceiveTimeoutHandler::get_timeout()
{
    // Increase timeout by a factor 1.5 with every timeout we hit:
    return timeout_ * std::pow(1.5, (double)num_timeout_);
}

void ReceiveTimeoutHandler::on_timeout()
{
    if (num_timeout_ == 0)
        manager_.waiting_for_receive(peer_instance_, port_name_, slot_);
    else
        if (manager_.is_deadlocked())
            throw Deadlock();
}

void ReceiveTimeoutHandler::on_receive()
{
    manager_.waiting_for_receive_done(peer_instance_, port_name_, slot_);
}

} }
