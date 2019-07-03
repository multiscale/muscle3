#pragma once

#include "libmuscle/timestamp.hpp"
#include "muscle_manager_protocol/muscle_manager_protocol.pb.h"


namespace libmuscle {

/** Log levels for MUSCLE 3.
 *
 * These match the levels in the MUSCLE Manager Protocol, and should be kept
 * identical to those. They also match the Python logging log levels, although
 * not numerically.
 */
enum class LogLevel {
    CRITICAL = 5,
    ERROR = 4,
    WARNING = 3,
    INFO = 1,
    DEBUG = 0
};

/** Creates a log level from a gRPC-generated LogLevel.
 *
 * @param level A log level, received from gRPC.
 * @return The same log level, as a libmuscle.LogLevel.
 */
LogLevel log_level_from_grpc(muscle_manager_protocol::LogLevel level);

/** Converts the log level to the gRPC-generated type.
 *
 * @param level A log level.
 * @return The same log level, as mmp.LogLevel.
 */
muscle_manager_protocol::LogLevel log_level_to_grpc(LogLevel level);


/** A log message as used by MUSCLE 3.
 */
class LogMessage {
    public:
        /// The identifier of the instance that generated this message.
        std::string instance_id;
        /// When the message was generated (real-world, not simulation).
        Timestamp timestamp;
        /// Log level of the message.
        LogLevel level;
        /// Content of the message.
        std::string text;

        /** Create a LogMessage.
         *
         * @param instance_id The identifier of the instance that generated this
         *                    message.
         * @param timestamp When the message was generated (real-world, not
         *                  simulation).
         * @param level Log level of the message.
         * @param text Content of the message
         */
        LogMessage(
                std::string const & instance_id, Timestamp timestamp,
                LogLevel level, std::string const & text);

        /** Convert the log message to the gRPC-generated type.
         *
         * @param message A log message.
         * @return The same log message, as the gRPC type.
         */
        muscle_manager_protocol::LogMessage to_grpc() const;
};

}

