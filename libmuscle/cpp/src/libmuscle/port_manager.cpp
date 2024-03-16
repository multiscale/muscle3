#include <libmuscle/port_manager.hpp>

#include <cassert>
#include <limits>
#include <sstream>
#include <tuple>


using ymmsl::Conduit;
using ymmsl::Identifier;
using ymmsl::Operator;
using ymmsl::Reference;

using std::get;
using std::prev;


namespace libmuscle { namespace _MUSCLE_IMPL_NS {

PortManager::PortManager(
        std::vector<int> const & index,
        Optional<PortsDescription> const & declared_ports)
    : index_(index)
    , declared_ports_(declared_ports)
    , ports_()
{}

void PortManager::connect_ports(PeerInfo const & peer_info) {
    muscle_settings_in_ = settings_in_port_(peer_info);

    if (declared_ports_.is_set())
        ports_ = ports_from_declared_(peer_info);
    else
        ports_ = ports_from_conduits_(peer_info);
}

bool PortManager::settings_in_connected() const {
    return muscle_settings_in_.get().is_connected();
}

Port const & PortManager::muscle_settings_in() const {
    return muscle_settings_in_.get();
}

Port & PortManager::muscle_settings_in() {
    return muscle_settings_in_.get();
}

PortsDescription PortManager::list_ports() const {
    PortsDescription result;
    for (auto const & port : ports_)
        result[port.second.oper].emplace_back(port.first);
    return result;
}

bool PortManager::port_exists(std::string const & port_name) const {
    return ports_.count(port_name) > 0;
}

Port const & PortManager::get_port(std::string const & port_name) const {
    return ports_.at(port_name);
}

Port & PortManager::get_port(std::string const & port_name) {
    return ports_.at(port_name);
}

PortManager::PortMessageCounts PortManager::get_message_counts() {
    PortMessageCounts port_message_counts;
    for(auto const & port_item : ports_)
        port_message_counts[port_item.first] = port_item.second.get_message_counts();

    assert(muscle_settings_in_.is_set());  // is always created by connect_ports()
    auto counts = muscle_settings_in_.get().get_message_counts();
    port_message_counts["muscle_settings_in"] = counts;

    return port_message_counts;
}

void PortManager::restore_message_counts(
        PortManager::PortMessageCounts const & port_message_counts) {
    for (auto const & item : port_message_counts) {
        if (item.first == "muscle_settings_in") {
            assert(muscle_settings_in_.is_set());  // is always created by connect()
            muscle_settings_in_.get().restore_message_counts(item.second);
        } else {
            auto port_item = ports_.find(item.first);
            if (port_item != ports_.end()) {
                port_item->second.restore_message_counts(item.second);
            } else {
                throw std::runtime_error(
                        "Unknown port " + item.first + " in snapshot."
                        " Have your port definitions changed since"
                        " the snapshot was taken?");
            }
        }
    }
}


PortManager::Ports_ PortManager::ports_from_declared_(PeerInfo const & peer_info) const {
    Ports_ ports;
    for (auto const & ppo : declared_ports_.get()) {
        for (auto const & port_desc : ppo.second) {
            std::string port_name;
            bool is_vector;
            std::tie(port_name, is_vector) = split_port_desc_(port_desc);
            if (port_name.find("muscle_") == 0u) {
                std::ostringstream oss;
                oss << "Port names starting with 'muscle_' are reserved for";
                oss << " MUSCLE, please rename port '" << port_name << "'.";
                throw std::runtime_error(oss.str());
            }
            bool is_connected = peer_info.is_connected(port_name);
            std::vector<int> port_peer_dims;
            if (is_connected) {
                auto peer_ports = peer_info.get_peer_ports(port_name);
                Reference peer_port = peer_ports.at(0);
                Reference peer_component(
                        peer_port.cbegin(), std::prev(peer_port.cend()));
                port_peer_dims = peer_info.get_peer_dims(peer_component);
                for (std::size_t i = 1; i < peer_ports.size(); i++) {
                    peer_port = peer_ports.at(i);
                    peer_component = Reference(
                            peer_port.cbegin(), std::prev(peer_port.cend()));
                    if (port_peer_dims != peer_info.get_peer_dims(peer_component)) {
                        std::stringstream ss;
                        ss << "Multicast port \"" << port_name;
                        ss << "\" is connected to peers with different";
                        ss << " dimensions. All peer components that this";
                        ss << " port is connected to must have the same";
                        ss << " multiplicity. Connected to ports: ";
                        bool first = true;
                        for (auto port : peer_ports) {
                            if (first)
                                first = false;
                            else
                                ss << ", ";
                            ss << port;
                        }
                        throw std::runtime_error(ss.str());
                    }
                }
            }
            ports.emplace(port_name, Port(
                    port_name, ppo.first, is_vector, is_connected,
                    index_.size(), port_peer_dims));
        }
    }
    return ports;
}

PortManager::Ports_ PortManager::ports_from_conduits_(PeerInfo const & peer_info) const {
    Ports_ ports;

    auto make_port = [&](
            Identifier const & port_id, Operator oper,
            std::vector<int> const & peer_dims) {
        int ndims = std::max(std::vector<int>::size_type(0u), peer_dims.size() - index_.size());
        bool is_vector = (ndims == 1);
        bool is_connected = peer_info.is_connected(port_id);
        if (std::string(port_id).find("muscle_") != 0u) {
            ports.emplace(port_id, Port(
                    port_id, oper, is_vector, is_connected, index_.size(), peer_dims));
        }
    };

    for (auto const & port_sender : peer_info.list_incoming_ports()) {
        std::string port_name(get<0>(port_sender));
        Reference sending_component(
                get<1>(port_sender).cbegin(), prev(get<1>(port_sender).cend()));

        auto const & peer_dims = peer_info.get_peer_dims(sending_component);
        make_port(get<0>(port_sender), Operator::F_INIT, peer_dims);
    }

    for (auto const & port_recvs : peer_info.list_outgoing_ports()) {
        std::string port_name(get<0>(port_recvs));
        Reference receiving_component(
                get<1>(port_recvs)[0].cbegin(),
                prev(get<1>(port_recvs)[0].cend()));

        auto const & peer_dims = peer_info.get_peer_dims(receiving_component);
        make_port(get<0>(port_recvs), Operator::O_F, peer_dims);
    }

    return ports;
}

Port PortManager::settings_in_port_(PeerInfo const & peer_info) const {
    Identifier msi("muscle_settings_in");
    if (peer_info.is_connected(msi)) {
            Reference sender_port = peer_info.get_peer_ports(msi)[0];
            Reference sender_component(
                    sender_port.cbegin(), std::prev(sender_port.cend()));
            return Port(
                    std::string(msi), Operator::F_INIT, false, true, index_.size(), {});
    }
    return Port(std::string(msi), Operator::F_INIT, false, false, index_.size(), {});
}

std::tuple<std::string, bool> PortManager::split_port_desc_(
        std::string const & port_desc) const {
    std::string port_name(port_desc);
    bool is_vector = false;

    auto found = port_desc.rfind("[]");
    if (found != std::string::npos && found == (port_desc.size() - 2)) {
        is_vector = true;
        port_name = port_desc.substr(0, port_desc.size() - 2);
    }

    found = port_name.rfind("[]");
    if (found != std::string::npos && found == (port_name.size() - 2)) {
        std::ostringstream oss;
        oss << "Port description '" << port_desc << "' is invalid: ports can";
        oss << " have at most one dimension.";
        throw std::invalid_argument(oss.str());
    }

    return std::make_tuple(port_name, is_vector);
}

} }

