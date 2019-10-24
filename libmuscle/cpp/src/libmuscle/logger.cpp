#include <libmuscle/logger.hpp>


namespace libmuscle { namespace impl {

Logger::Logger(std::string const & instance_id, MMPClient & manager)
    : instance_id_(instance_id)
    , manager_(manager)
    , remote_level_(LogLevel::WARNING)
{}

void Logger::set_remote_level(LogLevel level) {
    remote_level_ = level;
}

void Logger::append_args_(std::ostringstream & s) {}

} }

