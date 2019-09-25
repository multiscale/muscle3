#pragma once

#include <ymmsl/identity.hpp>
#include <ymmsl/model.hpp>

#include <libmuscle/endpoint.hpp>

#include <string>
#include <unordered_map>
#include <vector>


namespace libmuscle {

using PeerDims = std::unordered_map<ymmsl::Reference, std::vector<int>>;
using PeerLocations = std::unordered_map<
        ymmsl::Reference, std::vector<std::string>>;

class MockPeerManager {
    public:
        MockPeerManager(
                ymmsl::Reference const & kernel,
                std::vector<int> const & index,
                std::vector<ymmsl::Conduit> const & conduits,
                PeerDims const & peer_dims,
                PeerLocations const & peer_locations);

        bool is_connected(ymmsl::Identifier const & port) const;

        ymmsl::Reference get_peer_port(ymmsl::Identifier const & port) const;

        std::vector<int> get_peer_dims(ymmsl::Reference const & peer_kernel) const;

        std::vector<std::string> get_peer_locations(
                ymmsl::Reference const & peer_instance) const;

        Endpoint get_peer_endpoint(
                ymmsl::Identifier const & port,
                std::vector<int> const & slot) const;

        // Mock control variables
        static void reset();

        static int num_constructed;
        static ymmsl::Reference last_constructed_kernel_id;
        static std::vector<int> last_constructed_index;
        static std::vector<ymmsl::Conduit> last_constructed_conduits;
        static PeerDims last_constructed_peer_dims;
        static PeerLocations last_constructed_peer_locations;

        static bool is_connected_return_value;
        static std::unordered_map<ymmsl::Identifier, ymmsl::Reference>
            get_peer_port_table;
        static std::unordered_map<ymmsl::Reference, std::vector<int>>
            get_peer_dims_table;
        static std::unordered_map<ymmsl::Reference, Endpoint>
            get_peer_endpoint_table;
};

using PeerManager = MockPeerManager;

}

