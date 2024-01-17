#pragma once

#include <libmuscle/logger.hpp>
#include <libmuscle/message.hpp>
#include <libmuscle/namespace.hpp>
#include <libmuscle/peer_manager.hpp>
#include <libmuscle/port.hpp>
#include <libmuscle/profiler.hpp>
#include <libmuscle/util.hpp>

#include <ymmsl/ymmsl.hpp>

#include <memory>
#include <string>
#include <unordered_map>
#include <vector>


namespace mock_communicator {

using ::libmuscle::_MUSCLE_IMPL_NS::Message;
using ::libmuscle::_MUSCLE_IMPL_NS::Optional;


using CommunicatorSendMessageBase = MockFun<
    Void, Val<std::string const &>, Val<Message const &>,
    Val<Optional<int>>>;

struct CommunicatorSendMessageMock : CommunicatorSendMessageBase {
    void operator()(
            std::string const & port_name,
            Message const & message,
            Optional<int> slot = {}) {
        CommunicatorSendMessageBase::operator()(port_name, message, slot);
    }
};


using CommunicatorReceiveMessageBase = MockFun<
    Val<Message>, Val<std::string const &>,
    Val<Optional<int>>,
    Val<Optional<Message>>>;

struct CommunicatorReceiveMessageMock : CommunicatorReceiveMessageBase {
    Message operator()(
            std::string const & port_name,
            Optional<int> slot = {},
            Optional<Message> const & default_msg = {})
    {
        return CommunicatorReceiveMessageBase::operator()(
                port_name, slot, default_msg);
    }
};


using CommunicatorClosePortBase = MockFun<
    Void, Val<std::string const &>, Val<Optional<int>>>;

struct CommunicatorClosePortMock : CommunicatorClosePortBase {
    void operator()(std::string const & port_name, Optional<int> slot = {}) {
        CommunicatorClosePortBase::operator()(port_name, slot);
    }
};

}


namespace libmuscle { namespace _MUSCLE_IMPL_NS {

using PortsDescription = std::unordered_map<ymmsl::Operator, std::vector<std::string>>;


class MockCommunicator : public MockClass<MockCommunicator> {
    public:
        using PortMessageCounts = std::unordered_map<std::string, std::vector<int>>;

        MockCommunicator(ReturnValue) {
            NAME_MOCK_MEM_FUN(MockCommunicator, constructor);
            NAME_MOCK_MEM_FUN(MockCommunicator, get_locations);
            NAME_MOCK_MEM_FUN(MockCommunicator, connect);
            NAME_MOCK_MEM_FUN(MockCommunicator, settings_in_connected);
            NAME_MOCK_MEM_FUN(MockCommunicator, list_ports);
            NAME_MOCK_MEM_FUN(MockCommunicator, port_exists);
            NAME_MOCK_MEM_FUN(MockCommunicator, get_port);
            NAME_MOCK_MEM_FUN(MockCommunicator, send_message);
            NAME_MOCK_MEM_FUN(MockCommunicator, receive_message);
            NAME_MOCK_MEM_FUN(MockCommunicator, close_port);
            NAME_MOCK_MEM_FUN(MockCommunicator, shutdown);
            NAME_MOCK_MEM_FUN(MockCommunicator, get_message_counts);
            NAME_MOCK_MEM_FUN(MockCommunicator, restore_message_counts);

            get_locations.return_value = std::vector<std::string>(
                    {"tcp:test1,test2", "tcp:test3"});
            list_ports.return_value = PortsDescription();
        }

        MockCommunicator() {
            init_from_return_value();
        }

        MockCommunicator(
                ymmsl::Reference const & kernel,
                std::vector<int> const & index,
                Optional<PortsDescription> const & declared_ports,
                Logger & logger, Profiler & profiler)
        {
            init_from_return_value();
            constructor(kernel, index, declared_ports, logger, profiler);
        }

        MockFun<
            Void, Val<ymmsl::Reference const &>, Val<std::vector<int> const &>,
            Val<Optional<PortsDescription> const &>, Obj<Logger &>, Obj<Profiler &>>
                constructor;

        MockFun<Val<std::vector<std::string>>> get_locations;

        MockFun<
            Void, Val<std::vector<ymmsl::Conduit> const &>, Val<PeerDims const &>,
            Val<PeerLocations const &>> connect;

        MockFun<Val<bool>> settings_in_connected;

        MockFun<Val<PortsDescription>> list_ports;

        MockFun<Val<bool>, Val<std::string const &>> port_exists;

        MockFun<Obj<Port &>, Val<std::string const &>> get_port;

        ::mock_communicator::CommunicatorSendMessageMock send_message;

        ::mock_communicator::CommunicatorReceiveMessageMock receive_message;

        ::mock_communicator::CommunicatorClosePortMock close_port;

        MockFun<Void> shutdown;

        MockFun<Val<PortMessageCounts>> get_message_counts;

        MockFun<Void, Val<PortMessageCounts const &>> restore_message_counts;
};

using Communicator = MockCommunicator;

} }

