#pragma once

#include <libmuscle/data.hpp>
#include <libmuscle/namespace.hpp>
#include <libmuscle/util.hpp>
#include <ymmsl/ymmsl.hpp>

#include <vector>


namespace libmuscle { namespace _MUSCLE_IMPL_NS {

/** A MUSCLE Peer Protocol message.
 *
 * Messages carry the identity of their sender and receiver, so that they can
 * be routed by a MUSCLE Transport Overlay when we get to multi-site running in
 * the future.
 */
class MPPMessage {
    public:
        /** Create an MPP Message.
         *
         * Senders and receivers are referred to by a Reference, which
         * contains Instance[InstanceNumber].Port[Slot].
         *
         * The port_length field is only used if two vector ports are connected
         * together. In that case the number of slots is not determined by the
         * number of instances, and must be set by the sender and then
         * communicated to the receiver in this additional field in all
         * messages sent on the port.
         *
         * This is the on-the-wire object, the user-facing one is in
         * libmuscle/communicator.hpp.
         */
        MPPMessage(
                ::ymmsl::Reference const & sender, ::ymmsl::Reference const & receiver,
                Optional<int> port_length,
                double timestamp, Optional<double> next_timestamp,
                DataConstRef const & settings_overlay, int message_number,
                double saved_until, DataConstRef const & data);

        /** Create an MCP Message from an encoded buffer.
         *
         * @param data A vector with encoded data.
         */
        static MPPMessage from_bytes(DataConstRef const & data);

        /** Encode the message and return as a byte buffer.
         */
        DataConstRef encoded_as_dcr() const;

        /** Create an MCP Message from an encoded buffer.
         *
         * @param data A vector with encoded data.
         */
        static MPPMessage from_bytes(std::vector<char> const & data);

        /** Encode the message and return as a byte buffer.
         */
        std::vector<char> encoded() const;

        ::ymmsl::Reference sender;
        ::ymmsl::Reference receiver;
        Optional<int> port_length;
        double timestamp;
        Optional<double> next_timestamp;
        DataConstRef settings_overlay;
        int message_number;
        double saved_until;
        DataConstRef data;

    private:
        static MPPMessage from_dict_(DataConstRef const & dict);
        DataConstRef as_dict_() const;
};

} }

