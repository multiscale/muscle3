#pragma once

#include <libmuscle/mcp/client.hpp>


namespace libmuscle { namespace mcp {

class MockTcpClient : public Client {
    public:
        static bool can_connect_to(std::string const & location);

        static void shutdown(::ymmsl::Reference const & instance_id);

        MockTcpClient(::ymmsl::Reference const & instance_id, std::string const & location);
        MockTcpClient(MockTcpClient const & rhs) = delete;
        MockTcpClient & operator=(MockTcpClient const & rhs) = delete;
        MockTcpClient(MockTcpClient && rhs) = delete;
        MockTcpClient & operator=(MockTcpClient && rhs) = delete;
        virtual ~MockTcpClient() override;

        virtual Message receive(::ymmsl::Reference const & receiver) override;

        virtual void close() override;

        // Mock control variables
        static void reset();

        static int num_constructed;
        static Message next_receive_message;
        static ::ymmsl::Reference last_receiver;

    private:
        static ::ymmsl::Settings make_overlay_();
};

using TcpClient = MockTcpClient;

} }

