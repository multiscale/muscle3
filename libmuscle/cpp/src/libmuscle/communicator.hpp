#pragma once

#include <libmuscle/mcp/client.hpp>
#include <libmuscle/data.hpp>
#include <libmuscle/mcp/server.hpp>
#include <libmuscle/peer_manager.hpp>
#include <libmuscle/port.hpp>
#include <libmuscle/post_office.hpp>
#include <libmuscle/util.hpp>

#include <ymmsl/settings.hpp>

#include <string>
#include <unordered_map>
#include <vector>


namespace libmuscle {

/** A message to be sent or received.
 *
 * This class describes a message to be sent or that has been received.
 *
 * @attribute timestamp Simulation time for which this data is valid.
 * @attribute next_timestamp Simulation time for the next message to be
 *      transmitted through this port.
 * @attribute data An object to send or that was received.
 * @attribute settings Overlay settings to send or that were received.
 */
// Note: This is for communication with the user, it's not what actually goes
// out on the wire. See libmuscle::mcp::Message for that.
class Message {
    public:
        /** Create a Message.
         *
         * @param timestamp Simulation time for which this data is valid.
         * @param data An object to send or that was received.
         */
        Message(double timestamp, DataConstRef const & data);

        /** Create a Message.
         *
         * @param timestamp Simulation time for which this data is valid.
         * @param next_timestamp Simulation time for the next message to be
         *      transmitted through this port.
         * @param data An object to send or that was received.
         */
        Message(double timestamp,
                double next_timestamp,
                DataConstRef const & data);

        /** Create a Message.
         *
         * @param timestamp Simulation time for which this data is valid.
         * @param data An object to send or that was received.
         * @param settings Overlay settings to send or that were received.
         */
        Message(double timestamp,
                DataConstRef const & data,
                ymmsl::Settings const & settings);

        /** Create a Message.
         *
         * @param timestamp Simulation time for which this data is valid.
         * @param next_timestamp Simulation time for the next message to be
         *      transmitted through this port.
         * @param data An object to send or that was received.
         * @param settings Overlay settings to send or that were received.
         */
        Message(double timestamp,
                double next_timestamp,
                DataConstRef const & data,
                ymmsl::Settings const & settings);

        /** Returns the timestamp of the message.
         */
        double timestamp() const;

        /** Sets the timestamp of the message.
         *
         * @param timestamp The new value.
         */
        void set_timestamp(double timestamp);

        /** Returns whether the message has a next timestamp.
         */
        bool has_next_timestamp() const;

        /** Returns the next timestamp of the message.
         *
         * Only call if has_next_timestamp() returns true.
         *
         * @throw std::logic_error if the next timestamp is not set.
         */
        double next_timestamp() const;

        /** Sets the next timestamp of the message.
         *
         * @param next_timestamp The new value.
         */
        void set_next_timestamp(double next_timestamp);

        /** Unsets the next timestamp of the message.
         */
        void unset_next_timestamp();

        /** Returns the data of the message.
         */
        DataConstRef const & data() const;

        /** Returns whether the message carries settings.
         */
        bool has_settings() const;

        /** Returns the settings carried by the message.
         *
         * Only call if has_settings() returns true.
         */
        ::ymmsl::Settings const & settings() const;

    private:
        double timestamp_;
        Optional<double> next_timestamp_;
        DataConstRef data_;
        Optional<ymmsl::Settings> settings_;
};


/** A description of which ports a compute element has.
 *
 * You can create one like this:
 *
 * Ports ports({
 *     {Operator::F_INIT, {"port1", "port2"}},
 *     {Operator::O_F, {"port3[]"}}
 *     });
 *
 * and access elements as
 *
 * ports[Operator::F_INIT][0] == "port1";
 *
 * or for a const reference to a Ports
 *
 * ports.at(Operator::F_INIT)[1] == "port2";
 */
using PortsDescription = std::unordered_map<ymmsl::Operator, std::vector<std::string>>;


/** Communication engine for MUSCLE 3.
 *
 * This class is the mailroom for an instance that uses MUSCLE 3. It manages
 * the sending and receiving of messages, although it leaves the actual data
 * transmission to various protocol-specific servers and clients.
 */
class Communicator {
    public:
        /** Create a Communicator.
         *
         * The instance reference must start with one or more Identifiers,
         * giving the kernel id, followed by one or more integers which specify
         * the instance index.
         *
         * @param kernel The kernel this is the Communicator for.
         * @param index The index for this instance.
         * @param declared_ports The declared ports for this instance.
         * @param profiler The profiler to use for recording sends and receives.
         */
        // TODO: use actual Profiler
        Communicator(
                ymmsl::Reference const & kernel,
                std::vector<int> const & index,
                Optional<PortsDescription> const & declared_ports,
                int profiler);


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
         * @param conduits A list of conduits attached to this compute element,
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
        bool parameters_in_connected() const;

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

        /** Send a message and parameters to the outside world.
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

    private:
        using Ports_ = std::unordered_map<std::string, Port>;

        ymmsl::Reference instance_id_() const;
        Ports_ ports_from_declared_();
        Ports_ ports_from_conduits_(
                std::vector<ymmsl::Conduit> const & conduits) const;
        Port parameters_in_port_(std::vector<ymmsl::Conduit> const & conduits) const;
        mcp::Client & get_client_(ymmsl::Reference const & instance);

        Endpoint get_endpoint_(
                std::string const & port_name,
                std::vector<int> const & slot
                ) const;

        std::tuple<std::string, bool> split_port_desc_(
                std::string const & port_desc) const;

        ymmsl::Reference kernel_;
        std::vector<int> index_;
        Optional<PortsDescription> declared_ports_;
        PostOffice post_office_;
        int profiler_;
        std::vector<std::unique_ptr<mcp::Server>> servers_;
        std::unordered_map<ymmsl::Reference, std::unique_ptr<mcp::Client>> clients_;
        Ports_ ports_;
        std::unique_ptr<PeerManager> peer_manager_;
        Optional<Port> muscle_settings_in_;

        friend class TestCommunicator;
};

}

