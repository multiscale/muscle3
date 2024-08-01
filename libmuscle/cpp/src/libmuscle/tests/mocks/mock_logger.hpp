#pragma once

#include <libmuscle/logging.hpp>
#include <libmuscle/mmp_client.hpp>
#include <libmuscle/namespace.hpp>

#include <libmuscle/tests/mocks/mock_support.hpp>

#include <sstream>


template <typename... Args>
void concat_to_stringstream(std::ostringstream & os, Args... args);

template <>
void concat_to_stringstream(std::ostringstream & os) {}

template <typename T, typename... Args>
void concat_to_stringstream(std::ostringstream & os, T t, Args... args) {
    os << t;
    concat_to_stringstream(os, args...);
}


namespace libmuscle { namespace _MUSCLE_IMPL_NS {

class MockLogger : public MockClass<MockLogger> {
    public:
        MockLogger(ReturnValue) {
            NAME_MOCK_MEM_FUN(MockLogger, constructor);
            NAME_MOCK_MEM_FUN(MockLogger, set_remote_level);
            NAME_MOCK_MEM_FUN(MockLogger, set_local_level);
            NAME_MOCK_MEM_FUN(MockLogger, caplog);
        }

        MockLogger() {
            init_from_return_value();
        }

        MockLogger(
                std::string const & instance_id, std::string const & log_file,
                MMPClient & manager)
        {
            init_from_return_value();
            constructor(instance_id, log_file, manager);
        }

        MockFun<
            Void, Val<std::string const &>, Val<std::string const &>,
            Obj<MMPClient &>
        > constructor;

        MockFun<Void, Val<LogLevel>> set_remote_level;
        MockFun<Void, Val<LogLevel>> set_local_level;

        MockFun<Void, Val<LogLevel>, Val<std::string const &>> caplog;

        template <typename... Args>
        void log(LogLevel && level, Args... args) {
            std::ostringstream s;
            concat_to_stringstream(s, args...);
            caplog(std::forward<LogLevel>(level), s.str());
        }

        template <typename... Args>
        void critical(Args... args) {
            std::ostringstream s;
            concat_to_stringstream(s, args...);
            caplog(LogLevel::CRITICAL, s.str());
        }

        template <typename... Args>
        void error(Args... args) {
            std::ostringstream s;
            concat_to_stringstream(s, args...);
            caplog(LogLevel::ERROR, s.str());
        }

        template <typename... Args>
        void warning(Args... args) {
            std::ostringstream s;
            concat_to_stringstream(s, args...);
            caplog(LogLevel::WARNING, s.str());
        }

        template <typename... Args>
        void info(Args... args) {
            std::ostringstream s;
            concat_to_stringstream(s, args...);
            caplog(LogLevel::INFO, s.str());
        }

        template <typename... Args>
        void debug(Args... args) {
            std::ostringstream s;
            concat_to_stringstream(s, args...);
            caplog(LogLevel::DEBUG, s.str());
        }
};

using Logger = MockLogger;

} }

