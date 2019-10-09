#pragma once

#include <libmuscle/post_office.hpp>
#include <ymmsl/identity.hpp>

#include <string>


namespace libmuscle { namespace impl { namespace mcp {

/** A server that accepts MCP connections.
 *
 * This is a base class for MCP Servers. An MCP Server accepts connections
 * over some lower-level communication protocol, and processes message
 * requests by sending the requested message.
 */
class Server {
    public:
        /** Create a Server.
         *
         * @param instance_id Id of the instance we're a server for.
         * @param post_office: A PostOffice to obtain messages from.
         */
        Server(ymmsl::Reference const & instance_id, PostOffice & post_office);

        /** Returns the location this server listens on.
         *
         * @return A string containing the location.
         */
        virtual std::string get_location() const = 0;

        /** Closes this server.
         *
         * Stops the server listening, waits for existing clients to disconnect,
         * then frees any other resources.
         */
        virtual void close() = 0;

    protected:
        ymmsl::Reference instance_id_;
        ::libmuscle::impl::PostOffice & post_office_;
};

} } }

