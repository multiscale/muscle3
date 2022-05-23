#pragma once

#include <ymmsl/ymmsl.hpp>

#include <libmuscle/data.hpp>
#include <libmuscle/mpp_message.hpp>
#include <libmuscle/mcp/transport_server.hpp>
#include <libmuscle/outbox.hpp>


namespace libmuscle { namespace impl {


class MockPostOffice : public mcp::RequestHandler {
    public:
        MockPostOffice() = default;

        virtual int handle_request(
                char const * req_buf, std::size_t req_len,
                std::unique_ptr<DataConstRef> & res_buf) override;

        virtual std::unique_ptr<DataConstRef> get_response(int fd) override;

        void deposit(
                ymmsl::Reference const & receiver,
                std::unique_ptr<DataConstRef> message);

        void wait_for_receivers() const;

        // Mock control variables
        static void reset();

        static ymmsl::Reference last_receiver;
        static std::unique_ptr<MPPMessage> last_message;
};

using PostOffice = MockPostOffice;

} }

