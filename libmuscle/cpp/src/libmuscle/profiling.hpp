#pragma once

#include <cstddef>

#include <libmuscle/timestamp.hpp>
#include <libmuscle/util.hpp>
#include <ymmsl/ymmsl.hpp>


namespace libmuscle { namespace impl {

/** Profiling event types for MUSCLE3.
 *
 * These match the definitions on the Python side, and should be kept in sync.
 *
 * The underscore on register_ is just there because it's a keyword.
 */
enum class ProfileEventType {
    register_ = 0,
    connect = 4,
    deregister = 1,
    send = 2,
    receive = 3,
    receive_wait = 5,
    receive_transfer = 6,
    receive_decode = 7
};


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
                Optional<Timestamp> start_time = Optional<Timestamp>(),
                Optional<Timestamp> stop_time = Optional<Timestamp>(),
                Optional<ymmsl::Port> const & port = Optional<ymmsl::Port>(),
                Optional<int> port_length = Optional<int>(),
                Optional<int> slot = Optional<int>(),
                Optional<std::size_t> message_size = Optional<std::size_t>(),
                Optional<double> message_timestamp = Optional<double>());

        /** Sets start_time to the current time. */
        void start();

        /** Sets stop_time to the current time. */
        void stop();

        /// Type of event that was measured.
        ProfileEventType event_type;

        /// When the event started (real-world, not simulation time).
        Optional<Timestamp> start_time;

        /// When the event ended (real-world, not simulation time).
        Optional<Timestamp> stop_time;

        /// Port used for sending or receiving, if applicable.
        Optional<ymmsl::Port> port;

        /// Length of that port, if a vector.
        Optional<int> port_length;

        /// Slot that was sent or received on, if applicable.
        Optional<int> slot;

        /// Size of the message involved, if applicable.
        Optional<std::size_t> message_size;

        /// Timestamp sent with the message, if applicable.
        Optional<double> message_timestamp;
};

} }

