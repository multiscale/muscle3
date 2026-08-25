#include <libmuscle/communicator.hpp>

#include <libmuscle/data.hpp>
#include <libmuscle/logger.hpp>
#include <libmuscle/mcp/ext_types.hpp>
#include <libmuscle/mpp_message.hpp>
#include <libmuscle/mcp/tcp_transport_server.hpp>
#include <libmuscle/mpp_client.hpp>
#include <libmuscle/profiling.hpp>

#include <ymmsl/ymmsl.hpp>

#include <algorithm>
#include <cassert>
#include <limits>
#include <memory>
#include <sstream>


using libmuscle::_MUSCLE_IMPL_NS::Milestone;
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

namespace {

/** Helper method to construct a Message from an MPPMessage.
 * 
 * N.B. since C++ enforces only const access to .settings and .data, we don't need to
 * make a copy (unlike the Python equivalent).
 */
Message make_message(MPPMessage const & mpp_msg) {
    Message message(
        mpp_msg.timestamp,
        mpp_msg.data,
        mpp_msg.settings_overlay.as<Settings>()
    );
    if (mpp_msg.next_timestamp.is_set())
        message.set_next_timestamp(mpp_msg.next_timestamp.get());
    return message;
}


/** Helper template method to execute code for each slot of the given port.
 * 
 * Expects a function with arguments (Optional<int> slot, Reference port_ref)
 */
template<typename F>
void for_each_slot(Port const & port, F&& f) {
    Reference port_name(port.name);
    if (!port.is_vector()) {
        f({}, port_name);
    } else {
        int slot = 0; // Allow pre-receive to receive 1 message that updates port._length
        do {
            f(slot, port_name + slot);  
        } while (++slot < port.get_length());
    }
}

}

Communicator::Communicator(
        ymmsl::Reference const & kernel,
        std::vector<int> const & index,
        PortManager & port_manager,
        Profiler & profiler,
        MMPClient & manager)
    : kernel_(kernel)
    , index_(index)
    , port_manager_(port_manager)
    , profiler_(profiler)
    , manager_(manager)
    , server_()
    , clients_()
    , receive_timeout_(10.0)  // Notify manager, by default, after 10 seconds waiting in receive_message()
    , f_init_repeaters_()
    , f_init_repeat_cache_()
{}

std::vector<std::string> Communicator::get_locations() const {
    return server_.get_locations();
}

void Communicator::set_peer_info(PeerInfo const & peer_info) {
    peer_info_ = peer_info;
    timeline_manager_ = std::make_unique<TimelineManager>(port_manager_);
    prepare_conduit_filters_();
}

void Communicator::finish_reuse_iteration() {
    assert(timeline_manager_);
    IterationCount finished_iteration = timeline_manager_->finish_reuse_iteration();
    broadcast_milestone_(Milestone(finished_iteration), true);
}

TimelineState Communicator::get_state() const {
    assert(timeline_manager_);
    return timeline_manager_->get_state();
}

void Communicator::restore_state(TimelineState const & state) {
    assert(timeline_manager_);
    timeline_manager_->restore_state(state);
}

void Communicator::send_message(
        std::string const & port_name,
        Message const & message,
        Optional<int> slot)
{
    Port & port = port_manager_.get_port(port_name);
    if (!port.is_connected()) {
        log_debug("Sending message on unconnected port ", port_desc(port_name, slot));
        return;
    }
    if (!port.is_open(slot)) {
        if (is_milestone(message.data()) && Milestone(message.data()).is_final_milestone())
            return;  // Ignore closing an already closed port 
        throw std::runtime_error(
                "Port " + port_desc(port_name, slot) + " is already closed.");
    }
    log_debug("Sending message on ", port_desc(port_name, slot));

    IterationCount iteration;
    if (is_milestone(message.data()))
        iteration = Milestone(message.data()).iteration();
    else
        iteration = timeline_manager_->check_send_message(port_name, slot);

    ProfileEvent profile_event(
            ProfileEventType::send, ProfileTimestamp(), {}, port, {}, slot,
            port.get_num_messages(), {}, message.timestamp());

    Optional<int> port_length;
    if (port.is_resizable())
        port_length = port.get_length();

    auto endpoints = get_endpoints_(port, slot);
    auto& snd_endpoint = std::get<0>(endpoints);
    auto& recv_endpoints = std::get<1>(endpoints);
    for (auto recv_endpoint : recv_endpoints) {
        MPPMessage mpp_message(
                snd_endpoint.ref(), recv_endpoint.ref(),
                port_length, message.timestamp(), Optional<double>(),
                Data(message.settings()), port.get_num_messages(slot),
                message.data(), iteration);

        if (message.has_next_timestamp())
            mpp_message.next_timestamp = message.next_timestamp();

        auto message_bytes = mpp_message.encoded();
        profile_event.message_size = message_bytes.size();
        server_.deposit(recv_endpoint.ref(), std::move(message_bytes));
    }

    profile_event.stop();
    if (port.is_vector())
        profile_event.port_length = port.get_length();
    if (!is_milestone(message.data())) {
        profiler_.record_event(std::move(profile_event));
        port.increment_num_messages(slot);
    } else if (Milestone(message.data()).is_final_milestone())
        port.set_closed(slot);
}

