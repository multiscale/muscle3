#pragma once

#include <libmuscle/profiling.hpp>
#include <libmuscle/mmp_client.hpp>
#include <libmuscle/namespace.hpp>

#include <string>


namespace libmuscle { namespace _MUSCLE_IMPL_NS {

class MockProfiler {
    public:
        MockProfiler();

        MockProfiler(MMPClient & manager);

        void shutdown();

        void set_level(std::string const & level);

        void record_event(ProfileEvent && event);
};

using Profiler = MockProfiler;

} }

