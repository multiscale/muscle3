#include "libmuscle/logger.hpp"
#include "libmuscle/util.hpp"

#include <sstream>


namespace libmuscle { namespace _MUSCLE_IMPL_NS {

Logger::Logger(std::string const & instance_id, std::string const & log_file, MMPClient & manager)
    : instance_id_(instance_id)
    , manager_(manager)
    , remote_level_(LogLevel::WARNING)
    , local_level_(LogLevel::INFO)
{
    if (log_file.empty())
        local_log_stream_ = &std::cerr;
    else {
        local_log_file_.open(log_file, std::ios_base::app);
        local_log_stream_ = &local_log_file_;
    }
}

Logger::~Logger() {
    if (local_log_file_.is_open())
        local_log_file_.close();
}

void Logger::set_remote_level(LogLevel level) {
    if (level == LogLevel::LOCAL) {
        log(LogLevel::WARNING, "LOCAL is not a valid remote log level, using DEBUG");
        level = LogLevel::DEBUG;
    }
    remote_level_ = level;
}

void Logger::set_local_level(LogLevel level) {
    local_level_ = level;
}

void Logger::append_args_(std::ostringstream &) {}

} }

