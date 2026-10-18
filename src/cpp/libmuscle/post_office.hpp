#pragma once

#ifdef LIBMUSCLE_MOCK_POST_OFFICE
#include LIBMUSCLE_MOCK_POST_OFFICE
#else


#include <libmuscle/namespace.hpp>
#include <libmuscle/outbox.hpp>

#include <ymmsl/ymmsl.hpp>

#include <condition_variable>
#include <memory>
#include <mutex>
#include <vector>


namespace libmuscle { namespace _MUSCLE_IMPL_NS {

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
class PostOffice {
    public:
        /** Create a PostOffice.
         */
        PostOffice() = default;

        /** Destruct a PostOffice.
         */
        ~PostOffice();

        /** Try to retrieve a message
         *
         * If a message for the given receiver is available, then it will be
         * put into res_buf and -1 is returned. If no message is available,
         * res_buf is left unmodified and a file descriptor is returned. When
         * the response is available, a single byte can and must be read from
         * this file descriptor, and get_response must be called to pick up
         * the response.
         *
         * @param receiver Receiver to get a message for
         * @param res_buf Out parameter to put the response into, if available
         */
        int try_retrieve(
                ymmsl::Reference const & receiver, std::vector<char> & res_buf);

        /** Get a previously requested message
         *
         * This function must be called only when a previous call to
         * try_retrieve returned a file descriptor. When this file descriptor
         * becomes ready, read a byte from it and call this function, passing the
         * file descriptor. The message will then be returned and the file
         * descriptor invalidated.
         *
         * @param fd File descriptor to return
         * @return A byte array with the encoded response
         */
        std::vector<char> get_message(int fd);

        /** Deposit a message into an outbox.
         *
         * The message object should hold a byte array with encoded data, which
         * will be moved into an outbox.
         *
         * @param receiver Receiver of the message.
         * @param message The message to deposit.
         */
        void deposit(
                ymmsl::Reference const & receiver,
                std::vector<char> && message);

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

