#include <iostream>
#include <mutex>
#include <ostream>
#include <sstream>

namespace libmuscle { namespace _MUSCLE_IMPL_NS {

template <typename... Args>
void Logger::log(LogLevel level, Args... args) {
    std::lock_guard<std::recursive_mutex> lock(mutex_);
    if ((level >= local_level_) || (level >= remote_level_)) {
        auto ts = Timestamp();
        std::ostringstream oss;
        append_args_(oss, args...);

        if (local_log_stream_ && level >= local_level_) {
            (*local_log_stream_) << instance_id_ << " " << ts << " " << level;
            (*local_log_stream_) << ": " << oss.str() << std::endl;
        }

        if (manager_ && level >= remote_level_) {
            LogMessage message(instance_id_, Timestamp(), level, oss.str());
            try {
                if (num_dropped_ > 0) {
                    std::ostringstream oss2;
                    oss2 << num_dropped_ << " log messages were not sent to the";
                    oss2 << " manager log due to manager overload or network";
                    oss2 << " connectivity problems. Please see the instance log to";
                    oss2 << " read them.";

                    LogMessage dropped_msg = LogMessage(
                        instance_id_, Timestamp(), LogLevel::WARNING, oss2.str());

                    manager_->submit_log_message(dropped_msg);
                    num_dropped_ = 0;
                }
                manager_->submit_log_message(message);
            }
            catch (ConnectionLockedError const & e) {
                ++num_dropped_;
            }
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


template <typename... Args>
void log(LogLevel level, Args... args) {
    Logger::instance().log(level, args...);
}

template <typename... Args>
void log_critical(Args... args) {
    Logger::instance().log(LogLevel::CRITICAL, args...);
}

template <typename... Args>
void log_error(Args... args) {
    Logger::instance().log(LogLevel::ERROR, args...);
}

template <typename... Args>
void log_warning(Args... args) {
    Logger::instance().log(LogLevel::WARNING, args...);
}

template <typename... Args>
void log_info(Args... args) {
    Logger::instance().log(LogLevel::INFO, args...);
}

template <typename... Args>
void log_debug(Args... args) {
    Logger::instance().log(LogLevel::DEBUG, args...);
}

} }

