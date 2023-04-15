#include <mocks/mock_peer_manager.hpp>


using ymmsl::Conduit;
using ymmsl::Identifier;
using ymmsl::Reference;


namespace libmuscle { namespace _MUSCLE_IMPL_NS {

MockPeerManager::MockPeerManager(
        Reference const & kernel,
        std::vector<int> const & index,
        std::vector<Conduit> const & conduits,
        PeerDims const & peer_dims,
        PeerLocations const & peer_locations
        )
{
    ++num_constructed;
    last_constructed_kernel_id = kernel;
    last_constructed_index = index;
    last_constructed_conduits = conduits;
    last_constructed_peer_dims = peer_dims;
    last_constructed_peer_locations = peer_locations;
}

bool MockPeerManager::is_connected(Identifier const & port) const {
    return is_connected_return_value;
}

std::vector<Reference> MockPeerManager::get_peer_ports(Identifier const & port) const {
    return get_peer_port_table.at(port);
}

std::vector<int> MockPeerManager::get_peer_dims(
        Reference const & peer_kernel) const {
    return get_peer_dims_table.at(peer_kernel);
}

std::vector<std::string> MockPeerManager::get_peer_locations(
        Reference const & peer_instance) const {
    return std::vector<std::string>({std::string("tcp:test")});
}

std::vector<Endpoint> MockPeerManager::get_peer_endpoints(
        Identifier const & port,
        std::vector<int> const & slot
        ) const
{
    Reference port_slot(port);
    port_slot += slot;
    return get_peer_endpoint_table.at(port_slot);
}

void MockPeerManager::reset() {
    num_constructed = 0;
    last_constructed_kernel_id = "_none";
    last_constructed_index.clear();
    last_constructed_conduits.clear();
    last_constructed_peer_dims.clear();
    last_constructed_peer_locations.clear();

    is_connected_return_value = true;
    get_peer_port_table.clear();
    get_peer_dims_table.clear();
    get_peer_endpoint_table.clear();
}

int MockPeerManager::num_constructed = 0;
Reference MockPeerManager::last_constructed_kernel_id("_none");
std::vector<int> MockPeerManager::last_constructed_index;
std::vector<Conduit> MockPeerManager::last_constructed_conduits;
PeerDims MockPeerManager::last_constructed_peer_dims;
PeerLocations MockPeerManager::last_constructed_peer_locations;

bool MockPeerManager::is_connected_return_value;
std::unordered_map<Identifier, std::vector<Reference>> MockPeerManager::get_peer_port_table;
std::unordered_map<Reference, std::vector<int>> MockPeerManager::get_peer_dims_table;
std::unordered_map<Reference, std::vector<Endpoint>> MockPeerManager::get_peer_endpoint_table;

} }

