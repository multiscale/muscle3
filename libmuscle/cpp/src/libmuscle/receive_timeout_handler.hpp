#pragma once

#include <libmuscle/mcp/transport_client.hpp>
#include <libmuscle/mmp_client.hpp>

namespace libmuscle { namespace _MUSCLE_IMPL_NS {

/** Timeout handler when receiving messages from peers.
 * 
 * This handler sends a message to the Muscle Manager when the receive times out (and
 * another message when the message does arrive).
 * 
 * This is used by the manager to detect if the simulation is in a deadlock, where a
 * cycle of instances is waiting on each other.
 */
class ReceiveTimeoutHandler : public mcp::TimeoutHandler {
    public:
        ReceiveTimeoutHandler(
                MMPClient & manager,
                std::string const & peer_instance,
                std::string const & port_name,
                Optional<int> slot,
                double timeout);

        virtual ~ReceiveTimeoutHandler() = default;

        double get_timeout() override;
        void on_timeout() override;
        void on_receive() override;

    private:
        MMPClient & manager_;
        std::string const & peer_instance_;
        std::string const & port_name_;
        Optional<int> slot_;
        double timeout_;

};

} }