Communicator::FInitCacheType Communicator::pre_receive_f_init() {
    FInitCacheType cache;
    std::unordered_map<::ymmsl::Reference, IterationCount> iterations;

    // Pre-receive on ports without repeater filters:
    for (Port const & port : port_manager_.get_connected_ports(Operator::F_INIT, {})) {
        std::string port_name(port.name);
        if (f_init_repeaters_.count(port.name) == 0) {
            log_debug("Pre-receiving on port ", port_name);
            for_each_slot(port, [&](Optional<int> slot, Reference port_ref){
                auto mpp_message = receive_message_(port_name, slot);
                cache.emplace(port_ref, make_message(mpp_message));
                iterations.emplace(port_ref, mpp_message.iteration);
            });
        }
    }

    // Check if we have received milestones
    auto milestone = verify_received_milestones_(cache);
    if (milestone.is_set()) {
        // Propagate milestone
        broadcast_milestone_(milestone.get(), false);
        if (milestone.get().is_final_milestone())  // Final milestone received
            throw PortClosed();
        // Clean up stale messages from the cache
        IterationCount const milestone_iteration = milestone.get().iteration();
        for (auto it = f_init_repeat_cache_.begin(); it != f_init_repeat_cache_.end(); ) {
            if (it->second.iteration.size() >= milestone_iteration.size())
                it = f_init_repeat_cache_.erase(it);
            else
                ++it;
        }
        // Pre-receive again to receive the actual messages
        return pre_receive_f_init();
    }

    // Verify that all F_INIT messages agree on the iteration count
    auto & cur_iteration = timeline_manager_->check_f_init_iterations(iterations);
    // Put messages from repeater ports in the cache:
    pre_receive_f_init_with_repeaters_(cur_iteration, cache);
    return cache;
}

Optional<Milestone> Communicator::verify_received_milestones_(FInitCacheType const & cache) {
    std::vector<Optional<IterationCount>> milestone_iterations;
    std::vector<std::string> closed_ports;
    for (auto & item : cache) {
        Optional<IterationCount> it;
        if (is_milestone(item.second.data())) {
            Milestone milestone(item.second.data());
            it = milestone.iteration();
            if (milestone.is_final_milestone()) {
                closed_ports.emplace_back(item.first);
            }
        }
        auto found = std::find(milestone_iterations.begin(), milestone_iterations.end(), it);
        if (found == milestone_iterations.end())  // Not found
            milestone_iterations.push_back(it);
    }
    // Milestones should be consistent, or something went wrong
    if (milestone_iterations.size() > 1) {
        if (closed_ports.size() > 0) {
            std::ostringstream oss;
            oss << "Some ports were unexpectedly closed while trying to receive, did ";
            oss << "the peers crash? Closed ports: ";
            bool first = true;
            for (auto & port : closed_ports) {
                if (!first) oss << ", ";
                first = false;
                oss << port;
            }
            throw std::runtime_error(oss.str());
        }
        throw std::runtime_error(
            "Internal error: received milestones for different iterations in F_INIT. "
            "This is not supposed to happen and may be a bug in libmuscle. Please "
            "report an issue."
        );
    }
    if (milestone_iterations[0].is_set())
        return Milestone(milestone_iterations[0].get());
    return {};
}

