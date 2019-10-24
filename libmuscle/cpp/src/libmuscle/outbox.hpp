#pragma once

#include <libmuscle/data.hpp>

#include <ymmsl/ymmsl.hpp>

#include <condition_variable>
#include <memory>
#include <mutex>
#include <vector>

namespace libmuscle { namespace impl {


/** Stores messages to be sent to a particular receiver.
 *
 * An Outbox is a queue of messages, which may be deposited and then retrieved
 * in the same order.
 *
 * Outbox is thread-safe, so you can deposit and retrieve from different
 * threads without any additional locking.
 */
class Outbox {
    public:
        /** Create an empty Outbox.
         */
        Outbox() = default;

        /** Returns true iff the outbox is empty.
         */
        bool is_empty() const;

        /** Put a message in the Outbox.
         *
         * The message will be placed at the back of a queue, and may be
         * retrieved later via retrieve().
         *
         * @param message The message to store.
         */
        void deposit(std::unique_ptr<DataConstRef> message);

        /** Retrieve a message from the Outbox.
         *
         * The message will be removed from the front of the queue, and
         * returned to the caller. Blocks if the queue is empty, until a
         * message is deposited.
         *
         * @return The next message.
         */
        std::unique_ptr<DataConstRef> retrieve();

    private:
        std::vector<std::unique_ptr<DataConstRef>> queue_;
        mutable std::mutex mutex_;
        mutable std::condition_variable deposited_;
};

} }

