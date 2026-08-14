#include "libmuscle/logger.hpp"
#include "libmuscle/util.hpp"

#include <sstream>


namespace libmuscle { namespace _MUSCLE_IMPL_NS {

Logger & Logger::instance() {
    static Logger instance;
    return instance;
}

void Logger::init(
        std::string const & instance_id, std::string const & log_file, MMPClient * manager)
{
    std::lock_guard<std::recursive_mutex> lock(mutex_);
    instance_id_ = instance_id;

    if (log_file.empty())
        local_log_stream_ = &std::cerr;
    else {
        local_log_file_.open(log_file, std::ios_base::app);
        local_log_stream_ = &local_log_file_;
    }

    manager_ = manager;

}

void Logger::close() {
    std::lock_guard<std::recursive_mutex> lock(mutex_);
    local_log_stream_ = nullptr;
    manager_ = nullptr;
}

Logger::~Logger() {
    if (local_log_file_.is_open())
        local_log_file_.close();
}

void Logger::set_remote_level(LogLevel level) {
    std::lock_guard<std::recursive_mutex> lock(mutex_);
    if (level == LogLevel::LOCAL) {
        log(LogLevel::WARNING, "LOCAL is not a valid remote log level, using DEBUG");
        level = LogLevel::DEBUG;
    }
    remote_level_ = level;
}

void Logger::set_local_level(LogLevel level) {
    std::lock_guard<std::recursive_mutex> lock(mutex_);
    local_level_ = level;
}

Logger::Logger()
    : manager_(nullptr)
    , remote_level_(LogLevel::WARNING)
    , local_log_stream_(nullptr)
    , local_level_(LogLevel::INFO)
    , num_dropped_(0)
{}

void Logger::append_args_(std::ostringstream &) {}

} }

