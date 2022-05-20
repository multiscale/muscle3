#pragma once

#ifdef LIBMUSCLE_MOCK_MCP_TCP_TRANSPORT_CLIENT
#include LIBMUSCLE_MOCK_MCP_TCP_TRANSPORT_CLIENT
#else

#include <libmuscle/mcp/transport_client.hpp>


namespace libmuscle { namespace impl { namespace mcp {

/** A client that connects to a TCPTransport server.
 */
class TcpTransportClient : public TransportClient {
    public:
        /** Whether this client class can connect to the given location.
         *
         * @param location The location to potentially connect to.
         *
         * @return true iff this class can connect to this location.
         */
        static bool can_connect_to(std::string const & location);

        /** Create an MCP Transport Client for a given location.
         *
         * The client will connect to this location and be able to send
         * requests to it.
         *
         * @param location A location string to connect to.
         */
        TcpTransportClient(std::string const & location);

        /** Destruct the TcpTransportClient.
         */
        virtual ~TcpTransportClient() override;

        /** Send a request to the server and receive the response.
         *
         * This is a blocking call.
         *
         * @param req_buf Pointer to the request to send
         * @param req_len Length of the request in bytes
         * @param result Buffer to put the result into, will be resized as
         *      needed.
         */
        virtual void call(
                char const * req_buf, std::size_t req_len,
                std::vector<char> & result) const override;

        /** Closes this client.
         *
         * This closes any connections this client has and/or performs other
         * shutdown activities.
         */
        virtual void close() override;

    private:
        int socket_fd_;
};

} } }

#endif

