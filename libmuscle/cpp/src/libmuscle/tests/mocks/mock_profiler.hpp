#pragma once

#include <libmuscle/profiling.hpp>
#include <libmuscle/mmp_client.hpp>
#include <libmuscle/namespace.hpp>


namespace libmuscle { namespace _MUSCLE_IMPL_NS {

class MockProfiler {
    public:
        MockProfiler();

        MockProfiler(MMPClient & manager);

        void shutdown();

        void record_event(ProfileEvent && event);
};

using Profiler = MockProfiler;

} }

