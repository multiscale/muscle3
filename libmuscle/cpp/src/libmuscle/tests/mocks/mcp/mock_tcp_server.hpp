#pragma once

#include <libmuscle/mcp/server.hpp>


namespace libmuscle { namespace mcp {

class MockTcpServer : public Server {
    public:
        MockTcpServer(ymmsl::Reference const & instance_id, PostOffice & post_office);

        ~MockTcpServer();

        virtual std::string get_location() const;

        virtual void close();

        // Mock control variables
        static void reset();

        static int num_constructed;
        static ymmsl::Reference last_instance_id;
};

using TcpServer = MockTcpServer;

} }

