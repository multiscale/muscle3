#pragma once

#include <libmuscle/data.hpp>


namespace libmuscle {

/** Represents a ClosePort message.
 *
 * We need to be able to send a ClosePort message just like we send user data
 * and settings. Adding support for it to the Data class would expose it to
 * the user, while it's an internal sentinel object. We could also go full-OO
 * and create interfaces for external, internal and read-only use of the Data
 * class, add some factories, teach users about shared pointers, and so on,
 * but I'm not sure it would make anyone's life easier either. So we'll go with
 * this, it's a bit ugly, but it works.
 */
class ClosePort : public Data {
    public:
        /** Create a ClosePort object.
         *
         * The ClosePort object itself is the message, so it has no attributes
         * and doesn't contain any information other than its MessagePack
         * extension type id.
         */
        ClosePort();
};

}

