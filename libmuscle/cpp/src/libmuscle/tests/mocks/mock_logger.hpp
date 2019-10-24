#pragma once

#include <libmuscle/logging.hpp>
#include <libmuscle/mmp_client.hpp>


namespace libmuscle { namespace impl {

class MockLogger {
    public:
        MockLogger();
        MockLogger(std::string const & instance_id, MMPClient & manager);

        void set_remote_level(LogLevel level) {}

        template <typename... Args>
        void log(LogLevel level, Args... args) {}

        template <typename... Args>
        void critical(Args... args) {}

        template <typename... Args>
        void error(Args... args) {}

        template <typename... Args>
        void warning(Args... args) {}

        template <typename... Args>
        void info(Args... args) {}

        template <typename... Args>
        void debug(Args... args) {}
};

using Logger = MockLogger;

} }

