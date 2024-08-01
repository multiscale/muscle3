#pragma once

#ifdef LIBMUSCLE_MOCK_PORT_MANAGER
#include LIBMUSCLE_MOCK_PORT_MANAGER
#else

#include <libmuscle/namespace.hpp>
#include <libmuscle/peer_info.hpp>
#include <libmuscle/port.hpp>
#include <libmuscle/ports_description.hpp>
#include <libmuscle/test_support.hpp>

#include <ymmsl/ymmsl.hpp>

#include <string>
#include <unordered_map>
#include <vector>


namespace libmuscle { namespace _MUSCLE_IMPL_NS {

/** Manages sending and receiving ports of the current instance.
 */
class PortManager {
    public:
        using PortMessageCounts = std::unordered_map<std::string, std::vector<int>>;

        /** Create a PortManager.
         *
         * @param index The index for this instance.
         * @param declared_ports The declared ports for this instance.
         */
        PortManager(
                std::vector<int> const & index,
                Optional<PortsDescription> const & declared_ports);


        /** Connect this Communicator to its peers.
         *
         * This is the second stage in the simulation wiring process.
         *
         * Peers here are instances, and the information about them received
         * from the manager is in peer_info. We are going to create a set of
         * Port objects here, one for each of our ports.
         *
         * If the user gave us a set of ports (i.e. they were declared in the
         * code) then we'll create a Port object for each of those, with
         * information about the attached conduit / peer (if any) from
         * peer_info. If the user did not give us any ports (which is legal),
         * then the ports will be created entirely from the information
         * received from the manager. The user then has to use
         * Instance.list_ports() to see what ports they got, and do something
         * with them.
         *
         * @param peer_info Information about our peers from the manager.
         */
        void connect_ports(PeerInfo const & peer_info);

        /** Returns whether muscle_settings_in is connected.
         */
        bool settings_in_connected() const;

        /** Returns the muscle_settings_in port.
         */
        Port const & muscle_settings_in() const;

        /** Returns the muscle_settings_in port.
         */
        Port & muscle_settings_in();

        /** Returns a description of the ports this PortManager has.
         *
         * @return A map, indexed by Operator, containing lists of port names.
         *      Operators with no associated ports are not included.
         */
        PortsDescription list_ports() const;

        /** Returns whether a port with the given name exists.
         *
         * @param port_name Port name to check.
         *
         * @return True iff the port exists
         */
        bool port_exists(std::string const & port_name) const;

        /** Returns a Port object describing a port with the given name.
         *
         * @param port_name Name of the port to retrieve.
         *
         * @return A Port object for the port
         */
        Port const & get_port(std::string const & port_name) const;

        /** Returns a Port object describing a port with the given name.
         *
         * @param port_name Name of the port to retrieve.
         *
         * @return A Port object for the port
         */
        Port & get_port(std::string const & port_name);

        /** Get message counts for all ports on the communicator.
         *
         * @return A map indexed by port name containing a list of counts, one
         *      for each slot of the corresponding port.
         */
        PortMessageCounts get_message_counts();

        /** Restore message counts on all ports.
         *
         * @param port_message_counts: The message counts, as a map indexed by
         *      port name containing a vector of counts, one for each slot.
         */
        void restore_message_counts(PortMessageCounts const & port_message_counts);

    PRIVATE:
        using Ports_ = std::unordered_map<std::string, Port>;

        Ports_ ports_from_declared_(PeerInfo const & peer_info) const;
        Ports_ ports_from_conduits_(PeerInfo const & peer_info) const;
        Port settings_in_port_(PeerInfo const & peer_info) const;

        std::tuple<std::string, bool> split_port_desc_(
                std::string const & port_desc) const;

        std::vector<int> index_;
        Optional<PortsDescription> declared_ports_;
        Ports_ ports_;
        Optional<Port> muscle_settings_in_;

        friend class PortManagerTestAccess;
};

} }

#endif

