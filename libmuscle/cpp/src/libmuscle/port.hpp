#pragma once

#include <libmuscle/util.hpp>
#include <ymmsl/ymmsl.hpp>


namespace libmuscle { namespace impl {

/** Represents a gateway to the outside world.
 *
 * Ports can be used to send or receive messages. They have a name and an
 * operator, as well as a set of dimensions that determines the valid slot
 * indices for sending or receiving on this port.
 *
 * Ports keep track of the amount of messages sent or received on the port.
 * However, the actual incrementing and validation is done in
 * Communicator.
 */
class Port : public ::ymmsl::Port {
    public:
        /** Create a Port.
         *
         * @param name Name of this port.
         * @param oper Corresponding operator.
         * @param is_vector Whether this is a vector port.
         * @param is_connected Whether this port is connected to a peer.
         * @param our_ndims Number of dimensions of our instance set.
         * @param peer_dims Dimensions of the peer instance set of this port.
         */
        Port(
                std::string const & name, ::ymmsl::Operator oper,
                bool is_vector, bool is_connected,
                int our_ndims, std::vector<int> peer_dims,
                std::vector<int> num_messages=std::vector<int>(0));

        // Note: we only ever use this Port in libmuscle, and only use
        // ymmsl::Port in ymmsl. Port objects are always handled by value, so
        // there is no risk of slicing. If you want to do OO, add a virtual
        // destructor to ymmsl::Port as well as here.

        /** Returns whether the port is connected to a peer.
         *
         * @return True iff there is a peer.
         */
        bool is_connected() const;

        /** Returns whether this port is open.
         *
         * @return False iff the port has been closed.
         */
        bool is_open() const;

        /** Returns whether this slot port is open.
         *
         * Use only on vector ports.
         *
         * @param slot A slot to check.
         * @return False iff the slot has been closed.
         */
        bool is_open(int slot) const;

        /** Returns whether this slot/port is open.
         *
         * If slot is set, then this port must be a vector port, else it must
         * be a scalar port.
         *
         * @param slot An optional slot to check.
         * @return False iff the port/slot has been closed.
         */
        bool is_open(Optional<int> slot) const;

        /** Returns whether this is a vector port.
         */
        bool is_vector() const;

        /** Returns whether this port is resizable.
         *
         * Only valid for vector ports.
         */
        bool is_resizable() const;

        /** Returns the length of this port.
         *
         * Only valid for vector ports.
         */
        int get_length() const;

        /** Sets the length of a resizable vector port.
         *
         * Only call this if is_resizable() returns True.
         *
         * @param length The new length.
         *
         * @throws std::runtime_error if the port is not resizable.
         */
        void set_length(int length);

        /** Marks this port as closed.
         *
         * After calling this, is_open() will return false.
         */
        void set_closed();

        /** Marks this slot as closed.
         *
         * After calling this, is_open(slot) will return false.
         *
         * @param slot The slot to mark as closed.
         */
        void set_closed(int slot);

        /** Increment amount of messages sent or received.
         */
        void increment_num_messages();

        /** Increment amount of messages sent or received.
         *
         * Only valid for vector ports.
         *
         * @param slot The slot that is sent/received on
         */
        void increment_num_messages(int slot);

        /** Get the amount of messages sent or received
         */
        int get_num_messages() const;

        /** Get the amount of messages sent or received
         *
         * Only valid for vector ports.
         *
         * @param slot The slot that is sent/received on
         */
        int get_num_messages(int slot) const;

        /** True when this port has resumed.
         *
         * After resumption, each port/slot may discard exactly one message.
         * is_resuming keeps track of this state.
         */
        bool is_resuming() const;

        /** True when this port has resumed.
         *
         * After resumption, each port/slot may discard exactly one message.
         * is_resuming keeps track of this state.
         *
         * Only valid for vector ports.
         *
         * @param slot The slot that is sent/received on
         */
        bool is_resuming(int slot) const;

        /** Mark that this port has resumed and may no longer discard messages.
         */
        void set_resumed();

        /** Mark that this port has resumed and may no longer discard messages.
         *
         * Only valid for vector ports.
         *
         * @param slot The slot that is sent/received on
         */
        void set_resumed(int slot);

    private:
        bool is_connected_;
        int length_;
        bool is_resizable_;
        std::vector<bool> is_open_;
        std::vector<int> num_messages_;
        std::vector<bool> is_resuming_;
};

} }

