#include "compute_element.hpp"


namespace ymmsl {

bool allows_sending(Operator op) {
    return (op == Operator::NONE) ||
           (op == Operator::O_I) ||
           (op == Operator::O_F);
}

bool allows_receiving(Operator op) {
    return (op == Operator::NONE) ||
           (op == Operator::F_INIT) ||
           (op == Operator::S) ||
           (op == Operator::B);
}

}

