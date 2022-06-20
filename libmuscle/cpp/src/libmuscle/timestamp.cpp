#include <libmuscle/timestamp.hpp>

#include <chrono>
#include <cmath>
#include <time.h>


using wallclock = std::chrono::high_resolution_clock;


namespace libmuscle { namespace impl {

Timestamp::Timestamp(double seconds)
    : seconds(seconds)
{
    tzset();
}

Timestamp Timestamp::now() {
    auto since_epoch = wallclock::now().time_since_epoch();
    double cycles = since_epoch.count();
    double seconds = cycles * wallclock::period::num / wallclock::period::den;
    return Timestamp(seconds);
}

std::ostream & operator<<(std::ostream & os, Timestamp ts) {
    time_t time = static_cast<time_t>(ts.seconds);
    struct tm time_tm;
    localtime_r(&time, &time_tm);
    char buf[30];
    strftime(buf, 30u, "%Y-%m-%d %H:%M:%S", &time_tm);
    os << buf << "." << round((ts.seconds - floor(ts.seconds)) * 1000.0);
    return os;
}

} }

