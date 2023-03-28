#pragma once

#ifdef LIBMUSCLE_MOCK_COMMUNICATOR
#include LIBMUSCLE_MOCK_COMMUNICATOR
#else

#include <libmuscle/data.hpp>
#include <libmuscle/logger.hpp>
#include <libmuscle/mcp/transport_server.hpp>
#include <libmuscle/message.hpp>
#include <libmuscle/mpp_client.hpp>
#include <libmuscle/peer_manager.hpp>
#include <libmuscle/port.hpp>
#include <libmuscle/ports_description.hpp>
#include <libmuscle/post_office.hpp>
#include <libmuscle/profiler.hpp>
#include <libmuscle/util.hpp>

#include <ymmsl/ymmsl.hpp>

#include <string>
#include <unordered_map>
#include <vector>


namespace libmuscle { namespace impl {

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
         * @param declared_ports The declared ports for this instance.
         * @param logger The logger for this instance.
         * @param profiler The profiler to use for recording sends and receives.
         */
        Communicator(
                ymmsl::Reference const & kernel,
                std::vector<int> const & index,
                Optional<PortsDescription> const & declared_ports,
                Logger & logger, Profiler & profiler);


        /** Returns a list of locations that we can be reached at.
         *
         * These locations are of the form 'protocol:location', where the
         * protocol name does not contain a colon and location may be an
         * arbitrary string.
         *
         * @return A list of strings describing network locations.
         */
        std::vector<std::string> get_locations() const;

        /** Connect this Communicator to its peers.
         *
         * This is the second stage in the simulation wiring process.
         *
         * Peers here are instances, and peer_dims and peer_locations are
         * indexed by a Reference to an instance. Instance sets are multi-
         * dimensional arrays with sizes given by peer_dims.
         *
         * @param conduits A list of conduits attached to this component,
         *      as received from the manager.
         * @param peer_dims For each peer we share a conduit with, the
         *      dimensions of the instance set.
         * @param peer_locations A list of locations for each peer instance we
         *      share a conduit with.
         */
        void connect(
                std::vector<ymmsl::Conduit> const & conduits,
                PeerDims const & peer_dims,
                PeerLocations const & peer_locations);

        /** Returns true iff muscle_settings_in is connected.
         */
        bool settings_in_connected() const;

        /** Returns a description of the ports this Communicator has.
         *
         * @return A map, indexed by Operator, containing lists of port names.
         *      Operators with no associated ports are not included.
         */
        PortsDescription list_ports() const;

        /** Returns whether a port with the given name exists.
         *
         * @param port_name Port name to check.
         */
        bool port_exists(std::string const & port_name) const;

        /** Returns a Port object describing a port with the given name.
         *
         * @param port The port to retrieve.
         */
        Port const & get_port(std::string const & port_name) const;

        /** Returns a Port object describing a port with the given name.
         *
         * @param port The port to retrieve.
         */
        Port & get_port(std::string const & port_name);

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
         */
        void send_message(
                std::string const & port_name,
                Message const & message,
                Optional<int> slot = {});

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
         *
         * @throws std::runtime_error if no default was given and the port is
         *      not connected.
         */
        Message receive_message(
                std::string const & port_name,
                Optional<int> slot = {},
                Optional<Message> const & default_msg = {}
                );

        /** Closes the given port.
         *
         * This signals to any connected instance that no more messages will
         * be sent on this port, which it can use to decide whether to shut
         * down or continue running.
         *
         * @param port_name The name of the port to close.
         */
        void close_port(std::string const & port_name, Optional<int> slot = {});

        /** Shuts down the Communicator, closing connections.
         */
        void shutdown();

        /** Get message counts for all ports on the communicator.
         */
        PortMessageCounts get_message_counts();

        /** Restore message counts on all ports.
         */
        void restore_message_counts(PortMessageCounts const & port_message_counts);

    private:
        using Ports_ = std::unordered_map<std::string, Port>;

        ymmsl::Reference instance_id_() const;
        Ports_ ports_from_declared_();
        Ports_ ports_from_conduits_(
                std::vector<ymmsl::Conduit> const & conduits) const;
        Port settings_in_port_(std::vector<ymmsl::Conduit> const & conduits) const;
        MPPClient & get_client_(ymmsl::Reference const & instance);

        Endpoint get_endpoint_(
                std::string const & port_name,
                std::vector<int> const & slot
                ) const;

        std::tuple<std::string, bool> split_port_desc_(
                std::string const & port_desc) const;

        std::tuple<DataConstRef, mcp::ProfileData> try_receive_(
                MPPClient & client, ymmsl::Reference const & receiver,
                ymmsl::Reference const & peer);

        ymmsl::Reference kernel_;
        std::vector<int> index_;
        Optional<PortsDescription> declared_ports_;
        PostOffice post_office_;
        Logger & logger_;
        Profiler & profiler_;
        std::vector<std::unique_ptr<mcp::TransportServer>> servers_;
        std::unordered_map<ymmsl::Reference, std::unique_ptr<MPPClient>> clients_;
        Ports_ ports_;
        std::unique_ptr<PeerManager> peer_manager_;
        Optional<Port> muscle_settings_in_;

        friend class TestCommunicator;
};

} }

#endif

