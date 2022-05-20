#pragma once

#include <string>
#include <vector>


namespace libmuscle { namespace impl { namespace mcp {

/** Handles requests sent to a TransportServer.
 *
 * TransportServers operate in terms of chunks of bytes received and
 * sent in return. RequestHandlers interpret received chunks of bytes,
 * handle the request, and return a chunk of bytes containing an
 * encoded response.
 */
class RequestHandler {
public:
    /** Handle a request
     *
     * Requests may be handled immediately, or they may be deferred if a
     * response is not available yet. In the first case, this will resize
     * res_buf to fit the response, write it into res_buf, and return -1.
     * In the second case, res_buf is unmodified, and a file descriptor is
     * returned. When the response is available, a single byte can and must
     * be read from this file descriptor, and get_response must be called to
     * pick up the response.
     */
    virtual int handle_request(char const * req_buf, std::size_t req_len, std::vector<char> & res_buf) = 0;

    /** Get a response
     *
     * This function must be called only when a previous call to
     * handle_request returned a file descriptor. When this file descriptor
     * becomes ready, read a byte from it and call this function, passing the
     * file descriptor. The response will then be written into res_buf.
     */
    virtual void get_response(int fd, std::vector<char> & res_buf) = 0;
};


/** A server that accepts MCP connections.
 *
 * This is a base class for MCP Servers. An MCP Server accepts connections
 * over some lower-level communication protocol, receives requests and
 * returns responses from a RequestHandler.
 */
class TransportServer {
    public:
        /** Create a TransportServer.
         *
         * @param handler: A handler to handle requests
         */
        TransportServer(RequestHandler & handler);

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
        RequestHandler & handler_;
};

} } }

