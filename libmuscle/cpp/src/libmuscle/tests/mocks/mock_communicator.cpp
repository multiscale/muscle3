#include <mocks/mock_communicator.hpp>

#include <libmuscle/data.hpp>
#include <ymmsl/ymmsl.hpp>

#include <cassert>

using libmuscle::impl::Data;
using libmuscle::impl::DataConstRef;
using libmuscle::impl::Port;

using ymmsl::Conduit;
using ymmsl::Identifier;
using ymmsl::Operator;
using ymmsl::Reference;
using ymmsl::Settings;


namespace libmuscle { namespace impl {

MockCommunicator::MockCommunicator(
        ymmsl::Reference const & kernel,
        std::vector<int> const & index,
        Optional<PortsDescription> const & declared_ports,
        Logger & logger, Profiler & profiler)
{
    ++num_constructed;
}

std::vector<std::string> MockCommunicator::get_locations() const {
    return std::vector<std::string>({"tcp:test1,test2", "tcp:test3"});
}

void MockCommunicator::connect(
        std::vector<Conduit> const & conduits,
        PeerDims const & peer_dims,
        PeerLocations const & peer_locations)
{
}

bool MockCommunicator::settings_in_connected() const {
    return settings_in_connected_return_value;
}

PortsDescription MockCommunicator::list_ports() const {
    return list_ports_return_value;
}

bool MockCommunicator::port_exists(std::string const & port_name) const {
    return port_exists_return_value;
}

Port const & MockCommunicator::get_port(std::string const & port_name) const {
    return get_port_return_value.at(port_name);
}

Port & MockCommunicator::get_port(std::string const & port_name) {
    return get_port_return_value.at(port_name);
}

void MockCommunicator::send_message(
        std::string const & port_name,
        Message const & message,
        Optional<int> slot)
{
    last_sent_port = port_name;
    last_sent_message = message;
    last_sent_slot = slot;
}

Message MockCommunicator::receive_message(
        std::string const & port_name,
        Optional<int> slot,
        Optional<Message> const & default_msg)
{
    Reference key(port_name);
    if (slot.is_set())
        key += slot.get();
    if (next_received_message.count(key) == 0) {
        assert(default_msg.is_set());
        return default_msg.get();
    }
    if (is_close_port(next_received_message.at(key)->data())) {
        if (slot.is_set())
            get_port_return_value.at(port_name).set_closed(slot.get());
        else
            get_port_return_value.at(port_name).set_closed();
    }

    return *next_received_message.at(key);
}

void MockCommunicator::close_port(
        std::string const & port_name, Optional<int> slot)
{
}

void MockCommunicator::shutdown() {
}


MockCommunicator::PortMessageCounts MockCommunicator::get_message_counts() {
    return get_message_counts_return_value;
}

void MockCommunicator::restore_message_counts(
        PortMessageCounts const & port_message_counts){
    last_restored_message_counts = port_message_counts;
}


void MockCommunicator::reset() {
    num_constructed = 0;
    settings_in_connected_return_value = false;
    port_exists_return_value = true;
    get_port_return_value.clear();
    next_received_message.clear();
    list_ports_return_value.clear();
    last_sent_port = "";
    last_sent_message = Message(0.0);
    last_sent_slot = {};
    get_message_counts_return_value.clear();
    last_restored_message_counts = {};
}

int MockCommunicator::num_constructed = 0;

bool MockCommunicator::settings_in_connected_return_value = false;

bool MockCommunicator::port_exists_return_value = true;

std::unordered_map<std::string, Port> MockCommunicator::get_port_return_value;

std::unordered_map<Reference, std::unique_ptr<Message>>
    MockCommunicator::next_received_message;

PortsDescription MockCommunicator::list_ports_return_value;

std::string MockCommunicator::last_sent_port;

Message MockCommunicator::last_sent_message(0.0);

Optional<int> MockCommunicator::last_sent_slot;

MockCommunicator::PortMessageCounts MockCommunicator::get_message_counts_return_value;

MockCommunicator::PortMessageCounts MockCommunicator::last_restored_message_counts;

} }

