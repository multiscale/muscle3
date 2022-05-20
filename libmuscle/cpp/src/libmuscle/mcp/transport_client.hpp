#pragma once

#include <string>
#include <vector>


namespace libmuscle { namespace impl { namespace mcp {

/** A client that connects to an MCP transport server.
 *
 * This is a base class for MCP Transport Clients. An MCP Transport Client
 * connects to an MCP Transport Server over some lower-level communication
 * protocol, and sends requests to it.
 */
class TransportClient {
    public:
        /** Whether this client class can connect to the given location.
         *
         * @param location The location to potentially connect to.
         *
         * @return true iff this class can connect to this location.
         */
        static bool can_connect_to(std::string const & location);

        /** Clients can be created.
         */
        TransportClient() = default;

        /** Clients are not copyable.
         */
        TransportClient(TransportClient const & rhs) = delete;

        /** Clients are not copy-assignable.
         */
        TransportClient & operator=(TransportClient const & rhs) = delete;

        /** Clients are not moveable.
         */
        TransportClient(TransportClient && rhs) = delete;

        /** Clients are not move-assignable
         */
        TransportClient & operator=(TransportClient && rhs) = delete;

        /** Destruct the Client.
         */
        virtual ~TransportClient() = 0;

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
                std::vector<char> & result) const = 0;

        /** Closes this client.
         *
         * This closes any connections this client has and/or performs other
         * shutdown activities.
         */
        virtual void close() = 0;
};

} } }

