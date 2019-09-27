#pragma once

#include <libmuscle/data.hpp>
#include <libmuscle/util.hpp>

#include <ymmsl/settings.hpp>


namespace libmuscle {

/** A message to be sent or received.
 *
 * This class describes a message to be sent or that has been received.
 *
 * @attribute timestamp Simulation time for which this data is valid.
 * @attribute next_timestamp Simulation time for the next message to be
 *      transmitted through this port.
 * @attribute data An object to send or that was received.
 * @attribute settings Overlay settings to send or that were received.
 */
// Note: This is for communication with the user, it's not what actually goes
// out on the wire. See libmuscle::mcp::Message for that.
class Message {
    public:
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

        /** Returns whether the message carries settings.
         */
        bool has_settings() const;

        /** Returns the settings carried by the message.
         *
         * Only call if has_settings() returns true.
         */
        ::ymmsl::Settings const & settings() const;

    private:
        double timestamp_;
        Optional<double> next_timestamp_;
        DataConstRef data_;
        Optional<ymmsl::Settings> settings_;
};

}

