#pragma once

#include <ostream>

#include <libmuscle/namespace.hpp>


namespace libmuscle { namespace _MUSCLE_IMPL_NS {

/** A timestamp, as the number of seconds since the UNIX epoch.
 */
class Timestamp {
    public:
        /** Number of seconds since the UNIX epoch.
         */
        double seconds;

        /** Create a Timestamp representing the current time.
         */
        Timestamp();

        /** Create a Timestamp.
         *
         * @param seconds The number of seconds since the UNIX epoch.
         */
        Timestamp(double seconds);
};

std::ostream & operator<<(std::ostream & os, Timestamp ts);

} }

