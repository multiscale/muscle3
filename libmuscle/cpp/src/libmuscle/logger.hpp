#pragma once

#ifdef LIBMUSCLE_MOCK_LOGGER
#include LIBMUSCLE_MOCK_LOGGER
#else

#include <libmuscle/mmp_client.hpp>
#include <libmuscle/namespace.hpp>
#include <libmuscle/logging.hpp>

#include <fstream>
#include <ostream>
#include <string>


namespace libmuscle { namespace _MUSCLE_IMPL_NS {

/** A component that lets you log things to an MMPClient.
 */
class Logger {
    public:
        /** Create a Logger.
         *
         * @param manager The manager client to log to.
         */
        Logger(std::string const & instance_id, std::string const & log_file, MMPClient & manager);

        /** Destruct the logger.
         *
         * Closes the log file.
         */
        ~Logger();

        /** Set the minimum log level for a message to be sent to the manager.
         */
        void set_remote_level(LogLevel level);

        /** Set the minimum log level for a message to be logged to the local
         * log.
         */
        void set_local_level(LogLevel level);

        /** Send a log message at the given level.
         *
         * The arguments will be pushed into a std::ostream using operator<<,
         * and must be of a type that will support that. For example
         *
         * log(LogLevel::DEBUG, "Got a value ", 10);
         *
         * will result in a message with text "Got a value 10" to be logged.
         *
         * @param level The level to log at.
         * @param args The log message, see above.
         */
        template <typename... Args>
        void log(LogLevel level, Args... args);

        /** Send a log message at level critical.
         *
         * @param args The log message, see log().
         */
        template <typename... Args>
        void critical(Args... args);

        /** Send a log message at level critical.
         *
         * @param args The log message, see log().
         */
        template <typename... Args>
        void error(Args... args);

        /** Send a log message at level error.
         *
         * @param args The log message, see log().
         */
        template <typename... Args>
        void warning(Args... args);

        /** Send a log message at level warning.
         *
         * @param args The log message, see log().
         */
        template <typename... Args>
        void info(Args... args);

        /** Send a log message at level debug.
         *
         * @param args The log message, see log().
         */
        template <typename... Args>
        void debug(Args... args);

    private:
        std::string instance_id_;
        MMPClient & manager_;
        LogLevel remote_level_;
        std::ofstream local_log_file_;
        std::ostream * local_log_stream_;
        LogLevel local_level_;

        template <typename Arg, typename... Args>
        void append_args_(std::ostringstream & s, Arg arg, Args... args);

        void append_args_(std::ostringstream & s);
};

} }

#include <libmuscle/logger.tpp>

#endif

