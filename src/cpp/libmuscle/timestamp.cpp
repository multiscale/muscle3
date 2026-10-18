#include <libmuscle/timestamp.hpp>

#include <chrono>
#include <cmath>
#include <time.h>


using wallclock = std::chrono::high_resolution_clock;


namespace libmuscle { namespace _MUSCLE_IMPL_NS {

Timestamp::Timestamp() {
    auto since_epoch = wallclock::now().time_since_epoch();
    seconds = std::chrono::duration<double>(since_epoch).count();
}

Timestamp::Timestamp(double seconds)
    : seconds(seconds)
{}

std::ostream & operator<<(std::ostream & os, Timestamp ts) {
    // tzset() needs to be called before localtime_r according to POSIX
    tzset();
    time_t time = static_cast<time_t>(ts.seconds);
    struct tm time_tm;
    localtime_r(&time, &time_tm);
    char buf[30];
    strftime(buf, 30u, "%Y-%m-%d %H:%M:%S", &time_tm);
    os << buf << "." << round((ts.seconds - floor(ts.seconds)) * 1000.0);
    return os;
}

} }

