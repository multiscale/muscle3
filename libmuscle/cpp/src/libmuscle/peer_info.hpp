#pragma once

#ifdef LIBMUSCLE_MOCK_PEER_INFO
#include LIBMUSCLE_MOCK_PEER_INFO
#else

#include <ymmsl/ymmsl.hpp>

#include <libmuscle/endpoint.hpp>
#include <libmuscle/namespace.hpp>
#include <libmuscle/test_support.hpp>

#include <string>
#include <tuple>
#include <unordered_map>
#include <vector>


namespace libmuscle { namespace _MUSCLE_IMPL_NS {

using PeerDims = std::unordered_map<ymmsl::Reference, std::vector<int>>;
using PeerLocations = std::unordered_map<
        ymmsl::Reference, std::vector<std::string>>;
using IncomingPorts = std::vector<std::tuple<ymmsl::Identifier, ymmsl::Reference>>;
using OutgoingPorts = std::vector<
        std::tuple<ymmsl::Identifier, std::vector<ymmsl::Reference>>>;


/** Interprets information about peers for a Communicator.
 */
class PeerInfo {
    public:
        /** Create a PeerInfo.
         *
         * Peers here are instances, and peer_dims and peer_locations are
         * indexed by a Reference to an instance. Instance sets are multi-
         * dimensional arrays with sizes given by peer_dims.
         *
         * @param kernel The kernel for the instance whose peers we're managing.
         * @param index The index of the instance whose peers we're managing.
         * @param conduits A list of conduits attached to this component,
         *      as received from the manager.
         * @param peer_dims For each peer we share a conduit with, the dimensions
         *      of the instance set.
         * @param peer_locations A list of locations for each peer instance we
         *      share a conduit with.
         */
        PeerInfo(
                ymmsl::Reference const & kernel,
                std::vector<int> const & index,
                std::vector<ymmsl::Conduit> const & conduits,
                PeerDims const & peer_dims,
                PeerLocations const & peer_locations);

        /** List incoming ports.
         *
         * @return A vector of tuples containing a port id and a reference to the
         *      peer endpoint.
         */
        IncomingPorts list_incoming_ports() const;

        /** List outgoing ports.
         *
         * @return A vector of tuples containing a port id and a vector of references
         * to the peer endpoints.
         */
        OutgoingPorts list_outgoing_ports() const;

        /** Determine whether the given port is connected.
         *
         * @param port The port to check.
         * @return true iff the port is connected.
         */
        bool is_connected(ymmsl::Identifier const & port) const;

        /** Get a reference for all the peer ports.
         *
         * @param port Name of the port on this side.
         * @return Names of the port on the peers.
         */
        std::vector<ymmsl::Reference> const & get_peer_ports(
                ymmsl::Identifier const & port) const;

        /** Get the dimensions of a peer kernel.
         *
         * @param peer_kernel The peer kernel whose dimensions to get.
         */
        std::vector<int> get_peer_dims(ymmsl::Reference const & peer_kernel) const;

        /** Get the locations of a peer instance.
         *
         * There may be multiple, if the peer supports more than one protocol.
         *
         * @param peer_instance The instance whose locations to get.
         * @return A list of locations.
         */
        std::vector<std::string> get_peer_locations(
                ymmsl::Reference const & peer_instance) const;

        /** Determine the peer endpoints for the given port and slot.
         *
         * @param port The port on our side to send or receive on.
         * @param slot The slot to send or receive on.
         * @return The peer endpoints.
         */
        std::vector<Endpoint> get_peer_endpoints(
                ymmsl::Identifier const & port,
                std::vector<int> const & slot) const;

    PRIVATE:
        ymmsl::Reference kernel_;
        std::vector<int> index_;

        std::vector<ymmsl::Reference> incoming_ports_, outgoing_ports_;

        std::unordered_map<ymmsl::Reference, std::vector<ymmsl::Reference>> peers_;
        PeerDims peer_dims_;
        PeerLocations peer_locations_;
};

} }

#endif

