#include <libmuscle/communicator.hpp>

#include <libmuscle/data.hpp>
#include <libmuscle/mcp/ext_types.hpp>
#include <libmuscle/mcp/tcp_client.hpp>
#include <libmuscle/mcp/tcp_server.hpp>

#include <limits>


using libmuscle::Data;
using libmuscle::DataConstRef;
using libmuscle::mcp::ExtTypeId;
using libmuscle::mcp::TcpClient;
using libmuscle::mcp::TcpServer;

using ymmsl::Conduit;
using ymmsl::Identifier;
using ymmsl::Operator;
using ymmsl::Reference;
using ymmsl::Settings;


namespace libmuscle {

/* Represents a ClosePort_ message.
 *
 * We need to be able to send a ClosePort_ message just like we send user data
 * and settings. Adding support for it to the Data class would expose it to
 * the user, while it's an internal sentinel object. We could also go full-OO
 * and create interfaces for external, internal and read-only use of the Data
 * class, add some factories, teach users about shared pointers, and so on,
 * but I'm not sure it would make anyone's life easier either. So we'll go with
 * this, it's a bit ugly, but it works.
 */
class ClosePort_ : public Data {
    public:
        /* Create a ClosePort_ object.
         *
         * The ClosePort_ object itself is the message, so it has no attributes
         * and doesn't contain any information other than its MessagePack
         * extension type id.
         */
        ClosePort_()
            :  Data()
        {
            char * zoned_mem = zone_alloc_<char>(1);
            zoned_mem[0] = static_cast<char>(ExtTypeId::close_port);
            *mp_obj_ << msgpack::type::ext_ref(zoned_mem, 1);
        }
};


bool is_close_port(DataConstRef const & data) {
    return (data.mp_obj_->type == msgpack::type::EXT &&
            data.mp_obj_->via.ext.type() ==
                static_cast<int8_t>(ExtTypeId::close_port));
}


Message::Message(
        double timestamp,
        DataConstRef const & data)
    : timestamp_(timestamp)
    , next_timestamp_()
    , data_(data)
    , settings_()
{}

Message::Message(
        double timestamp,
        double next_timestamp,
        DataConstRef const & data)
    : timestamp_(timestamp)
    , next_timestamp_(next_timestamp)
    , data_(data)
    , settings_()
{}

Message::Message(
        double timestamp,
        DataConstRef const & data,
        Settings const & settings)
    : timestamp_(timestamp)
    , next_timestamp_()
    , data_(data)
    , settings_(settings)
{}

Message::Message(
        double timestamp,
        double next_timestamp,
        DataConstRef const & data,
        Settings const & settings)
    : timestamp_(timestamp)
    , next_timestamp_(next_timestamp)
    , data_(data)
    , settings_(settings)
{}

double Message::timestamp() const {
    return timestamp_;
}

void Message::set_timestamp(double timestamp) {
    timestamp_ = timestamp;
}

bool Message::has_next_timestamp() const {
    return next_timestamp_.is_set();
}

double Message::next_timestamp() const {
    return next_timestamp_.get();
}

void Message::set_next_timestamp(double next_timestamp) {
    next_timestamp_ = next_timestamp;
}

void Message::unset_next_timestamp() {
    next_timestamp_ = {};
}

DataConstRef const & Message::data() const {
    return data_;
}

bool Message::has_settings() const {
    return settings_.is_set();
}

Settings const & Message::settings() const {
    return settings_.get();
}


Communicator::Communicator(
        ymmsl::Reference const & kernel,
        std::vector<int> const & index,
        Optional<PortsDescription> const & declared_ports,
        int profiler)
    : kernel_(kernel)
    , index_(index)
    , declared_ports_(declared_ports)
    , profiler_(profiler)
    , servers_()
    , clients_()
    , ports_()
{
    servers_.emplace_back(new TcpServer(instance_id_(), post_office_));
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

    muscle_settings_in_ = parameters_in_port_(conduits);
}

bool Communicator::parameters_in_connected() const {
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

    // Port const & port = ports_.at(port_name);

    // TODO start profile event

    Endpoint recv_endpoint = peer_manager_->get_peer_endpoint(
            snd_endpoint.port, slot_list);

    Data settings_overlay(message.settings());

    Optional<int> port_length;
    if (ports_.at(port_name).is_resizable())
        port_length = ports_.at(port_name).get_length();

    auto mcp_message = std::make_unique<mcp::Message>(
            snd_endpoint.ref(), recv_endpoint.ref(),
            port_length, message.timestamp(), Optional<double>(),
            settings_overlay, message.data());

    if (message.has_next_timestamp())
        mcp_message->next_timestamp = message.next_timestamp();

    post_office_.deposit(recv_endpoint.ref(), std::move(mcp_message));

    // TODO: stop and complete profile event
}

Message Communicator::receive_message(
        std::string const & port_name,
        Optional<int> slot,
        Optional<Message> const & default_msg)
{
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
        else
            return default_msg.get();
    }

