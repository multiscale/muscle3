#pragma once

#include <libmuscle/timestamp.hpp>

#include <string>


namespace libmuscle { namespace impl {

/** Log levels for MUSCLE 3.
 *
 * These match the Python log levels in name and value, which is what's used
 * in the MUSCLE Manager Protocol. So they must be kept the same or things
 * will break.
 */
enum class LogLevel {
    CRITICAL = 50,
    ERROR = 40,
    WARNING = 30,
    INFO = 20,
    DEBUG = 10
};

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
};

} }

