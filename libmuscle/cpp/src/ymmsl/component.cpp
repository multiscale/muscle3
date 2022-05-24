#include <ymmsl/component.hpp>


namespace ymmsl { namespace impl {

bool allows_sending(Operator op) {
    return (op == Operator::NONE) ||
           (op == Operator::O_I) ||
           (op == Operator::O_F);
}

bool allows_receiving(Operator op) {
    return (op == Operator::NONE) ||
           (op == Operator::F_INIT) ||
           (op == Operator::S);
}

Port::Port(Identifier const & name, Operator oper)
    : name(name)
    , oper(oper)
{}

} }

