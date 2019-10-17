#pragma once

#ifdef LIBMUSCLE_MOCK_LOGGER
#include LIBMUSCLE_MOCK_LOGGER
#else

#include <libmuscle/mmp_client.hpp>
#include <libmuscle/logging.hpp>


namespace libmuscle { namespace impl {

/** A component that lets you log things to an MMPClient.
 */
class Logger {
    public:
        /** Create a Logger.
         *
         * @param manager The manager client to log to.
         */
        Logger(std::string const & instance_id, MMPClient & manager);

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

        template <typename Arg, typename... Args>
        void append_args_(std::ostringstream & s, Arg arg, Args... args);

        void append_args_(std::ostringstream & s);
};

} }

#include <libmuscle/logger.tpp>

#endif