void Communicator::pre_receive_f_init_with_repeaters_(
        IterationCount const & cur_iteration, FInitCacheType & cache)
{
    for (auto & item : f_init_repeaters_) {
        auto & port_name = item.first;
        auto & filters = item.second;
        auto & port = port_manager_.get_port(port_name);

        // If the message is not in the cache we need to receive again. We may need
        // to receive and discard multiple messages here, see the tests
        // (test_repeater_filters_discard_messages) for a scenario.
        Reference port_ref(port_name);
        if (port.is_vector())
            port_ref += 0;
        while (f_init_repeat_cache_.count(port_ref) == 0) {
            log_debug("Pre-receiving on port ", port_name);
            for_each_slot(port, [&](Optional<int> recv_slot, Reference recv_port_ref) {
                auto mpp_msg = receive_message_(port_name, recv_slot);
                if (is_subiteration(cur_iteration, mpp_msg.iteration)) {
                    f_init_repeat_cache_.emplace(recv_port_ref, mpp_msg);
                } else if(mpp_msg.iteration > cur_iteration) {
                    throw std::runtime_error(
                        "Internal error: Received a message from the future on "
                        + port_desc(port_name, recv_slot) + ". Message iteration is "
                        + to_string(mpp_msg.iteration) + ", while ours is " + to_string(cur_iteration) + "."
                    );
                }
            });
        }

        // Repeat or pad the cached messages
        bool pad_message = false;
        std::size_t offset = cur_iteration.size() - filters.size();
        for (std::size_t i = 0; i < filters.size(); ++i) {
            if (filters[i] == ::ymmsl::ConduitFilter::PAD && cur_iteration[offset + i] > 0)
                pad_message = true;
        }
        for_each_slot(port, [&](Optional<int> slot, Reference port_ref) {
            auto & mpp_msg = f_init_repeat_cache_.at(port_ref);
            if (!is_subiteration(cur_iteration, mpp_msg.iteration))
                throw std::runtime_error(
                    "Internal error: Invalid cached message for "
                    + port_desc(port_name, slot) + ". Cached message iteration is "
                    + to_string(mpp_msg.iteration) + ", while ours is " + to_string(cur_iteration) + "."
                );
            auto message = make_message(mpp_msg);
            if (pad_message)
                message.set_data(Data());
            cache.emplace(port_ref, message);
        });
    }
}

Message Communicator::receive_s_message(
        std::string const & port_name,
        Optional<int> slot)
{
    timeline_manager_->check_receive_s(port_name, slot);
    // Instance should not need to bother about milestones, so we keep receiving
    // messages until we have actual data.
    while (true) {
        auto message = receive_message_(port_name, slot);
        if (is_milestone(message.data)) {
            if (Milestone(message.data).is_final_milestone())
                throw PortClosed();
            // TODO: handle milestone, if needed
        } else {
            timeline_manager_->record_received_s_message(
                    port_name, slot, message.iteration);
            return make_message(message);
        }
    }
}


MPPMessage Communicator::receive_message_(
        std::string const & port_name,
        Optional<int> slot)
{
    Port & port = port_manager_.get_port(port_name);
    std::string port_and_slot = port_desc(port_name, slot);
    log_debug("Waiting for message on ", port_and_slot);

    ProfileEvent receive_event(
            ProfileEventType::receive, ProfileTimestamp(), {}, port, {}, slot,
            port.get_num_messages());

    auto endpoints = get_endpoints_(port, slot);
    auto& recv_endpoint = std::get<0>(endpoints);
    // peer_info already checks that there is at most one snd_endpoint
    // connected to the port we receive on
    auto& snd_endpoint = std::get<1>(endpoints)[0];
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

    recv_decode_event.stop();

    if (mpp_message.port_length.is_set())
        if (port.is_resizable())
            port.set_length(mpp_message.port_length.get());

    if (is_milestone(mpp_message.data)) {
        if (Milestone(mpp_message.data).is_final_milestone())
            port.set_closed(slot);
    }

    ProfileTimestamp start_recv, end_wait, end_transfer;
    std::tie(start_recv, end_wait, end_transfer) = std::get<1>(msg_and_profile);
    ProfileEvent recv_wait_event(
            ProfileEventType::receive_wait, start_recv,
            end_wait, port, mpp_message.port_length, slot,
            port.get_num_messages(), msg.size(), mpp_message.timestamp);

    ProfileEvent recv_xfer_event(
            ProfileEventType::receive_transfer, end_wait,
            end_transfer, port, mpp_message.port_length, slot,
            port.get_num_messages(), msg.size(), mpp_message.timestamp);

    recv_decode_event.message_timestamp = mpp_message.timestamp;
    receive_event.message_timestamp = mpp_message.timestamp;

    if (port.is_vector()) {
        receive_event.port_length = port.get_length();
        recv_wait_event.port_length = port.get_length();
        recv_xfer_event.port_length = port.get_length();
        recv_decode_event.port_length = port.get_length();
    }

    receive_event.message_size = std::get<0>(msg_and_profile).size();

    if (!is_milestone(mpp_message.data) || !Milestone(mpp_message.data).is_final_milestone()) {
        // Don't log receives of final milestone: this is recorded as SHUTDOWN_WAIT
        profiler_.record_event(std::move(recv_wait_event));
        profiler_.record_event(std::move(recv_xfer_event));
        profiler_.record_event(std::move(recv_decode_event));
        profiler_.record_event(std::move(receive_event));
    }

    int expected_message_number = port.get_num_messages(slot);
    if (expected_message_number != mpp_message.message_number) {
        if (expected_message_number - 1 == mpp_message.message_number and
                port.is_resuming(slot)) {
            log_debug("Discarding received message on ", port_and_slot,
                          ": resuming from weakly consistent snapshot");
            if (!is_milestone(mpp_message.data))
                port.set_resumed(slot);
            return receive_message_(port_name, slot);
        }
        std::ostringstream oss;
        oss << "Received message on " << port_and_slot;
        oss << " with unexpected message number " << mpp_message.message_number;
        oss << ". Was expecting " << expected_message_number;
        oss << ". Are you resuming from an inconsistent snapshot?";
        throw std::runtime_error(oss.str());
    }

    if (!is_milestone(mpp_message.data)) {
        port.increment_num_messages(slot);
        log_debug("Received message on ", port_and_slot);
    } else {
        Milestone milestone(mpp_message.data);
        if (milestone.is_final_milestone())
            log_debug("Port ", port_and_slot, " is now closed");
        else
            log_debug("Received ", std::string(milestone), " on ", port_and_slot);
    }
    return mpp_message;
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
        log_info(oss.str());
        clients_[instance] = std::make_unique<MPPClient>(locations);
    }
    return *clients_.at(instance);
}

