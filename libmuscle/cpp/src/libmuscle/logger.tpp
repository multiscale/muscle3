#include <iostream>
#include <ostream>
#include <sstream>

namespace libmuscle { namespace impl {

template <typename... Args>
void Logger::log(LogLevel level, Args... args) {
    if ((level >= local_level_) || (level >= remote_level_)) {
        auto ts = Timestamp();
        std::ostringstream oss;
        append_args_(oss, args...);

        if (level >= local_level_) {
            (*local_log_stream_) << instance_id_ << " " << ts << " " << level;
            (*local_log_stream_) << ": " << oss.str() << std::endl;
        }

        if (level >= remote_level_) {
            LogMessage msg(instance_id_, Timestamp(), level, oss.str());
            manager_.submit_log_message(msg);
        }
    }
}

template <typename... Args>
void Logger::critical(Args... args) {
    log(LogLevel::CRITICAL, args...);
}

template <typename... Args>
void Logger::error(Args... args) {
    log(LogLevel::ERROR, args...);
}

template <typename... Args>
void Logger::warning(Args... args) {
    log(LogLevel::WARNING, args...);
}

template <typename... Args>
void Logger::info(Args... args) {
    log(LogLevel::INFO, args...);
}

template <typename... Args>
void Logger::debug(Args... args) {
    log(LogLevel::DEBUG, args...);
}

template <typename Arg, typename... Args>
void Logger::append_args_(std::ostringstream & s, Arg arg, Args... args) {
    s << arg;
    append_args_(s, args...);
}

} }

