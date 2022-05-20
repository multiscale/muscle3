#include <chrono>

#include <libmuscle/timestamp.hpp>

using wallclock = std::chrono::high_resolution_clock;


namespace libmuscle { namespace impl {

Timestamp::Timestamp(double seconds)
    : seconds(seconds)
{}

Timestamp Timestamp::now() {
    auto since_epoch = wallclock::now().time_since_epoch();
    double cycles = since_epoch.count();
    double seconds = cycles * wallclock::period::num / wallclock::period::den;
    return Timestamp(seconds);
}

} }

