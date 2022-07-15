#include <stdexcept>

#include "logging.hpp"


namespace libmuscle { namespace impl {

std::ostream & operator<<(std::ostream & os, LogLevel level) {
    switch (level) {
        case LogLevel::LOCAL:
            return os << "LOCAL";
        case LogLevel::DEBUG:
            return os << "DEBUG";
        case LogLevel::INFO:
            return os << "INFO";
        case LogLevel::WARNING:
            return os << "WARNING";
        case LogLevel::ERROR:
            return os << "ERROR";
        case LogLevel::CRITICAL:
            return os << "CRITICAL";
        case LogLevel::DISABLE:
            return os << "DISABLED";
        default:
            throw std::runtime_error("Unknown log level");
    }
}


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

