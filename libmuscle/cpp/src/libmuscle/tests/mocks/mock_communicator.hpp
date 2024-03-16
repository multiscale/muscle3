#pragma once

#include <libmuscle/logger.hpp>
#include <libmuscle/message.hpp>
#include <libmuscle/namespace.hpp>
#include <libmuscle/peer_info.hpp>
#include <libmuscle/port.hpp>
#include <libmuscle/port_manager.hpp>
#include <libmuscle/profiler.hpp>
#include <libmuscle/util.hpp>

#include <ymmsl/ymmsl.hpp>

#include <mocks/mock_support.hpp>

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
    Val<std::tuple<Message, double>>, Val<std::string const &>,
    Val<Optional<int>>,
    Val<Optional<Message>>>;

struct CommunicatorReceiveMessageMock : CommunicatorReceiveMessageBase {
    std::tuple<Message, double> operator()(
            std::string const & port_name,
            Optional<int> slot = {},
            Optional<Message> const & default_msg = {})
    {
        return CommunicatorReceiveMessageBase::operator()(
                port_name, slot, default_msg);
    }

    bool called_with(
            std::string const & port_name,
            Optional<int> slot = {},
            Optional<Message> const & default_msg = {}) const
    {
        return CommunicatorReceiveMessageBase::called_with(
                port_name, slot, default_msg);
    }

    bool called_once_with(
            std::string const & port_name,
            Optional<int> slot = {},
            Optional<Message> const & default_msg = {}) const
    {
        return CommunicatorReceiveMessageBase::called_once_with(
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
            NAME_MOCK_MEM_FUN(MockCommunicator, set_peer_info);
            NAME_MOCK_MEM_FUN(MockCommunicator, send_message);
            NAME_MOCK_MEM_FUN(MockCommunicator, receive_message);
            NAME_MOCK_MEM_FUN(MockCommunicator, shutdown);
        }

        MockCommunicator() {
            init_from_return_value();
        }

        MockCommunicator(
                ymmsl::Reference const & kernel,
                std::vector<int> const & index,
                PortManager & port_manager,
                Logger & logger, Profiler & profiler)
        {
            init_from_return_value();
            constructor(kernel, index, port_manager, logger, profiler);
        }

        MockFun<
            Void, Val<ymmsl::Reference const &>, Val<std::vector<int> const &>,
            Obj<PortManager &>, Obj<Logger &>, Obj<Profiler &>>
                constructor;

        MockFun<Val<std::vector<std::string>>> get_locations;

        MockFun<Void, Val<PeerInfo const &>> set_peer_info;

        MockFun<
            Void, Val<std::vector<ymmsl::Conduit> const &>, Val<PeerDims const &>,
            Val<PeerLocations const &>> connect;

        ::mock_communicator::CommunicatorSendMessageMock send_message;

        ::mock_communicator::CommunicatorReceiveMessageMock receive_message;

        MockFun<Void> shutdown;
};

using Communicator = MockCommunicator;

} }