    Port & port = (ports_.count(port_name)) ? (ports_.at(port_name)) : muscle_settings_in_.get();

    // TODO start profile event

    Endpoint snd_endpoint = peer_manager_->get_peer_endpoint(
            recv_endpoint.port, slot_list);
    mcp::Client & client = get_client_(snd_endpoint.instance());
    mcp::Message mcp_message = client.receive(recv_endpoint.ref());

    Settings overlay_settings(mcp_message.parameter_overlay.as<Settings>());

    if (mcp_message.port_length.is_set())
        if (port.is_resizable())
            port.set_length(mcp_message.port_length.get());

    Message message(
            mcp_message.timestamp, mcp_message.data, overlay_settings);

    if (mcp_message.next_timestamp.is_set())
        message.set_next_timestamp(mcp_message.next_timestamp.get());

    if (is_close_port(message.data())) {
        if (slot.is_set())
            port.set_closed(slot.get());
        else
            port.set_closed();
    }

    // TODO stop and finalise profile event

    return message;
}

void Communicator::close_port(
        std::string const & port_name, Optional<int> slot) {
    Message message(
            std::numeric_limits<double>::infinity(),
            ClosePort_(), Settings());
    send_message(port_name, message, slot);
}

void Communicator::shutdown() {
    for (auto & client : clients_)
        client.second->close();

    TcpClient::shutdown(instance_id_());

    post_office_.wait_for_receivers();

    for (auto & server : servers_)
        server->close();
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
                Reference peer_port = peer_manager_->get_peer_port(port_name);
                Reference peer_ce(peer_port.cbegin(), std::prev(peer_port.cend()));
                port_peer_dims = peer_manager_->get_peer_dims(peer_ce);
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

        if (conduit.sending_compute_element() == kernel_) {
            port_id = conduit.sending_port();
            oper = Operator::O_F;
            port_peer_dims = peer_manager_->get_peer_dims(
                    conduit.receiving_compute_element());
        }
        else if (conduit.receiving_compute_element() == kernel_) {
            port_id = conduit.receiving_port();
            oper = Operator::F_INIT;
            port_peer_dims = peer_manager_->get_peer_dims(
                    conduit.sending_compute_element());
        }
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

Port Communicator::parameters_in_port_(std::vector<Conduit> const & conduits) const {
    for (auto const & conduit : conduits) {
        if (conduit.receiving_compute_element() == kernel_) {
            Identifier port_id = conduit.receiving_port();
            if (port_id == "muscle_settings_in")
                return Port(port_id, Operator::F_INIT, false,
                        peer_manager_->is_connected(port_id), index_.size(),
                        peer_manager_->get_peer_dims(conduit.sending_compute_element()));
        }
    }
    return Port("muscle_settings_in", Operator::F_INIT, false, false, index_.size(), {});
}

mcp::Client & Communicator::get_client_(Reference const & instance) {
    if (clients_.count(instance) != 0)
        return *clients_.at(instance);

    for (auto const & location : peer_manager_->get_peer_locations(instance)) {
        if (TcpClient::can_connect_to(location)) {
            auto client = std::make_unique<TcpClient>(instance_id_(), location);
            clients_[instance] = std::move(client);
            return *clients_.at(instance);
        }
    }
    std::ostringstream oss;
    oss << "Could not find a matching protocol for " << instance;
    throw std::runtime_error(oss.str());
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

    if (port_desc.rfind("[]") == (port_desc.size() - 2)) {
        is_vector = true;
        port_name = port_desc.substr(0, port_desc.size() - 2);
    }

    if (port_name.rfind("[]") == (port_name.size() - 2)) {
        std::ostringstream oss;
        oss << "Port description '" << port_desc << "' is invalid: ports can";
        oss << " have at most one dimension.";
        throw std::invalid_argument(oss.str());
    }

    return std::make_tuple(port_name, is_vector);
}

}

