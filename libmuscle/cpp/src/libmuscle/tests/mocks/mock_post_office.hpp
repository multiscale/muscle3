#pragma once

#include <ymmsl/ymmsl.hpp>

#include <libmuscle/data.hpp>
#include <libmuscle/mpp_message.hpp>
#include <libmuscle/mcp/transport_server.hpp>
#include <libmuscle/namespace.hpp>
#include <libmuscle/outbox.hpp>

#include <libmuscle/tests/mocks/mock_encoded_message.hpp>
#include <libmuscle/tests/mocks/mock_support.hpp>

#include <memory>


namespace libmuscle { namespace _MUSCLE_IMPL_NS {


class MockPostOffice : public MockClass<MockPostOffice> {
    public:
        MockPostOffice(ReturnValue) {
            NAME_MOCK_MEM_FUN(MockPostOffice, constructor);
            NAME_MOCK_MEM_FUN(MockPostOffice, try_retrieve);
            NAME_MOCK_MEM_FUN(MockPostOffice, get_message);
            NAME_MOCK_MEM_FUN(MockPostOffice, deposit);
            NAME_MOCK_MEM_FUN(MockPostOffice, wait_for_receivers);
        }

        MockPostOffice() {
            init_from_return_value();
            constructor();
        }

        MockFun<Void> constructor;

        MockFun<
            Val<int>, Val<ymmsl::Reference const &>,
            ::mock_encoded_message::EncodedMessageOut> try_retrieve;

        MockFun<::mock_encoded_message::EncodedMessageRet, Val<int>> get_message;

        MockFun<Void,
            Val<ymmsl::Reference const &>, ::mock_encoded_message::EncodedMessage
        > deposit;

        MockFun<Void> wait_for_receivers;
};


using PostOffice = MockPostOffice;

} }

