#include <libmuscle/peer_manager.hpp>

#include <sstream>

using ymmsl::Conduit;
using ymmsl::Identifier;
using ymmsl::Reference;


namespace libmuscle { namespace _MUSCLE_IMPL_NS {

PeerManager::PeerManager(
        Reference const & kernel,
        std::vector<int> const & index,
        std::vector<Conduit> const & conduits,
        PeerDims const & peer_dims,
        PeerLocations const & peer_locations
        )
    : kernel_(kernel)
    , index_(index)
    , peers_()                          // peer port ids, indexed by local kernel.port
    , peer_dims_(peer_dims)             // indexed by peer kernel id
    , peer_locations_(peer_locations)   // indexed by peer instance id
{
    for (auto const & conduit : conduits) {
        if (conduit.sending_component() == kernel_) {
            // we send on the port this conduit attaches to
            auto search = peers_.find(conduit.sender);
            if (search == peers_.end())
                search = peers_.emplace(
                        conduit.sender, std::vector<Reference>()).first;
            search->second.push_back(conduit.receiver);
        }
        if (conduit.receiving_component() == kernel_) {
            // we receive on the port this conduit attaches to
            if (peers_.count(conduit.receiver)) {
                std::stringstream ss;
                ss << "Receiving port \"" << conduit.receiving_port();
                ss << "\" is connected by multiple conduits, but at most one";
                ss << " is allowed.";
                throw std::runtime_error(ss.str());
            }
            std::vector<Reference> vec = {conduit.sender};
            peers_.emplace(conduit.receiver, vec);
        }
    }
}

bool PeerManager::is_connected(Identifier const & port) const {
    return peers_.count(kernel_ + port);
}

 std::vector<ymmsl::Reference> const & PeerManager::get_peer_ports(
            Identifier const & port) const {
    return peers_.at(kernel_ + port);
}

std::vector<int> PeerManager::get_peer_dims(
        Reference const & peer_kernel) const {
    return peer_dims_.at(peer_kernel);
}

std::vector<std::string> PeerManager::get_peer_locations(
        Reference const & peer_instance) const {
    return peer_locations_.at(peer_instance);
}

std::vector<Endpoint> PeerManager::get_peer_endpoints(
        Identifier const & port,
        std::vector<int> const & slot
        ) const
{
    auto peers = peers_.at(kernel_ + port);
    std::vector<Endpoint> endpoints;

    for (auto peer : peers) {
        Reference peer_kernel(peer.cbegin(), std::prev(peer.cend()));
        Identifier peer_port = std::prev(peer.cend())->identifier();

        std::vector<int> total_index = index_;
        total_index.insert(total_index.end(), slot.cbegin(), slot.cend());

        // rebalance the indices
        int peer_dim = peer_dims_.at(peer_kernel).size();
        auto peer_dim_it = std::next(total_index.cbegin(), peer_dim);
        std::vector<int> peer_index(total_index.cbegin(), peer_dim_it);
        std::vector<int> peer_slot(peer_dim_it, total_index.cend());
        endpoints.emplace_back(peer_kernel, peer_index, peer_port, peer_slot);
    }

    return endpoints;
}

} }

