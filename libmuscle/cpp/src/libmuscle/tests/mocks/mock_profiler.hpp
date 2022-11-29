#pragma once

#include <libmuscle/profiling.hpp>
#include <libmuscle/mmp_client.hpp>


namespace libmuscle { namespace impl {

class MockProfiler {
    public:
        MockProfiler();

        MockProfiler(MMPClient & manager);

        void shutdown();

        void record_event(ProfileEvent && event);
};

using Profiler = MockProfiler;

} }

