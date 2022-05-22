#pragma once

#include <libmuscle/mcp/message.hpp>

#include <ymmsl/ymmsl.hpp>

#include <string>
#include <vector>


namespace libmuscle { namespace impl {

class MockMPPClient {
    public:
        MockMPPClient(std::vector<std::string> const & locations);
        MockMPPClient(MockMPPClient const & rhs) = delete;
        MockMPPClient & operator=(MockMPPClient const & rhs) = delete;
        MockMPPClient(MockMPPClient && rhs) = delete;
        MockMPPClient & operator=(MockMPPClient && rhs) = delete;
        ~MockMPPClient();

        DataConstRef receive(::ymmsl::Reference const & receiver);

        void close();

        // Mock control variables
        static void reset();

        static int num_constructed;
        static mcp::Message next_receive_message;
        static ::ymmsl::Reference last_receiver;

    private:
        static ::ymmsl::Settings make_overlay_();
};

using MPPClient = MockMPPClient;

} }

