#pragma once

#include <ostream>


namespace libmuscle { namespace impl {

/** A timestamp, as the number of seconds since the UNIX epoch.
 */
class Timestamp {
    public:
        /** Number of seconds since the UNIX epoch.
         */
        double seconds;

        /** Create a Timestamp.
         *
         * @param seconds The number of seconds since the UNIX epoch.
         */
        Timestamp(double seconds);

        /** Create a Timestamp representing the current time.
         */
        static Timestamp now();
};

std::ostream & operator<<(std::ostream & os, Timestamp ts);

} }

