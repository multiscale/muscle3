#pragma once

#ifdef LIBMUSCLE_MOCK_MCP_TCP_TRANSPORT_SERVER
#include LIBMUSCLE_MOCK_MCP_TCP_TRANSPORT_SERVER
#else

#include <libmuscle/mcp/transport_server.hpp>

#include <condition_variable>
#include <thread>
#include <netdb.h>


namespace libmuscle { namespace impl { namespace mcp {

/** A server that accepts TCP connections.
 */
class TcpTransportServer : public TransportServer {
    public:
        /** Create a TcpTransportServer.
         *
         * @param handler A handler to handler requests
         */
        TcpTransportServer(RequestHandler & handler);

        /** Closes the server if it wasn't already closed.
         */
        ~TcpTransportServer();

        /** Returns the location this server listens on.
         *
         * @return A string containing the location.
         */
        virtual std::string get_location() const;

        /** Closes this server.
         *
         * Stops the server listening, waits for existing clients to disconnect,
         * then frees any other resources.
         */
        virtual void close();

    private:
        std::vector<std::string> get_interfaces_() const;

        using AddrInfoList_ = std::unique_ptr<addrinfo, void (*)(addrinfo*)>;
        AddrInfoList_ get_address_info_(std::string const & address) const;

        std::vector<int> create_sockets_(addrinfo const * addresses) const;

        std::string get_address_string_(int sockfd) const;

        void set_location_(std::string const & location);

        std::vector<int> set_up_sockets_();

        static void server_thread_(TcpTransportServer * self);

        mutable std::mutex mutex_;
        mutable std::condition_variable location_set_;
        int control_pipe_[2];
        std::thread thread_;
        std::string location_;
};

} } }

#endif

