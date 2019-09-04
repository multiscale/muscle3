#pragma once

#include <libmuscle/mcp/client.hpp>


namespace libmuscle { namespace mcp {

/** A client that connects to an MCP server.
 *
 * This is a base class for MCP Clients. An MCP Client connects to an MCP
 * Server over some lower-level communication protocol, and requests messages
 * from it.
 */
class TcpClient : public Client {
    public:
        /** Whether this client class can connect to the given location.
         *
         * @param location The location to potentially connect to.
         *
         * @return true iff this class can connect to this location.
         */
        static bool can_connect_to(std::string const & location);

        /** Shut down and free any resources shared by all clients.
         *
         * This is an optional hook for communication subsystems that need it. If
         * implemented, it must work correctly even if no clients have ever been
         * instantiated.
         *
         * This will be called after all clients of this class have been closed.
         */
        static void shutdown(::ymmsl::Reference const & instance_id);

        /** Create an MCP Client for a given location.
         *
         * The client will connect to this location and be able to request messages
         * from any compute element and port represented by it.
         *
         * @param instance_id Id of our instance.
         * @param location A location string from the peer.
         */
        TcpClient(::ymmsl::Reference const & instance_id, std::string const & location);

        /** Clients are not copyable.
         */
        TcpClient(TcpClient const & rhs) = delete;

        /** Clients are not copy-assignable.
         */
        TcpClient & operator=(TcpClient const & rhs) = delete;

        /** Move-construct a new TcpClient.
         */
        TcpClient(TcpClient && rhs) = delete;

        /** Move-assign a TcpClient.
         */
        TcpClient & operator=(TcpClient && rhs) = delete;

        /** Destruct the TcpClient.
         */
        virtual ~TcpClient() override;

        /** Receive a message from a port this client connects to.
         *
         * @param The receiving (local) port.
         *
         * @return The recived message.
         */
        virtual Message receive(::ymmsl::Reference const & receiver) override;

        /** Closes this client.
         *
         * This closes any connections this client has and/or performs other
         * shutdown activities.
         */
        virtual void close() override;

    private:
        int socket_fd_;
};

} }

