#pragma once

#include <libmuscle/data.hpp>
#include <libmuscle/namespace.hpp>
#include <libmuscle/test_support.hpp>
#include <libmuscle/util.hpp>

#include <ymmsl/ymmsl.hpp>


namespace libmuscle { namespace _MUSCLE_IMPL_NS {

/** A message to be sent or received.
 *
 * This class describes a message to be sent or that has been received.
 *
 */
// Note: This is for communication with the user, it's not what actually goes
// out on the wire. See libmuscle::mcp::Message for that.
class Message {
    public:
        /** Create an empty Message.
         *
         * @param timestamp Simulation time for which this data is valid.
         */
        explicit Message(double timestamp);

        /** Create a Message.
         *
         * @param timestamp Simulation time for which this data is valid.
         * @param data An object to send or that was received.
         */
        Message(double timestamp, DataConstRef const & data);

        /** Create a Message.
         *
         * @param timestamp Simulation time for which this data is valid.
         * @param next_timestamp Simulation time for the next message to be
         *      transmitted through this port.
         * @param data An object to send or that was received.
         */
        Message(double timestamp,
                double next_timestamp,
                DataConstRef const & data);

        /** Create a Message.
         *
         * @param timestamp Simulation time for which this data is valid.
         * @param data An object to send or that was received.
         * @param settings Overlay settings to send or that were received.
         */
        Message(double timestamp,
                DataConstRef const & data,
                ymmsl::Settings const & settings);

        /** Create a Message.
         *
         * @param timestamp Simulation time for which this data is valid.
         * @param next_timestamp Simulation time for the next message to be
         *      transmitted through this port.
         * @param data An object to send or that was received.
         * @param settings Overlay settings to send or that were received.
         */
        Message(double timestamp,
                double next_timestamp,
                DataConstRef const & data,
                ymmsl::Settings const & settings);

        /** Copy constructor.
         */
        Message(Message const & message);

        /** Move constructor.
         */
        Message(Message && message);

        /** Copy assignment.
         */
        Message & operator=(Message const & message);

        /** Move assignment.
         */
        Message & operator=(Message && message);

        /** Returns the timestamp of the message.
         */
        double timestamp() const;

        /** Sets the timestamp of the message.
         *
         * @param timestamp The new value.
         */
        void set_timestamp(double timestamp);

        /** Returns whether the message has a next timestamp.
         */
        bool has_next_timestamp() const;

        /** Returns the next timestamp of the message.
         *
         * Only call if has_next_timestamp() returns true.
         *
         * @throw std::logic_error if the next timestamp is not set.
         */
        double next_timestamp() const;

        /** Sets the next timestamp of the message.
         *
         * @param next_timestamp The new value.
         */
        void set_next_timestamp(double next_timestamp);

        /** Unsets the next timestamp of the message.
         */
        void unset_next_timestamp();

        /** Returns the data of the message.
         */
        DataConstRef const & data() const;

        /** Sets data to the given value.
         *
         * @param data The new data to set.
         */
        void set_data(DataConstRef const & data);

        /** Returns whether the message carries settings.
         */
        bool has_settings() const;

        /** Returns the settings carried by the message.
         *
         * Only call if has_settings() returns true.
         */
        ::ymmsl::Settings const & settings() const;

        /** Sets settings to the given value.
         *
         * This overwrites the entire Settings object, not a single value.
         *
         * @param settings The new settings to use.
         */
        void set_settings(::ymmsl::Settings const & settings);

        /** Unsets the settings of the message.
         */
        void unset_settings();

    PRIVATE:
        double timestamp_;
        Optional<double> next_timestamp_;
        DataConstRef data_;
        Optional<ymmsl::Settings> settings_;
};

} }

