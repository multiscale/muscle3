#include "libmuscle/port_grpc.hpp"

#include "libmuscle/operator.hpp"
#include <muscle_manager_protocol/muscle_manager_protocol.pb.h>
#include <ymmsl/identity.hpp>


namespace mmp = ::muscle_manager_protocol;
using ymmsl::Identifier;


namespace libmuscle {

::ymmsl::Port port_from_grpc(mmp::Port const & port) {
    return ::ymmsl::Port(
            Identifier(port.name()),
            operator_from_grpc(port.operator_()));
}

mmp::Port port_to_grpc(::ymmsl::Port const & port) {
    auto result = mmp::Port();
    result.set_name(port.name);
    result.set_operator_(operator_to_grpc(port.oper));
    return result;
}

}

