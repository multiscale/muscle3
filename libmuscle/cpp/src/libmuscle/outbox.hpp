#pragma once

#include <libmuscle/data.hpp>
#include <libmuscle/namespace.hpp>

#include <ymmsl/ymmsl.hpp>

#include <condition_variable>
#include <memory>
#include <mutex>
#include <vector>

namespace libmuscle { namespace _MUSCLE_IMPL_NS {


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
        Outbox();

        /** Lock this Outbox so other threads can't access it.
         *
         * If multiple threads may access this object, then it must be locked
         * while calling any member function.
         *
         * @return A unique_lock holding an internal mutex.
         */
        std::unique_lock<std::mutex> lock();

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
         * returned to the caller. It is an error if no message is present
         * in the queue.
         *
         * @return The next message.
         *
         * @throws std::runtime_error If no message is available.
         */
        std::unique_ptr<DataConstRef> retrieve();

        /** Sets fd to notify deposition on.
         *
         * @param fd The fd to send a byte to when a message is deposited.
         */
        void set_notification_fd(int fd);

        /** Resets notification fd and returns original value.
         *
         * @return The current notification fd.
         */
        int return_notification_fd();

    private:
        mutable std::mutex mutex_;
        std::vector<std::unique_ptr<DataConstRef>> queue_;
        int notification_fd_;
};

} }

