#include <stdexcept>

#include "logging.hpp"


namespace libmuscle { namespace impl {

LogMessage::LogMessage(
        std::string const & instance_id,
        Timestamp timestamp,
        LogLevel level,
        std::string const & text
)
    : instance_id(instance_id)
    , timestamp(timestamp)
    , level(level)
    , text(text)
{}

} }

