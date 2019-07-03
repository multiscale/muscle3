#include <stdexcept>

#include "logging.hpp"


namespace mmp = muscle_manager_protocol;

namespace libmuscle {

LogLevel log_level_from_grpc(mmp::LogLevel level) {
    LogLevel result;
    switch (level) {
        case mmp::LOG_LEVEL_DEBUG:
            result = LogLevel::DEBUG;
            break;
        case mmp::LOG_LEVEL_INFO:
            result = LogLevel::INFO;
            break;
        case mmp::LOG_LEVEL_WARNING:
            result = LogLevel::WARNING;
            break;
        case mmp::LOG_LEVEL_ERROR:
            result = LogLevel::ERROR;
            break;
        case mmp::LOG_LEVEL_CRITICAL:
            result = LogLevel::CRITICAL;
            break;
        default:
            throw std::runtime_error("Invalid log level");
    }
    return result;
}

mmp::LogLevel log_level_to_grpc(LogLevel level) {
    mmp::LogLevel result;
    switch (level) {
        case LogLevel::DEBUG:
            result = mmp::LOG_LEVEL_DEBUG;
            break;
        case LogLevel::INFO:
            result = mmp::LOG_LEVEL_INFO;
            break;
        case LogLevel::WARNING:
            result = mmp::LOG_LEVEL_WARNING;
            break;
        case LogLevel::ERROR:
            result = mmp::LOG_LEVEL_ERROR;
            break;
        case LogLevel::CRITICAL:
            result = mmp::LOG_LEVEL_CRITICAL;
            break;
    }
    return result;
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

mmp::LogMessage LogMessage::to_grpc() const {
    auto result = mmp::LogMessage();
    result.set_instance_id(instance_id);
    result.set_allocated_timestamp(timestamp.to_grpc().release());
    result.set_level(log_level_to_grpc(level));
    result.set_text(text);

    return result;
}

}

