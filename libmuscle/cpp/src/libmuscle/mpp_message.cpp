#include <libmuscle/mpp_message.hpp>
#include <libmuscle/mcp/data_pack.hpp>
#include <ymmsl/identity.hpp>

#include <msgpack.hpp>

#include <cstring>
#include <utility>


namespace libmuscle { namespace impl {

MPPMessage::MPPMessage(
            ::ymmsl::Reference const & sender,
            ::ymmsl::Reference const & receiver,
            ::libmuscle::impl::Optional<int> port_length,
            double timestamp, ::libmuscle::impl::Optional<double> next_timestamp,
            DataConstRef const & settings_overlay,
            DataConstRef const & data
            )
        : sender(sender)
        , receiver(receiver)
        , port_length(port_length)
        , timestamp(timestamp)
        , next_timestamp(next_timestamp)
        , settings_overlay(settings_overlay)
        , data(data)
    {}

MPPMessage MPPMessage::from_bytes(DataConstRef const & data) {
    // decode
    auto zone = std::make_shared<msgpack::zone>();
    DataConstRef dict = mcp::unpack_data(zone, data.as_byte_array(), data.size());

    // create message
    libmuscle::impl::Optional<int> port_length;
    if (dict["port_length"].is_a<int>())
        port_length = dict["port_length"].as<int>();

    libmuscle::impl::Optional<double> next_timestamp;
    if (dict["next_timestamp"].is_a<double>())
        next_timestamp = dict["next_timestamp"].as<double>();

    return MPPMessage(
            dict["sender"].as<std::string>(),
            dict["receiver"].as<std::string>(),
            port_length,
            dict["timestamp"].as<double>(),
            next_timestamp,
            dict["settings_overlay"],
            dict["data"]);
}

DataConstRef MPPMessage::encoded() const {
    Data port_length_data;
    if (port_length.is_set())
        port_length_data = port_length.get();

    Data next_timestamp_data;
    if (next_timestamp.is_set())
        next_timestamp_data = next_timestamp.get();

    Data msg_dict = Data::dict(
            "sender", std::string(sender),
            "receiver", std::string(receiver),
            "port_length", port_length_data,
            "timestamp", timestamp,
            "next_timestamp", next_timestamp_data,
            "settings_overlay", settings_overlay,
            "data", data
            );

    msgpack::sbuffer sbuf;
    msgpack::pack(sbuf, msg_dict);

    auto bytes = Data::byte_array(sbuf.size());
    memcpy(bytes.as_byte_array(), sbuf.data(), sbuf.size());

    return std::move(bytes);
}

} }

