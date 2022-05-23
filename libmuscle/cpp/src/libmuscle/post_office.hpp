#pragma once

#ifdef LIBMUSCLE_MOCK_POST_OFFICE
#include LIBMUSCLE_MOCK_POST_OFFICE
#else


#include <libmuscle/data.hpp>
#include <libmuscle/outbox.hpp>
#include <libmuscle/mcp/transport_server.hpp>

#include <msgpack.hpp>
#include <ymmsl/ymmsl.hpp>

#include <condition_variable>
#include <memory>
#include <mutex>


namespace libmuscle { namespace impl {

/** Helper class for managing pipes.
 *
 * Contains a connected pair of open file descriptors, which can be used for
 * one-way communication.
 */
struct Pipe {
    /** Sending and receiving fds. */
    int sending_fd, receiving_fd;

    /** Create a Pipe with freshly allocated fds. */
    Pipe();

    /** Create a Pipe from the given fds. */
    Pipe(int sending_fd, int receiving_fd);

    /** Close file descriptors. */
    void close();
};


/** Holds messages to be retrieved.
 *
 * A PostOffice holds outboxes with messages for receivers.
 */
class PostOffice : public mcp::RequestHandler {
    public:
        /** Create a PostOffice.
         */
        PostOffice() = default;

        /** Destruct a PostOffice.
         */
        ~PostOffice();

        /** Handle a request
         *
         * Requests may be handled immediately, or they may be deferred if a
         * response is not available yet. In the first case, this will place
         * the response as a byte array wrapped in a Data object into res_buf,
         * and return -1.
         *
         * In the second case, res_buf is unmodified, and a file descriptor is
         * returned. When the response is available, a single byte can and must
         * be read from this file descriptor, and get_response must be called to
         * pick up the response.
         *
         * @param req_buf Pointer to request bytes
         * @param req_len Number of bytes in request
         * @param res_buf Out parameter to put the response into, if available
         */
        virtual int handle_request(
                char const * req_buf, std::size_t req_len,
                std::unique_ptr<DataConstRef> & res_buf) override;

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
        virtual std::unique_ptr<DataConstRef> get_response(int fd) override;

        /** Deposit a message into an outbox.
         *
         * The message object should hold a byte array with encoded data.
         *
         * @param receiver Receiver of the message.
         * @param message The message to deposit.
         */
        void deposit(
                ymmsl::Reference const & receiver,
                std::unique_ptr<DataConstRef> message);

        /** Waits until all outboxes are empty.
         */
        void wait_for_receivers() const;

    private:
        Outbox & get_outbox_(ymmsl::Reference const & receiver);

        Pipe get_pipe_();
        void return_pipe_(Pipe const & pipe);

        // A mutex that protects outboxes_ and pending_outboxes_, but not any
        // individual outbox.
        mutable std::mutex outboxes_mutex_;
        mutable std::condition_variable retrieved_;
        std::unordered_map<ymmsl::Reference, std::unique_ptr<Outbox>> outboxes_;
        // Lookup table of outboxes that have a pending read
        std::unordered_map<int, Outbox*> pending_outboxes_;


        // Cache for notification pipes
        mutable std::mutex pipes_mutex_;
        std::vector<Pipe> pipes_;
};

} }

#endif

