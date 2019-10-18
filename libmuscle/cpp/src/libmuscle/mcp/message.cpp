#include <libmuscle/mcp/message.hpp>
#include <ymmsl/identity.hpp>

#include <msgpack.hpp>

#include <utility>


namespace libmuscle { namespace impl { namespace mcp {

Message::Message(
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

Message Message::from_bytes(DataConstRef const & data) {
    // decode
    auto zone = std::make_shared<msgpack::zone>();
    DataConstRef dict = unpack_data(zone, data.as_byte_array(), data.size());

    // create message
    libmuscle::impl::Optional<int> port_length;
    if (dict["port_length"].is_a<int>())
        port_length = dict["port_length"].as<int>();

    libmuscle::impl::Optional<double> next_timestamp;
    if (dict["next_timestamp"].is_a<double>())
        next_timestamp = dict["next_timestamp"].as<double>();

    return Message(
            dict["sender"].as<std::string>(),
            dict["receiver"].as<std::string>(),
            port_length,
            dict["timestamp"].as<double>(),
            next_timestamp,
            dict["settings_overlay"],
            dict["data"]);
}

} } }

