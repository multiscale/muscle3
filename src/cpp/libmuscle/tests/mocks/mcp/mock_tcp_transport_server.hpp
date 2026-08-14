#pragma once

#include <libmuscle/mcp/transport_server.hpp>
#include <libmuscle/namespace.hpp>

#include <ymmsl/ymmsl.hpp>


namespace libmuscle { namespace _MUSCLE_IMPL_NS { namespace mcp {

class MockTcpTransportServer
    : public MockClass<MockTcpTransportServer>
    , public TransportServer
{
    public:
        MockTcpTransportServer(ReturnValue) {
            NAME_MOCK_MEM_FUN(MockTcpTransportServer, constructor);
            NAME_MOCK_MEM_FUN(MockTcpTransportServer, get_location_mock);
            NAME_MOCK_MEM_FUN(MockTcpTransportServer, close_mock);
        }

        MockTcpTransportServer(RequestHandler & handler) {
            init_from_return_value();
            constructor(handler);
        }

        MockFun<Void, Obj<RequestHandler &>> constructor;

        virtual std::string get_location() const override {
            return get_location_mock();
        }

        mutable MockFun<Val<std::string>> get_location_mock;

        virtual void close() override {
            return close_mock();
        }

        MockFun<Void> close_mock;
};

using TcpTransportServer = MockTcpTransportServer;

} } }

