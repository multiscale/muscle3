#include <libmuscle/mark.hpp>


namespace libmuscle { namespace _MUSCLE_IMPL_NS {

namespace mark {

void before_tcp_receive(int socket_fd) {
#ifdef INJECT_BEFORE_TCP_RECEIVE
    INJECT_BEFORE_TCP_RECEIVE
#endif
}

void before_tcp_send(int socket_fd) {
#ifdef INJECT_BEFORE_TCP_SEND
    INJECT_BEFORE_TCP_SEND
#endif
}


}

} }

