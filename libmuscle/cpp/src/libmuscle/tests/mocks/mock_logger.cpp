#include "mocks/mock_logger.hpp"


namespace libmuscle { namespace impl {

MockLogger::MockLogger() {}

MockLogger::MockLogger(
        std::string const & instance_id,
        std::string const & log_file, MMPClient & manager) {}

} }

