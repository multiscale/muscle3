#pragma once

#include <ymmsl/ymmsl.hpp>

#include <libmuscle/mcp/transport_server.hpp>
#include <libmuscle/namespace.hpp>
#include <libmuscle/tests/mocks/mock_encoded_message.hpp>
#include <libmuscle/tests/mocks/mock_support.hpp>

#include <vector>


namespace libmuscle { namespace _MUSCLE_IMPL_NS {


class MockMPPServer : public MockClass<MockMPPServer> {
    public:
        MockMPPServer(ReturnValue) {
            NAME_MOCK_MEM_FUN(MockMPPServer, constructor);
            NAME_MOCK_MEM_FUN(MockMPPServer, get_locations);
            NAME_MOCK_MEM_FUN(MockMPPServer, deposit);
            NAME_MOCK_MEM_FUN(MockMPPServer, wait_for_receivers);
            NAME_MOCK_MEM_FUN(MockMPPServer, shutdown);
        }

        MockMPPServer() {
            init_from_return_value();
            constructor();
        }

        MockFun<Void> constructor;

        MockFun<Val<std::vector<std::string>>> get_locations;

        MockFun<Void,
            Val<ymmsl::Reference const &>, ::mock_encoded_message::EncodedMessage
        > deposit;

        MockFun<Void> wait_for_receivers;

        MockFun<Void> shutdown;
};


using MPPServer = MockMPPServer;

} }

