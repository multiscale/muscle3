#pragma once

#ifdef LIBMUSCLE_MOCK_COMMUNICATOR
#include LIBMUSCLE_MOCK_COMMUNICATOR
#else

#include <libmuscle/logger.hpp>
#include <libmuscle/message.hpp>
#include <libmuscle/mmp_client.hpp>
#include <libmuscle/mpp_client.hpp>
#include <libmuscle/mpp_server.hpp>
#include <libmuscle/namespace.hpp>
#include <libmuscle/peer_info.hpp>
#include <libmuscle/port.hpp>
#include <libmuscle/port_manager.hpp>
#include <libmuscle/ports_description.hpp>
#include <libmuscle/profiler.hpp>
#include <libmuscle/receive_timeout_handler.hpp>
#include <libmuscle/test_support.hpp>
#include <libmuscle/util.hpp>

#include <ymmsl/ymmsl.hpp>

#include <string>
#include <tuple>
#include <unordered_map>
#include <vector>


namespace libmuscle { namespace _MUSCLE_IMPL_NS {

/** Communication engine for MUSCLE3.
 *
 * This class is the mailroom for an instance that uses MUSCLE3. It manages
 * the sending and receiving of messages, although it leaves the actual data
 * transmission to various protocol-specific servers and clients.
 */
class Communicator {
    public:
        using PortMessageCounts = std::unordered_map<std::string, std::vector<int>>;

        /** Create a Communicator.
         *
         * The instance reference must start with one or more Identifiers,
         * giving the kernel id, followed by one or more integers which specify
         * the instance index.
         *
         * @param kernel The kernel this is the Communicator for.
         * @param index The index for this instance.
         * @param port_manager The PortManager to use.
         * @param logger The logger for this instance.
         * @param profiler The profiler to use for recording sends and receives.
         */
        Communicator(
                ymmsl::Reference const & kernel,
                std::vector<int> const & index,
                PortManager & port_manager,
                Logger & logger, Profiler & profiler,
                MMPClient & manager);

        /** Returns a list of locations that we can be reached at.
         *
         * These locations are of the form 'protocol:location', where the
         * protocol name does not contain a colon and location may be an
         * arbitrary string.
         *
         * @return A list of strings describing network locations.
         */
        std::vector<std::string> get_locations() const;

        /** Inform this Communicator about its peers.
         *
         * This tells the Communicator about its peers, so that it can route
         * messages accordingly.
         *
         * @param peer_info Information about the peers.
         */
        void set_peer_info(PeerInfo const & peer_info);

        /** Send a message and settings to the outside world.
         *
         * Sending is non-blocking, a copy of the message will be made and
         * stored until the receiver is ready to receive it.
         *
         * Message must have its settings attribute set.
         *
         * @param port_name The port on which this message is to be sent.
         * @param message The message to send.
         * @param slot The slot to send the message on.
         * @param checkpoints_considered_until When we last checked if we
         *      should save a snapshot (wallclock time).
         */
        void send_message(
                std::string const & port_name,
                Message const & message,
                Optional<int> slot = {},
                double checkpoints_considered_until = -std::numeric_limits<double>::infinity());

        /** Receive a message and attached settings overlay.
         *
         * Receiving is a blocking operation. This function will contact the
         * sender, wait for a message to be available, and receive and return
         * it.
         *
         * If the port is not connected, then the default value will be
         * returned if one was given, exactly as it was given. If no default
         * was given then a std::runtime_error will be raised.
         *
         * This is non-const, because receiving a message may cause an update
         * to the dimensions of the port.
         *
         * @param port_name The endpoint on which a message is to be received.
         * @param slot The slot to receive the message on, if any.
         * @param default_msg A message to return if the port is not connected.
         *
         * @return The received message, with message.settings holding the
         *      settings overlay. The setings attribute is guaranteed to be set.
         *      Second, the saved_until metadata field from the received message.
         *
         * @throws std::runtime_error if no default was given and the port is
         *      not connected.
         */
        std::tuple<Message, double> receive_message(
                std::string const & port_name,
                Optional<int> slot = {},
                Optional<Message> const & default_msg = {}
                );

        /** Shuts down the Communicator, closing connections.
         */
        void shutdown();

        /** Update the timeout after which the manager is notified that we are
         * waiting for a message.
         * 
         * @param receive_timeout Timeout (seconds). A negative number disables
         *      the deadlock notification mechanism.
         */
        void set_receive_timeout(double receive_timeout) { receive_timeout_ = receive_timeout; }

        /** Get the timeout after which the manager is notified that we are
         * waiting for a message.
         */
        double get_receive_timeout() const { return receive_timeout_; }

    PRIVATE:
        using Ports_ = std::unordered_map<std::string, Port>;

        ymmsl::Reference instance_id_() const;
        MPPClient & get_client_(ymmsl::Reference const & instance);

        Endpoint get_endpoint_(
                std::string const & port_name,
                std::vector<int> const & slot
                ) const;

        std::tuple<std::vector<char>, mcp::ProfileData> try_receive_(
                MPPClient & client, ymmsl::Reference const & receiver,
                ymmsl::Reference const & peer, ReceiveTimeoutHandler *handler);

        void close_port_(std::string const & port_name, Optional<int> slot = {});

        /* Closes outgoing ports.
         *
         * This sends a close port message on all slots of all outgoing ports.
         */
        void close_outgoing_ports_();

        /* Receives messages until a ClosePort is received.
         *
         * Receives at least once.
         *
         * @param port_name Port to drain.
         */
        void drain_incoming_port_(std::string const & port_name);

        /* Receives messages until a ClosePort is received.
         *
         * Works with (resizable) vector ports.
         *
         * @param port_name Port to drain.
         */
        void drain_incoming_vector_port_(std::string const & port_name);

        /* Closes incoming ports.
         *
         * This receives on all incoming ports until a ClosePort is received on them,
         * signaling that there will be no more messages, and allowing the sending
         * instance to shut down cleanly.
         */
        void close_incoming_ports_();

        /* Closes all ports.
         *
         * This sends a close port message on all slots of all outgoing ports, then
         * receives one on all incoming ports.
         */
        void close_ports_();

        ymmsl::Reference kernel_;
        std::vector<int> index_;
        PortManager & port_manager_;
        Logger & logger_;
        Profiler & profiler_;
        MMPClient & manager_;
        MPPServer server_;
        std::unordered_map<ymmsl::Reference, std::unique_ptr<MPPClient>> clients_;
        Optional<PeerInfo> peer_info_;
        double receive_timeout_;
};

} }

#endif

