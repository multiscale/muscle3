#include <libmuscle/logger.hpp>


namespace libmuscle { namespace impl {

Logger::Logger(std::string const & instance_id, MMPClient & manager)
    : instance_id_(instance_id)
    , manager_(manager)
{}

void Logger::append_args_(std::ostringstream & s) {}

} }

