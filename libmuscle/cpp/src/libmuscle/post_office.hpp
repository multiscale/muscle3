#pragma once

#ifdef LIBMUSCLE_MOCK_POST_OFFICE
#include LIBMUSCLE_MOCK_POST_OFFICE
#else


#include <ymmsl/ymmsl.hpp>

#include <libmuscle/mcp/message.hpp>
#include <libmuscle/outbox.hpp>

#include <condition_variable>
#include <memory>
#include <mutex>


namespace libmuscle { namespace impl {


/** Holds messages to be retrieved.
 *
 * A PostOffice holds outboxes with messages for receivers.
 */
class PostOffice {
    public:
        /** Create a PostOffice.
         */
        PostOffice() = default;

        /** Check whether a message is available for the given receiver.
         *
         * @param receiver The receiver to request for.
         * @returns True iff there is at least one message waiting.
         */
        bool has_message(ymmsl::Reference const & receiver);

        /** Get a message from a receiver's outbox.
         *
         * Used by servers to get messages that have been sent to another
         * instance. This dequeues the message, the next call will return
         * the next message.
         *
         * @param receiver The receiver of the message.
         */
        std::unique_ptr<mcp::Message> get_message(
                ymmsl::Reference const & receiver);

        /** Deposit a message into an outbox.
         *
         * @param receiver Receiver of the message.
         * @param message The message to deposit.
         */
        void deposit(
                ymmsl::Reference const & receiver,
                std::unique_ptr<mcp::Message> message);

        /** Waits until all outboxes are empty.
         */
        void wait_for_receivers() const;

    private:
        Outbox & get_outbox_(ymmsl::Reference const & receiver);

        // A mutex that protects outboxes_, but not any individual outbox.
        mutable std::mutex outboxes_mutex_;
        mutable std::condition_variable retrieved_;
        std::unordered_map<ymmsl::Reference, std::unique_ptr<Outbox>> outboxes_;
};

} }

#endif

