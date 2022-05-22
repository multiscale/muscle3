#pragma once

#include <libmuscle/mcp/transport_server.hpp>

#include <ymmsl/ymmsl.hpp>


namespace libmuscle { namespace impl { namespace mcp {

class MockTcpTransportServer : public TransportServer {
    public:
        MockTcpTransportServer(RequestHandler & handler);

        ~MockTcpTransportServer();

        virtual std::string get_location() const;

        virtual void close();

        // Mock control variables
        static void reset();

        static int num_constructed;
};

using TcpTransportServer = MockTcpTransportServer;

} } }

