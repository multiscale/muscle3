#pragma once

#include <libmuscle/namespace.hpp>


namespace libmuscle { namespace _MUSCLE_IMPL_NS {

namespace mark {

/** Before receiving on the given TCP socket
 *
 * This is used to inject faults by the network connection fault tolerance integration
 * tests.
 */
void before_tcp_receive(int socketfd);

/** Before sending on the given TCP socket
 *
 * This is used to inject faults by the network connection fault tolerance integration
 * tests.
 */
void before_tcp_send(int socketfd);


}

} }

