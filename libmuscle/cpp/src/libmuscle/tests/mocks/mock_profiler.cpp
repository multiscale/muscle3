#include "mocks/mock_profiler.hpp"

#include <libmuscle/mpp_client.hpp>


namespace libmuscle { namespace _MUSCLE_IMPL_NS {

    MockProfiler::MockProfiler() {}

    MockProfiler::MockProfiler(MMPClient & manager) {}

    void MockProfiler::shutdown() {}

    void MockProfiler::record_event(ProfileEvent && event) {}

} }

