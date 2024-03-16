#pragma once

#include <libmuscle/mcp/transport_client.hpp>
#include <libmuscle/mpp_message.hpp>
#include <libmuscle/namespace.hpp>
#include <libmuscle/profiling.hpp>
#include <mocks/mock_support.hpp>

#include <ymmsl/ymmsl.hpp>

#include <string>
#include <tuple>
#include <vector>


namespace libmuscle { namespace _MUSCLE_IMPL_NS {


class MockMPPClient : public MockClass<MockMPPClient> {
    public:
        MockMPPClient(ReturnValue) {
            NAME_MOCK_MEM_FUN(MockMPPClient, constructor);
            NAME_MOCK_MEM_FUN(MockMPPClient, receive);
            NAME_MOCK_MEM_FUN(MockMPPClient, close);
        }

        MockMPPClient(std::vector<std::string> const & locations) {
            init_from_return_value();
            constructor(locations);
        }

        MockFun<Void, Val<std::vector<std::string> const &>> constructor;

        MockFun<
            Val<std::tuple<std::vector<char>, mcp::ProfileData>>,
            Val<::ymmsl::Reference const &>
            > receive;

        MockFun<Void> close;
};

using MPPClient = MockMPPClient;

} }

