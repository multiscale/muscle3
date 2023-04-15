#pragma once

#include <libmuscle/namespace.hpp>
#include <libmuscle/timestamp.hpp>

#include <ostream>
#include <string>


namespace libmuscle { namespace _MUSCLE_IMPL_NS {

/** Log levels for MUSCLE3.
 *
 * These match the Python log levels in name and value, which is what's used
 * in the MUSCLE Manager Protocol. So they must be kept the same or things
 * will break.
 *
 * DISABLE may be used to disable remote or local logging. LOCAL can be used
 * by logging calls in the logging or communication subsystems to avoid a
 * situation in which the log statement being sent to the manager triggers
 * another logging call, leading to an infinite loop. These log messages will
 * never be logged remotely.
 */
enum class LogLevel {
    DISABLE = 100,
    CRITICAL = 50,
    ERROR = 40,
    WARNING = 30,
    INFO = 20,
    DEBUG = 10,
    LOCAL = 0
};

std::ostream & operator<<(std::ostream & o, LogLevel level);


/** A log message as used by MUSCLE3.
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

