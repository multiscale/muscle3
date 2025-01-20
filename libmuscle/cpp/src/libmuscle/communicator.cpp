#include <libmuscle/communicator.hpp>

#include <libmuscle/close_port.hpp>
#include <libmuscle/data.hpp>
#include <libmuscle/mcp/ext_types.hpp>
#include <libmuscle/mpp_message.hpp>
#include <libmuscle/mcp/tcp_transport_server.hpp>
#include <libmuscle/mpp_client.hpp>
#include <libmuscle/profiling.hpp>

#include <ymmsl/ymmsl.hpp>

#include <limits>
#include <sstream>


using libmuscle::_MUSCLE_IMPL_NS::ClosePort;
using libmuscle::_MUSCLE_IMPL_NS::Data;
using libmuscle::_MUSCLE_IMPL_NS::mcp::ExtTypeId;
using libmuscle::_MUSCLE_IMPL_NS::MPPClient;
using libmuscle::_MUSCLE_IMPL_NS::mcp::TcpTransportServer;

using ymmsl::allows_receiving;
using ymmsl::Conduit;
using ymmsl::Identifier;
using ymmsl::Operator;
using ymmsl::Reference;
using ymmsl::Settings;


namespace libmuscle { namespace _MUSCLE_IMPL_NS {

Communicator::Communicator(
        ymmsl::Reference const & kernel,
        std::vector<int> const & index,
        PortManager & port_manager,
        Logger & logger, Profiler & profiler,
        MMPClient & manager)
    : kernel_(kernel)
    , index_(index)
    , port_manager_(port_manager)
    , logger_(logger)
    , profiler_(profiler)
    , manager_(manager)
    , server_()
    , clients_()
    , receive_timeout_(10.0)  // Notify manager, by default, after 10 seconds waiting in receive_message()
{}

std::vector<std::string> Communicator::get_locations() const {
    return server_.get_locations();
}

void Communicator::set_peer_info(PeerInfo const & peer_info) {
    peer_info_ = peer_info;
}

void Communicator::send_message(
        std::string const & port_name,
        Message const & message,
        Optional<int> slot,
        double checkpoints_considered_until)
{
    std::vector<int> slot_list;
    if (slot.is_set()) {
        logger_.debug("Sending message on ", port_name, "[", slot.get(), "]");
        slot_list.push_back(slot.get());
    }
    else
        logger_.debug("Sending message on ", port_name);

    Endpoint snd_endpoint = get_endpoint_(port_name, slot_list);
    if (!port_manager_.get_port(snd_endpoint.port).is_connected())
        // log sending on disconnected port
        return;

    Port & port = port_manager_.get_port(port_name);

    ProfileEvent profile_event(
            ProfileEventType::send, ProfileTimestamp(), {}, port, {}, slot,
            port.get_num_messages(), {}, message.timestamp());

    auto recv_endpoints = peer_info_.get().get_peer_endpoints(
            snd_endpoint.port, slot_list);

    Data settings_overlay(message.settings());

    Optional<int> port_length;
    if (port.is_resizable())
        port_length = port.get_length();

    for (auto recv_endpoint : recv_endpoints) {
        MPPMessage mpp_message(
                snd_endpoint.ref(), recv_endpoint.ref(),
                port_length, message.timestamp(), Optional<double>(),
                settings_overlay, port.get_num_messages(slot),
                checkpoints_considered_until,
                message.data());

        if (message.has_next_timestamp())
            mpp_message.next_timestamp = message.next_timestamp();

        auto message_bytes = mpp_message.encoded();
        profile_event.message_size = message_bytes.size();
        server_.deposit(recv_endpoint.ref(), std::move(message_bytes));
    }

    port.increment_num_messages(slot);

    profile_event.stop();
    if (port.is_vector())
        profile_event.port_length = port.get_length();
    if (!is_close_port(message.data()))
        profiler_.record_event(std::move(profile_event));
}

std::tuple<Message, double> Communicator::receive_message(
        std::string const & port_name,
        Optional<int> slot,
        Optional<Message> const & default_msg)
{
    Port & port = (port_name == "muscle_settings_in") ?
        port_manager_.muscle_settings_in() : port_manager_.get_port(port_name);

    std::string port_and_slot = port_name;
    if (slot.is_set())
        port_and_slot = port_name + "[" + std::to_string(slot.get()) + "]";
    logger_.debug("Waiting for message on ", port_and_slot);
    std::vector<int> slot_list;
    if (slot.is_set())
        slot_list.emplace_back(slot.get());

    Endpoint recv_endpoint(get_endpoint_(port_name, slot_list));

    ProfileEvent receive_event(
            ProfileEventType::receive, ProfileTimestamp(), {}, port, {}, slot,
            port.get_num_messages());

    // peer_info already checks that there is at most one snd_endpoint
    // connected to the port we receive on
    Endpoint snd_endpoint = peer_info_.get().get_peer_endpoints(
            recv_endpoint.port, slot_list).at(0);
    MPPClient & client = get_client_(snd_endpoint.instance());
    ReceiveTimeoutHandler handler(
            manager_, snd_endpoint.instance(), port_name, slot, receive_timeout_);
    ReceiveTimeoutHandler *timeout_handler = receive_timeout_ < 0 ? nullptr : &handler;
    auto msg_and_profile = try_receive_(
            client, recv_endpoint.ref(), snd_endpoint.kernel, port_and_slot, timeout_handler);
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

    if (is_close_port(mpp_message.data)) {
        if (slot.is_set())
            port.set_closed(slot.get());
        else
            port.set_closed();
    }

    Message message(
            mpp_message.timestamp, mpp_message.data, overlay_settings);

    if (mpp_message.next_timestamp.is_set())
        message.set_next_timestamp(mpp_message.next_timestamp.get());

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
            logger_.debug("Discarding received message on ", port_and_slot,
                          ": resuming from weakly consistent snapshot");
            port.set_resumed(slot);
            return receive_message(port_name, slot, default_msg);
        }
        std::ostringstream oss;
        oss << "Received message on " << port_and_slot;
        oss << " with unexpected message number " << mpp_message.message_number;
        oss << ". Was expecting " << expected_message_number;
        oss << ". Are you resuming from an inconsistent snapshot?";
        throw std::runtime_error(oss.str());
    }
    port.increment_num_messages(slot);

