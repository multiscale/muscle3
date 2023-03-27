#include "mocks/mock_logger.hpp"


namespace libmuscle { namespace _MUSCLE_IMPL_NS {

MockLogger::MockLogger() {}

MockLogger::MockLogger(
        std::string const & instance_id,
        std::string const & log_file, MMPClient & manager) {}

} }