std::tuple<Endpoint, std::vector<Endpoint>> Communicator::get_endpoints_(
        Port const & port, Optional<int> const & slot) const {
    return {
        Endpoint(kernel_, index_, port.name, slot),
        peer_info_.get().get_peer_endpoints(port.name, slot)
    };
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

void Communicator::broadcast_milestone_(Milestone const & milestone, bool only_o_i) {
    log_debug("Sending ", std::string(milestone), " to all ", (only_o_i ? "O_I" : "outgoing"), " ports");
    Message message(-std::numeric_limits<double>::infinity(), milestone, Settings());

    auto do_broadcast = [&](Operator op) {
        for (Port const & port : port_manager_.get_connected_ports(op, {})) {
            if (port.is_vector()) {
                for (int slot = 0; slot < port.get_length(); ++slot)
                    send_message(port.name, message, slot);
            } else {
                send_message(port.name, message);
            }
        }
    };

    do_broadcast(Operator::O_I);
    if (!only_o_i)
        do_broadcast(Operator::O_F);
}

void Communicator::close_outgoing_ports_() {
    broadcast_milestone_(Milestone(IterationCount({})), false);
}

void Communicator::drain_incoming_port_(std::string const & port_name) {
    auto const & port = port_manager_.get_port(port_name);
    while (port.is_open())
        receive_message_(port_name);
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
                receive_message_(port_name, slot);
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

void Communicator::prepare_conduit_filters_() {
    // F_INIT repeat/pad filters
    for (Port const & port : port_manager_.get_connected_ports(Operator::F_INIT, {})) {
        std::vector<::ymmsl::ConduitFilter> filters = peer_info_.get().get_filters_for_receiver(kernel_ + port.name);
        // Only keep the repeater filters, the sending component handles reducers:
        filters.erase(
            std::remove_if(filters.begin(), filters.end(), ::ymmsl::is_reducer),
            filters.end());
        if (!filters.empty())
            f_init_repeaters_.emplace(port.name, filters);
    }
    // S repeat/pad filters are not implemented
    for (Port const & port : port_manager_.get_connected_ports(Operator::S, {})) {
        std::vector<::ymmsl::ConduitFilter> filters = peer_info_.get().get_filters_for_receiver(kernel_ + port.name);
        // Only keep the repeater filters, the sending component handles reducers:
        for (auto & filter: filters) {
            if (is_repeater(filter))
                throw std::runtime_error(
                    "Repeater filters are not implemented for S ports, you may connect "
                    "the conduit to an F_INIT port instead."
                );
        }
    }
    // TODO: reducer filters
}

} }

