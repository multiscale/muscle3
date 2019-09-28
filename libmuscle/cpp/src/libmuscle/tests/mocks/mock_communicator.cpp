#include <mocks/mock_communicator.hpp>

#include <libmuscle/data.hpp>
#include <ymmsl/model.hpp>


using libmuscle::Data;
using libmuscle::DataConstRef;
using libmuscle::Port;

using ymmsl::Conduit;
using ymmsl::Identifier;
using ymmsl::Operator;
using ymmsl::Reference;
using ymmsl::Settings;


namespace libmuscle {

bool is_close_port(DataConstRef const & data) {
    return true;
}


MockCommunicator::MockCommunicator(
        ymmsl::Reference const & kernel,
        std::vector<int> const & index,
        Optional<PortsDescription> const & declared_ports,
        int profiler)
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

bool MockCommunicator::parameters_in_connected() const {
    return true;
}

PortsDescription MockCommunicator::list_ports() const {
    PortsDescription result;
    return result;
}

bool MockCommunicator::port_exists(std::string const & port_name) const {
    return true;
}

Port const & MockCommunicator::get_port(std::string const & port_name) const {
    return get_port_return_value;
}

Port & MockCommunicator::get_port(std::string const & port_name) {
    return get_port_return_value;
}

void MockCommunicator::send_message(
        std::string const & port_name,
        Message const & message,
        Optional<int> slot)
{
}

Message MockCommunicator::receive_message(
        std::string const & port_name,
        Optional<int> slot,
        Optional<Message> const & default_msg)
{
    Message message(0.0, 1.0, Data());
    return message;
}

void MockCommunicator::close_port(
        std::string const & port_name, Optional<int> slot)
{
}

void MockCommunicator::shutdown() {
}


void MockCommunicator::reset() {
    num_constructed = 0;
    get_port_return_value.set_length(10);
}

int MockCommunicator::num_constructed = 0;

Port MockCommunicator::get_port_return_value(
        "out", Operator::O_F, true, true, 0, {});

}

