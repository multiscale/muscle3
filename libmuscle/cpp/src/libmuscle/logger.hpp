#pragma once

#ifdef LIBMUSCLE_MOCK_LOGGER
#include LIBMUSCLE_MOCK_LOGGER
#else

#include <libmuscle/mmp_client.hpp>
#include <libmuscle/namespace.hpp>
#include <libmuscle/logging.hpp>

#include <fstream>
#include <mutex>
#include <ostream>
#include <string>


namespace libmuscle { namespace _MUSCLE_IMPL_NS {

/** A component that lets you log things to an MMPClient.
 *
 * Singletons should be used sparingly, and I'm not super-happy about this because one
 * of my core design principles for libmuscle C++ was to attach everything to the
 * Instance instance the user creates, but passing the Logger instance around the whole
 * aggregation of classes is getting messy too. And after all the Python version uses
 * the Python logging subsystem which works in the same way.
 *
 * In the future, we could use the AOP system to mark entry and exit of the Instance
 * class public API member functions, and hook into that to tell the Logger to set
 * output streams for that particular Instance. If we make them thread-local, then that
 * will enable multiple Instance instances again.
 */
class Logger {
    public:
        /** Return the instance.
         */
        static Logger & instance();

        /** Destruct the logger.
         *
         * Closes the log file.
         */
        ~Logger();

        /** Initialise the logger.
         *
         * After this has been called, the logger can actually log things.
         */
        void init(std::string const & instance_id, std::string const & log_file, MMPClient * manager);

        /** Close the logger.
         *
         * After this has been called, no more log messages will be logged.
         */
        void close();

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
        /** Create a Logger.
         *
         * @param manager The manager client to log to.
         */
        Logger();

        std::mutex mutex_;
        std::string instance_id_;
        MMPClient * manager_;
        LogLevel remote_level_;
        std::ofstream local_log_file_;
        std::ostream * local_log_stream_;
        LogLevel local_level_;

        template <typename Arg, typename... Args>
        void append_args_(std::ostringstream & s, Arg arg, Args... args);

        void append_args_(std::ostringstream & s);
};


/** Send a log message at the given level.
 *
 * The arguments will be pushed into a std::ostream using operator<<, and must be of a
 * type that will support that. For example
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
void log_critical(Args... args);

/** Send a log message at level critical.
 *
 * @param args The log message, see log().
 */
template <typename... Args>
void log_error(Args... args);

/** Send a log message at level error.
 *
 * @param args The log message, see log().
 */
template <typename... Args>
void log_warning(Args... args);

/** Send a log message at level warning.
 *
 * @param args The log message, see log().
 */
template <typename... Args>
void log_info(Args... args);

/** Send a log message at level debug.
 *
 * @param args The log message, see log().
 */
template <typename... Args>
void log_debug(Args... args);


} }

#include <libmuscle/logger.tpp>



#endif

