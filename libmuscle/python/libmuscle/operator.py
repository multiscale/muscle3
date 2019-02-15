from typing import Dict

from ymmsl import Operator
import muscle_manager_protocol.muscle_manager_protocol_pb2 as mmp


def operator_from_grpc(
        operator: mmp.Operator
        ) -> Operator:
    """Creates an operator from a gRPC-generated Operator.

    Args:
        operator: An operator, received from gRPC.

    Returns:
        The same operator, as an Operator.
    """
    operator_map = {
            mmp.OPERATOR_NONE: Operator.NONE,
            mmp.OPERATOR_F_INIT: Operator.F_INIT,
            mmp.OPERATOR_O_I: Operator.O_I,
            mmp.OPERATOR_S: Operator.S,
            mmp.OPERATOR_B: Operator.B,
            mmp.OPERATOR_O_F: Operator.O_F
            }   # type: Dict[int, Operator]
    return operator_map[operator]


def operator_to_grpc(operator: Operator) -> mmp.Operator:
    """Converts the operator to the gRPC generated type.

    Returns:
        The operator, as the gRPC type.
    """
    operator_map = {
            Operator.NONE: mmp.OPERATOR_NONE,
            Operator.F_INIT: mmp.OPERATOR_F_INIT,
            Operator.O_I: mmp.OPERATOR_O_I,
            Operator.S: mmp.OPERATOR_S,
            Operator.B: mmp.OPERATOR_B,
            Operator.O_F: mmp.OPERATOR_O_F
            }   # type: Dict[Operator, mmp.Operator]
    return operator_map[operator]
