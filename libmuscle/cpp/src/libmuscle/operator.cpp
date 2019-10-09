#include "operator.hpp"


namespace mmp = muscle_manager_protocol;


namespace libmuscle { namespace impl {

ymmsl::Operator operator_from_grpc(mmp::Operator op) {
    ymmsl::Operator result;

    switch (op) {
        case mmp::OPERATOR_NONE:
            result = ymmsl::Operator::NONE;
            break;
        case mmp::OPERATOR_F_INIT:
            result = ymmsl::Operator::F_INIT;
            break;
        case mmp::OPERATOR_O_I:
            result = ymmsl::Operator::O_I;
            break;
        case mmp::OPERATOR_S:
            result = ymmsl::Operator::S;
            break;
        case mmp::OPERATOR_B:
            result = ymmsl::Operator::B;
            break;
        case mmp::OPERATOR_O_F:
            result = ymmsl::Operator::O_F;
            break;
        case mmp::OPERATOR_MAP:
            result = ymmsl::Operator::NONE;
            break;
        default:
            // https://www.xkcd.com/2200
            throw std::runtime_error(
                    "ERROR: We've reached an unreachable state."
                    " Anything is possible."
                    " The limits were in our heads all along."
                    " Follow your dreams.");
    }
    return result;
}

muscle_manager_protocol::Operator operator_to_grpc(ymmsl::Operator op) {
    mmp::Operator result;

    switch (op) {
        case ymmsl::Operator::NONE:
            result = mmp::OPERATOR_NONE;
            break;
        case ymmsl::Operator::F_INIT:
            result = mmp::OPERATOR_F_INIT;
            break;
        case ymmsl::Operator::O_I:
            result = mmp::OPERATOR_O_I;
            break;
        case ymmsl::Operator::S:
            result = mmp::OPERATOR_S;
            break;
        case ymmsl::Operator::B:
            result = mmp::OPERATOR_B;
            break;
        case ymmsl::Operator::O_F:
            result = mmp::OPERATOR_O_F;
            break;
    }
    return result;
}

} }

