#pragma once

#include <libmuscle/logging.hpp>
#include <libmuscle/mmp_client.hpp>
#include <libmuscle/namespace.hpp>


namespace libmuscle { namespace _MUSCLE_IMPL_NS {

class MockLogger {
    public:
        MockLogger();
        MockLogger(
                std::string const & instance_id,
                std::string const & log_file, MMPClient & manager);

        void set_remote_level(LogLevel level) {}

        void set_local_level(LogLevel level) {}

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

