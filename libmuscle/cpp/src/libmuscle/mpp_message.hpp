#pragma once

#include <libmuscle/data.hpp>
#include <libmuscle/util.hpp>
#include <ymmsl/ymmsl.hpp>


namespace libmuscle { namespace impl {

/** A MUSCLE Peer Protocol message.
 *
 * Messages carry the identity of their sender and receiver, so that they can
 * be routed by a MUSCLE Transport Overlay when we get to multi-site running in
 * the future.
 */
struct MPPMessage {
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
            ::libmuscle::impl::Optional<int> port_length,
            double timestamp, ::libmuscle::impl::Optional<double> next_timestamp,
            DataConstRef const & settings_overlay, int message_number,
            DataConstRef const & data);

    /** Create an MCP Message from an encoded buffer.
     *
     * @param data A DataConstRef containing a byte array with encoded data.
     */
    static MPPMessage from_bytes(DataConstRef const & data);

    /** Encode the message and return as a byte buffer.
     *
     * Returns a byte_array in a DataConstRef.
     */
    DataConstRef encoded() const;

    ::ymmsl::Reference sender;
    ::ymmsl::Reference receiver;
    ::libmuscle::impl::Optional<int> port_length;
    double timestamp;
    ::libmuscle::impl::Optional<double> next_timestamp;
    DataConstRef settings_overlay;
    int message_number;
    DataConstRef data;
};

} }

