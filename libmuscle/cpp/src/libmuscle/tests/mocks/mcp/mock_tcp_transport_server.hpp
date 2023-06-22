#pragma once

#include <libmuscle/mcp/transport_server.hpp>
#include <libmuscle/namespace.hpp>

#include <ymmsl/ymmsl.hpp>


namespace libmuscle { namespace _MUSCLE_IMPL_NS { namespace mcp {

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

