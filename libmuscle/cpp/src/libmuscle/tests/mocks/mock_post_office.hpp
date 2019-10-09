#pragma once

#include <ymmsl/ymmsl.hpp>

#include "libmuscle/mcp/message.hpp"
#include "libmuscle/outbox.hpp"


namespace libmuscle { namespace impl {


class MockPostOffice {
    public:
        MockPostOffice() = default;

        bool has_message(ymmsl::Reference const & receiver);

        std::unique_ptr<mcp::Message> get_message(
                ymmsl::Reference const & receiver);

        void deposit(
                ymmsl::Reference const & receiver,
                std::unique_ptr<mcp::Message> message);

        void wait_for_receivers() const;

        // Mock control variables
        static void reset();

        static ymmsl::Reference last_receiver;
        static std::unique_ptr<mcp::Message> last_message;
};

using PostOffice = MockPostOffice;

} }

