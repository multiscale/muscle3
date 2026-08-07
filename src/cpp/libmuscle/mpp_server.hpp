#pragma once

#ifdef LIBMUSCLE_MOCK_MPP_SERVER
#include LIBMUSCLE_MOCK_MPP_SERVER
#else

#include <libmuscle/mcp/transport_server.hpp>
#include <libmuscle/namespace.hpp>
#include <libmuscle/post_office.hpp>
#include <libmuscle/test_support.hpp>

#include <vector>


namespace libmuscle { namespace _MUSCLE_IMPL_NS {

/** Handles peer protocol requests.
 *
 * This accepts peer protocol message requests and responds to them by
 * getting messages from a PostOffice.
 */
class MPPRequestHandler : public mcp::RequestHandler {
    public:
        /** Create an MPPRequestHnadler.
         *
         * @param post_office The PostOffice to get messages from
         */
        MPPRequestHandler(PostOffice & post_office);

        /** Destruct the object */
        virtual ~MPPRequestHandler() = default;

        /** Handle a request.
         *
         * This receives an MCP request and handles it by blocking until
         * the requested message is available, then returning it.
         *
         * @param req_buf Pointer to request bytes
         * @param req_len Number of bytes in request
         * @param res_buf Out parameter to put the response into, if available
         */
        virtual int handle_request(
                char const * req_buf, std::size_t req_len,
                std::vector<char> & res_buf) override;

        /** Get a response
         *
         * This function must be called only when a previous call to
         * handle_request returned a file descriptor. When this file descriptor
         * becomes ready, read a byte from it and call this function, passing the
         * file descriptor. The response will then be written into res_buf.
         *
         * @param fd File descriptor to return
         * @return A byte array wrapped in a DataConstRef with the response
         */
        virtual std::vector<char> get_response(int fd) override;


    PRIVATE:
        PostOffice & post_office_;
};


/** Serves MPP requests.
 *
 * This manages a collection of servers for different protocols and a
 * PostOffice that stores outgoing messages.
 */
class MPPServer {
    public:
        /** Create an MPPServer. */
        MPPServer();

        /** Returns a list of locations that we can be reached at.
         *
         * These locations are of the form 'protocol:location', where
         * the protocol name does not contain a colon and location may
         * be an arbitrary string.
         *
         * @return A list of strings describing network locations.
         */
        std::vector<std::string> get_locations() const;

        /** Deposits a message for the receiver to retrieve.
         *
         * @param receiver Receiver of the message
         * @param message The message to deposit
         */
        void deposit(
                ymmsl::Reference const & receiver,
                std::vector<char> && message);

        /** Waits for all deposited messages to have been received. */
        void wait_for_receivers() const;

        /** Shut down all servers. */
        void shutdown();

    PRIVATE:
        PostOffice post_office_;
        MPPRequestHandler handler_;
        std::vector<std::unique_ptr<mcp::TransportServer>> servers_;
};

} }

#endif

