#include "libmuscle/mcp/message.hpp"
#include "ymmsl/identity.hpp"

#include <utility>


namespace libmuscle { namespace mcp {

Message::Message(
            ::ymmsl::Reference const & sender,
            ::ymmsl::Reference const & receiver,
            ::libmuscle::Optional<int> port_length,
            double timestamp, ::libmuscle::Optional<double> next_timestamp,
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

} }