    logger_.debug("Received message on ", port_and_slot);

    if (is_close_port(message.data())) {
        logger_.debug("Port ", port_and_slot, " is now closed");
    }
    return std::make_tuple(message, mpp_message.saved_until);
}

void Communicator::shutdown() {
    close_ports_();

    for (auto & client : clients_)
        client.second->close();

    ProfileEvent wait_event(ProfileEventType::disconnect_wait, ProfileTimestamp());
    server_.wait_for_receivers();
    profiler_.record_event(std::move(wait_event));

    ProfileEvent shutdown_event(ProfileEventType::shutdown, ProfileTimestamp());
    server_.shutdown();
    profiler_.record_event(std::move(shutdown_event));
}


Reference Communicator::instance_id_() const {
    return kernel_ + index_;
}

MPPClient & Communicator::get_client_(Reference const & instance) {
    if (clients_.count(instance) == 0) {
        auto const & locations = peer_info_.get().get_peer_locations(instance);
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

std::tuple<std::vector<char>, mcp::ProfileData> Communicator::try_receive_(
        MPPClient & client, Reference const & receiver, Reference const & peer,
        std::string const & port_and_slot, ReceiveTimeoutHandler *timeout_handler) {
    try {
        return client.receive(receiver, timeout_handler);
    } catch(Deadlock const & err) {
        throw std::runtime_error(
            "Deadlock detected when receiving a message on '" +
            port_and_slot +
            "'. See manager logs for more detail.");
    } catch(std::runtime_error const & err) {
        throw std::runtime_error(
            "Error while receiving a message: connection with peer '" +
            static_cast<std::string>(peer) +
            "' was lost. Did the peer crash?\n\tOriginal error: " + err.what());
    }
}

void Communicator::close_port_(
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

void Communicator::close_outgoing_ports_() {
    for (auto const & oper_ports : port_manager_.list_ports()) {
        if (allows_sending(oper_ports.first)) {
            for (auto const & port_name : oper_ports.second) {
                auto const & port = port_manager_.get_port(port_name);
                if (port.is_vector()) {
                    for (int slot = 0; slot < port.get_length(); ++slot)
                        close_port_(port_name, slot);
                }
                else
                    close_port_(port_name);
            }
        }
    }
}

void Communicator::drain_incoming_port_(std::string const & port_name) {
    auto const & port = port_manager_.get_port(port_name);
    while (port.is_open())
        receive_message(port_name);
}

void Communicator::drain_incoming_vector_port_(std::string const & port_name) {
    auto const & port = port_manager_.get_port(port_name);

    bool all_closed = true;
    for (int slot = 0; slot < port.get_length(); ++slot)
        if (port.is_open(slot))
            all_closed = false;

    while (!all_closed) {
        all_closed = true;
        for (int slot = 0; slot < port.get_length(); ++slot) {
            if (port.is_open(slot))
                receive_message(port_name, slot);
            if (port.is_open(slot))
                all_closed = false;
        }
    }
}

void Communicator::close_incoming_ports_() {
    for (auto const & oper_ports : port_manager_.list_ports()) {
        if (allows_receiving(oper_ports.first)) {
            for (auto const & port_name : oper_ports.second) {
                auto const & port = port_manager_.get_port(port_name);
                if (!port.is_connected())
                    continue;
                if (port.is_vector())
                    drain_incoming_vector_port_(port_name);
                else
                    drain_incoming_port_(port_name);
            }
        }
    }
}

void Communicator::close_ports_() {
    close_outgoing_ports_();
    close_incoming_ports_();
}

} }

