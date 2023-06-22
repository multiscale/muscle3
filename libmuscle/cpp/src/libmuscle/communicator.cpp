#include <libmuscle/communicator.hpp>

#include <libmuscle/close_port.hpp>
#include <libmuscle/data.hpp>
#include <libmuscle/mcp/ext_types.hpp>
#include <libmuscle/mpp_message.hpp>
#include <libmuscle/mcp/tcp_transport_server.hpp>
#include <libmuscle/mpp_client.hpp>
#include <libmuscle/profiling.hpp>

#include <limits>
#include <sstream>


using libmuscle::_MUSCLE_IMPL_NS::ClosePort;
using libmuscle::_MUSCLE_IMPL_NS::Data;
using libmuscle::_MUSCLE_IMPL_NS::DataConstRef;
using libmuscle::_MUSCLE_IMPL_NS::mcp::ExtTypeId;
using libmuscle::_MUSCLE_IMPL_NS::MPPClient;
using libmuscle::_MUSCLE_IMPL_NS::mcp::TcpTransportServer;

using ymmsl::Conduit;
using ymmsl::Identifier;
using ymmsl::Operator;
using ymmsl::Reference;
using ymmsl::Settings;


namespace libmuscle { namespace _MUSCLE_IMPL_NS {

Communicator::Communicator(
        ymmsl::Reference const & kernel,
        std::vector<int> const & index,
        Optional<PortsDescription> const & declared_ports,
        Logger & logger, Profiler & profiler)
    : kernel_(kernel)
    , index_(index)
    , declared_ports_(declared_ports)
    , logger_(logger)
    , profiler_(profiler)
    , servers_()
    , clients_()
    , ports_()
{
    servers_.emplace_back(new TcpTransportServer(post_office_));
}

std::vector<std::string> Communicator::get_locations() const {
    std::vector<std::string> result;
    for (auto const & server : servers_)
        result.emplace_back(server->get_location());
    return result;
}

void Communicator::connect(
        std::vector<Conduit> const & conduits,
        PeerDims const & peer_dims,
        PeerLocations const & peer_locations)
{
    peer_manager_ = std::make_unique<PeerManager>(
            kernel_, index_, conduits, peer_dims, peer_locations);

    if (declared_ports_.is_set())
        ports_ = ports_from_declared_();
    else
        ports_ = ports_from_conduits_(conduits);

    muscle_settings_in_ = settings_in_port_(conduits);
}

bool Communicator::settings_in_connected() const {
    return muscle_settings_in_.get().is_connected();
}

PortsDescription Communicator::list_ports() const {
    PortsDescription result;
    for (auto const & port : ports_)
        result[port.second.oper].emplace_back(port.first);
    return result;
}

bool Communicator::port_exists(std::string const & port_name) const {
    return ports_.count(port_name) > 0;
}

Port const & Communicator::get_port(std::string const & port_name) const {
    return ports_.at(port_name);
}

Port & Communicator::get_port(std::string const & port_name) {
    return ports_.at(port_name);
}

void Communicator::send_message(
        std::string const & port_name,
        Message const & message,
        Optional<int> slot)
{
    if (slot.is_set())
        logger_.debug("Sending message on ", port_name, "[", slot.get(), "]");
    else
        logger_.debug("Sending message on ", port_name);
    std::vector<int> slot_list;
    if (slot.is_set()) {
        slot_list.push_back(slot.get());
        int slot_length = ports_.at(port_name).get_length();
        if (slot_length <= slot.get()) {
            std::ostringstream oss;
            oss << "Slot out of bounds. You are sending on slot " << slot;
            oss << " of port '" << port_name << "', which is of length";
            oss << " " << slot_length << ", so that slot does not exist.";
            throw std::runtime_error(oss.str());
        }
    }

    Endpoint snd_endpoint = get_endpoint_(port_name, slot_list);
    if (!peer_manager_->is_connected(snd_endpoint.port))
        // log sending on disconnected port
        return;

    Port & port = ports_.at(port_name);

    ProfileEvent profile_event(
            ProfileEventType::send, ProfileTimestamp(), {}, port, {}, slot,
            port.get_num_messages(), {}, message.timestamp());

    auto recv_endpoints = peer_manager_->get_peer_endpoints(
            snd_endpoint.port, slot_list);

    Data settings_overlay(message.settings());

    Optional<int> port_length;
    if (port.is_resizable())
        port_length = port.get_length();

    for (auto recv_endpoint : recv_endpoints) {
        MPPMessage mpp_message(
                snd_endpoint.ref(), recv_endpoint.ref(),
                port_length, message.timestamp(), Optional<double>(),
                settings_overlay, port.get_num_messages(slot), -1.0,
                message.data());

        if (message.has_next_timestamp())
            mpp_message.next_timestamp = message.next_timestamp();

        auto message_bytes = std::make_unique<DataConstRef>(mpp_message.encoded());
        profile_event.message_size = message_bytes->size();
        post_office_.deposit(recv_endpoint.ref(), std::move(message_bytes));
    }

    port.increment_num_messages(slot);

    profile_event.stop();
    if (port.is_vector())
        profile_event.port_length = port.get_length();
    if (!is_close_port(message.data()))
        profiler_.record_event(std::move(profile_event));
}

Message Communicator::receive_message(
        std::string const & port_name,
        Optional<int> slot,
        Optional<Message> const & default_msg)
{
    if (slot.is_set())
        logger_.debug("Waiting for message on ", port_name, "[", slot.get(), "]");
    else
        logger_.debug("Waiting for message on ", port_name);
    std::vector<int> slot_list;
    if (slot.is_set())
        slot_list.emplace_back(slot.get());

    Endpoint recv_endpoint(get_endpoint_(port_name, slot_list));

    if (!peer_manager_->is_connected(recv_endpoint.port)) {
        if (!default_msg.is_set()) {
            std::ostringstream oss;
            oss << "Tried to receive on port '" << port_name << "', which is";
            oss << " disconnected, and no default value was given. Either";
            oss << " specify a default, or connect a sending component to";
            oss << " this port.";
            throw std::runtime_error(oss.str());
        }
        else {
            logger_.debug("No message received on ", port_name, " as it is not connected");
            return default_msg.get();
        }
    }

    Port & port = (ports_.count(port_name)) ? (ports_.at(port_name)) : muscle_settings_in_.get();

    ProfileEvent receive_event(
            ProfileEventType::receive, ProfileTimestamp(), {}, port, {}, slot,
            port.get_num_messages());

    // peer_manager already checks that there is at most one snd_endpoint
    // connected to the port we receive on
    Endpoint snd_endpoint = peer_manager_->get_peer_endpoints(
            recv_endpoint.port, slot_list).at(0);
    MPPClient & client = get_client_(snd_endpoint.instance());
    auto msg_and_profile = try_receive_(
            client, recv_endpoint.ref(), snd_endpoint.kernel);
    auto & msg = std::get<0>(msg_and_profile);

    ProfileEvent recv_decode_event(
            ProfileEventType::receive_decode, ProfileTimestamp(), {}, port, {}, slot,
            port.get_num_messages(), msg.size());

    auto mpp_message = MPPMessage::from_bytes(msg);
    Settings overlay_settings(mpp_message.settings_overlay.as<Settings>());

    recv_decode_event.stop();

    if (mpp_message.port_length.is_set())
        if (port.is_resizable())
            port.set_length(mpp_message.port_length.get());

    Message message(
            mpp_message.timestamp, mpp_message.data, overlay_settings);

    if (mpp_message.next_timestamp.is_set())
        message.set_next_timestamp(mpp_message.next_timestamp.get());

    if (is_close_port(message.data())) {
        if (slot.is_set())
            port.set_closed(slot.get());
        else
            port.set_closed();
    }

    ProfileTimestamp start_recv, end_wait, end_transfer;
    std::tie(start_recv, end_wait, end_transfer) = std::get<1>(msg_and_profile);
    ProfileEvent recv_wait_event(
            ProfileEventType::receive_wait, start_recv,
            end_wait, port, mpp_message.port_length, slot,
            port.get_num_messages(), msg.size(), message.timestamp());

    ProfileEvent recv_xfer_event(
            ProfileEventType::receive_transfer, end_wait,
            end_transfer, port, mpp_message.port_length, slot,
            port.get_num_messages(), msg.size(), message.timestamp());

    recv_decode_event.message_timestamp = message.timestamp();
    receive_event.message_timestamp = message.timestamp();

    if (port.is_vector()) {
        receive_event.port_length = port.get_length();
        recv_wait_event.port_length = port.get_length();
        recv_xfer_event.port_length = port.get_length();
        recv_decode_event.port_length = port.get_length();
    }

    receive_event.message_size = std::get<0>(msg_and_profile).size();

    if (!is_close_port(message.data())) {
        profiler_.record_event(std::move(recv_wait_event));
        profiler_.record_event(std::move(recv_xfer_event));
        profiler_.record_event(std::move(recv_decode_event));
        profiler_.record_event(std::move(receive_event));
    }

    int expected_message_number = port.get_num_messages(slot);
    if (expected_message_number != mpp_message.message_number) {
        if (expected_message_number - 1 == mpp_message.message_number and
                port.is_resuming(slot)) {
            if (slot.is_set())
                logger_.debug("Discarding received message on ", port_name,
                              "[", slot.get(), "]: resuming from weakly",
                              " consistent snapshot");
            else
                logger_.debug("Discarding received message on ", port_name,
                              ": resuming from weakly constistent snapshot");
            port.set_resumed(slot);
            return receive_message(port_name, slot, default_msg);
        }
        std::ostringstream oss;
        oss << "Received message on " << port_name;
        if (slot.is_set())
            oss << "[" << slot.get() << "]";
        oss << " with unexpected message number " << mpp_message.message_number;
        oss << ". Was expecting " << expected_message_number;
        oss << ". Are you resuming from an inconsistent snapshot?";
        throw std::runtime_error(oss.str());
    }
    port.increment_num_messages(slot);

    if (slot.is_set())
        logger_.debug("Received message on ", port_name, "[", slot.get(), "]");
    else
        logger_.debug("Received message on ", port_name);

    if (is_close_port(message.data())) {
        if (slot.is_set())
            logger_.debug("Port ", port_name, "[", slot.get(), "] is now closed");
        else
            logger_.debug("Port ", port_name, " is now closed");
    }
    return message;
}

void Communicator::close_port(
        std::string const & port_name, Optional<int> slot) {
    Message message(
            std::numeric_limits<double>::infinity(),
            ClosePort(), Settings());
    if (slot.is_set())
        logger_.debug("Closing port ", port_name, "[", slot.get(), "]");
    else
        logger_.debug("Closing port ", port_name);
    send_message(port_name, message, slot);
}

void Communicator::shutdown() {
    for (auto & client : clients_)
        client.second->close();

    post_office_.wait_for_receivers();

    for (auto & server : servers_)
        server->close();
}

Communicator::PortMessageCounts Communicator::get_message_counts() {
    PortMessageCounts port_message_counts;
    for(auto const & port_item : ports_)
        port_message_counts[port_item.first] = port_item.second.get_message_counts();

    assert(muscle_settings_in_.is_set());  // is always created by connect()
    auto counts = muscle_settings_in_.get().get_message_counts();
    port_message_counts["muscle_settings_in"] = counts;

    return port_message_counts;
}

void Communicator::restore_message_counts(
        Communicator::PortMessageCounts const & port_message_counts) {
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


Reference Communicator::instance_id_() const {
    return kernel_ + index_;
}

Communicator::Ports_ Communicator::ports_from_declared_() {
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
            bool is_connected = peer_manager_->is_connected(port_name);
            std::vector<int> port_peer_dims;
            if (is_connected) {
                auto peer_ports = peer_manager_->get_peer_ports(port_name);
                Reference peer_port = peer_ports.at(0);
                Reference peer_ce(peer_port.cbegin(), std::prev(peer_port.cend()));
                port_peer_dims = peer_manager_->get_peer_dims(peer_ce);
                for (std::size_t i = 1; i < peer_ports.size(); i++) {
                    peer_port = peer_ports.at(i);
                    peer_ce = Reference(peer_port.cbegin(), std::prev(peer_port.cend()));
                    if (port_peer_dims != peer_manager_->get_peer_dims(peer_ce)) {
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

Communicator::Ports_ Communicator::ports_from_conduits_(
        std::vector<Conduit> const & conduits) const {
    Ports_ ports;
    for (auto const & conduit : conduits) {
        Identifier port_id("muscle_none");
        Operator oper;
        std::vector<int> port_peer_dims;

        if (conduit.sending_component() == kernel_) {
            port_id = conduit.sending_port();
            oper = Operator::O_F;
            port_peer_dims = peer_manager_->get_peer_dims(
                    conduit.receiving_component());
        }
        else if (conduit.receiving_component() == kernel_) {
            port_id = conduit.receiving_port();
            oper = Operator::F_INIT;
            port_peer_dims = peer_manager_->get_peer_dims(
                    conduit.sending_component());
        }
        else
            continue;
        int ndims = std::max(std::vector<int>::size_type(0u), port_peer_dims.size() - index_.size());
        bool is_vector = (ndims == 1);
        bool is_connected = peer_manager_->is_connected(port_id);
        if (std::string(port_id).find("muscle_") != 0u) {
            ports.emplace(port_id, Port(
                    port_id, oper, is_vector, is_connected, index_.size(),
                    port_peer_dims));
        }
    }
    return ports;
}

Port Communicator::settings_in_port_(std::vector<Conduit> const & conduits) const {
    for (auto const & conduit : conduits) {
        if (conduit.receiving_component() == kernel_) {
            Identifier port_id = conduit.receiving_port();
            if (port_id == "muscle_settings_in")
                return Port(port_id, Operator::F_INIT, false,
                        peer_manager_->is_connected(port_id), index_.size(),
                        peer_manager_->get_peer_dims(conduit.sending_component()));
        }
    }
    return Port("muscle_settings_in", Operator::F_INIT, false, false, index_.size(), {});
}

MPPClient & Communicator::get_client_(Reference const & instance) {
    if (clients_.count(instance) == 0) {
        auto const & locations = peer_manager_->get_peer_locations(instance);
        std::ostringstream oss;
        oss << "Connecting to peer " << instance << " at [";
        for (std::size_t i = 0u; i < locations.size(); ++i) {
            if (i != 0u)
                oss << ", ";
            oss << locations[i];
        }
        oss << "]";
        logger_.info(oss.str());
        clients_[instance] = std::make_unique<MPPClient>(locations);
    }
    return *clients_.at(instance);
}

Endpoint Communicator::get_endpoint_(
        std::string const & port_name, std::vector<int> const & slot) const {
    try {
        Identifier port(port_name);
        return Endpoint(kernel_, index_, port, slot);
    }
    catch (std::invalid_argument const & e) {
        std::ostringstream oss;
        oss << "'" << port_name << "' is not a valid port name: " << e.what();
        throw std::invalid_argument(oss.str());
    }
}

std::tuple<std::string, bool> Communicator::split_port_desc_(
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

std::tuple<DataConstRef, mcp::ProfileData> Communicator::try_receive_(
        MPPClient & client, Reference const & receiver, Reference const & peer) {
    try {
        return client.receive(receiver);
    } catch(std::runtime_error const & err) {
        throw std::runtime_error(
            "Error while receiving a message: connection with peer '" +
            static_cast<std::string>(peer) +
            "' was lost. Did the peer crash?\n\tOriginal error: " + err.what());
    }
}

} }

