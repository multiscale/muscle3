#pragma once

#include <libmuscle/mcp/message.hpp>
#include <ymmsl/identity.hpp>

#include <string>


namespace libmuscle { namespace impl { namespace mcp {

/** A client that connects to an MCP server.
 *
 * This is a base class for MCP Clients. An MCP Client connects to an MCP
 * Server over some lower-level communication protocol, and requests messages
 * from it.
 */
class Client {
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
         * Note that all functionality is in derived classes, this constructor
         * is here for reference. All derived classes must implement it.
         *
         * @param instance_id Id of our instance.
         * @param location A location string from the peer.
         */
        Client(::ymmsl::Reference const & instance_id, std::string const & location);

        /** Clients are not copyable.
         */
        Client(Client const & rhs) = delete;

        /** Clients are not copy-assignable.
         */
        Client & operator=(Client const & rhs) = delete;

        /** Clients are not moveable.
         */
        Client(Client && rhs) = delete;

        /** Clients are not move-assignable
         */
        Client & operator=(Client && rhs) = delete;

        /** Destruct the Client.
         */
        virtual ~Client() = 0;

        /** Receive a message from a port this client connects to.
         *
         * @param The receiving (local) port.
         *
         * @return The recived message.
         */
        virtual Message receive(::ymmsl::Reference const & receiver) = 0;

        /** Closes this client.
         *
         * This closes any connections this client has and/or performs other
         * shutdown activities.
         */
        virtual void close() = 0;
};

} } }

