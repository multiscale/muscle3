#pragma once

#include <libmuscle/namespace.hpp>
#include <libmuscle/profiling.hpp>

#include <string>
#include <tuple>
#include <vector>


namespace libmuscle { namespace _MUSCLE_IMPL_NS { namespace mcp {


/** Timeline of a receive.
 *
 * This is (start, end of wait and beginning of transfer, end)
 */
using ProfileData = std::tuple<
        ProfileTimestamp, ProfileTimestamp, ProfileTimestamp>;


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
         * This is a blocking call. Besides the result, this function
         * returns a tuple with three timestamps. These were taken when
         * the function was first called, when data became available and
         * the transfer started, and when the transfer stopped.
         *
         * @param req_buf Pointer to the request to send
         * @param req_len Length of the request in bytes
         *
         * @return std::vector<char> containing a byte array with the
         *         received data, and the timestamps.
         */
        virtual std::tuple<std::vector<char>, ProfileData> call(
                char const * req_buf, std::size_t req_len) const = 0;

        /** Closes this client.
         *
         * This closes any connections this client has and/or performs other
         * shutdown activities.
         */
        virtual void close() = 0;
};

} } }

