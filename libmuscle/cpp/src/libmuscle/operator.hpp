#pragma once

#include <muscle_manager_protocol/muscle_manager_protocol.pb.h>
#include <ymmsl/ymmsl.hpp>


namespace libmuscle {

/** Convert an operator from the gRPC to the ymmsl type.
 *
 * @param op The operator to convert.
 */
ymmsl::Operator operator_from_grpc(muscle_manager_protocol::Operator op);

/** Convert an operator from ymmsl to gRPC.
 *
 * @param op The operator to convert.
 */
muscle_manager_protocol::Operator operator_to_grpc(ymmsl::Operator op);

}

