#pragma once

#include <ymmsl/ymmsl.hpp>

#include <libmuscle/data.hpp>
#include <libmuscle/mpp_message.hpp>
#include <libmuscle/mcp/transport_server.hpp>
#include <libmuscle/namespace.hpp>
#include <libmuscle/outbox.hpp>

#include <memory>


namespace mock_post_office {

using ::libmuscle::_MUSCLE_IMPL_NS::DataConstRef;
using ::libmuscle::_MUSCLE_IMPL_NS::MPPMessage;

struct EncodedMessage {
    using ArgType = std::unique_ptr<DataConstRef>;
    using StorageType = std::shared_ptr<MPPMessage>;

    static StorageType arg_to_store(ArgType const & message) {
        return std::make_shared<MPPMessage>(MPPMessage::from_bytes(*message));
    }

    static ArgType store_to_arg(StorageType const & stored) {
        return std::make_unique<DataConstRef>(stored->encoded());
    }
};

struct EncodedMessageOut {
    using ArgType = std::unique_ptr<DataConstRef> &;
    using StorageType = DataConstRef *;

    static StorageType arg_to_store(ArgType const & buffer) {
        return buffer.get();
    }
};

}


namespace libmuscle { namespace _MUSCLE_IMPL_NS {


class MockPostOffice : public MockClass<MockPostOffice>, public mcp::RequestHandler {
    public:
        MockPostOffice(ReturnValue) {
            NAME_MOCK_MEM_FUN(MockPostOffice, constructor);
            NAME_MOCK_MEM_FUN(MockPostOffice, handle_request_mock);
            NAME_MOCK_MEM_FUN(MockPostOffice, get_response_mock);
            NAME_MOCK_MEM_FUN(MockPostOffice, deposit);
            NAME_MOCK_MEM_FUN(MockPostOffice, wait_for_receivers);
        }

        MockPostOffice() {
            init_from_return_value();
            constructor();
        }

        MockFun<Void> constructor;

        /* Virtual member functions cannot be overridden by an object, so we override
         * them with a function and then forward to the mock.
         */
        MockFun<
            Val<int>,
            Val<char const *, const char *>, Val<std::size_t>,
            ::mock_post_office::EncodedMessageOut
        > handle_request_mock;

        virtual int handle_request(
                char const * req_buf, std::size_t req_len,
                std::unique_ptr<DataConstRef> & res_buf) override
        {
            return std::move(handle_request_mock(req_buf, req_len, res_buf));
        }

        MockFun<::mock_post_office::EncodedMessage, Val<int>> get_response_mock;

        virtual std::unique_ptr<DataConstRef> get_response(int fd) override {
            return get_response_mock(fd);
        }

        MockFun<Void,
            Val<ymmsl::Reference const &>, ::mock_post_office::EncodedMessage
        > deposit;

        MockFun<Void> wait_for_receivers;
};


using PostOffice = MockPostOffice;

} }

