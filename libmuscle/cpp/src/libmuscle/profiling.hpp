#pragma once

#include <cstddef>
#include <cstdint>

#include <libmuscle/namespace.hpp>
#include <libmuscle/timestamp.hpp>
#include <libmuscle/util.hpp>
#include <ymmsl/ymmsl.hpp>


namespace libmuscle { namespace _MUSCLE_IMPL_NS {

/** Profiling event types for MUSCLE3.
 *
 * These match the definitions on the Python side, and should be kept in sync.
 *
 * The underscore on register_ is just there because it's a keyword.
 */
enum class ProfileEventType {
    register_ = 0,
    connect = 4,
    send = 2,
    receive = 3,
    receive_wait = 5,
    receive_transfer = 6,
    receive_decode = 7,
    disconnect_wait = 8,
    deregister = 1
};


/** A timestamp for profiling.
 *
 * This has higher resolution than Timestamp, storing a number of
 * nanoseconds since the epoch in an int64_t. The epoch is usually
 * close to the UNIX epoch.
 */
class ProfileTimestamp {
    public:
        /** Create a timestamp.
         */
        ProfileTimestamp();

        /** Create a timestamp for a given time point.
         *
         * @param nanoseconds: Time to set. If unset, use the current time.
         */
        ProfileTimestamp(int64_t nanoseconds);

        /// Number of nanoseconds since the epoch.
        int64_t nanoseconds;

    private:
        static int64_t time_ref_;
};

std::ostream & operator<<(std::ostream & os, ProfileTimestamp ts);


/** A profile event as used by MUSCLE3.
 *
 * This represents a single measurement of the timing of some event that
 * occurred while executing the simulation.
 */
class ProfileEvent {
    public:
        /** Create a ProfileEvent.
         *
         * @param event_type Type of event that was measured.
         * @param start_time When the even started (real-world, not simulation
         *      time).
         * @param stop_time When the event ended (real-world, not simulation
         *      time).
         * @param port Port used for sending or receiving, if applicable.
         * @param port_length Length of that port, if a vector.
         * @param slot Slot that was sent or received on, if applicable.
         * @param message_size Size of the message involved, if applicable.
         * @param message_timestamp Timestamp sent with the message, if
         *      applicable.
         */
        ProfileEvent(
                ProfileEventType event_type,
                Optional<ProfileTimestamp> start_time = Optional<ProfileTimestamp>(),
                Optional<ProfileTimestamp> stop_time = Optional<ProfileTimestamp>(),
                Optional<ymmsl::Port> const & port = Optional<ymmsl::Port>(),
                Optional<int> port_length = Optional<int>(),
                Optional<int> slot = Optional<int>(),
                Optional<int> message_number = Optional<int>(),
                Optional<std::size_t> message_size = Optional<std::size_t>(),
                Optional<double> message_timestamp = Optional<double>());

        /** Sets start_time to the current time. */
        void start();

        /** Sets stop_time to the current time. */
        void stop();

        /// Type of event that was measured.
        ProfileEventType event_type;

        /// When the event started (real-world, not simulation time).
        Optional<ProfileTimestamp> start_time;

        /// When the event ended (real-world, not simulation time).
        Optional<ProfileTimestamp> stop_time;

        /// Port used for sending or receiving, if applicable.
        Optional<ymmsl::Port> port;

        /// Length of that port, if a vector.
        Optional<int> port_length;

        /// Slot that was sent or received on, if applicable.
        Optional<int> slot;

        /// Number of the message involved, if applicable. Starts at 0.
        Optional<int> message_number;

        /// Size of the message involved, if applicable.
        Optional<std::size_t> message_size;

        /// Timestamp sent with the message, if applicable.
        Optional<double> message_timestamp;
};

} }

