#include <ymmsl/component.hpp>

#include <stdexcept>

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

std::string operator_name(Operator op) {
    switch (op)
    {
    case Operator::NONE:
        return "NONE";
    case Operator::F_INIT:
        return "F_INIT";
    case Operator::O_I:
        return "O_I";
    case Operator::S:
        return "S";
    case Operator::O_F:
        return "O_F";
    }
    throw std::logic_error("Unreachable code reached");
}

Operator operator_for_name(std::string const & name) {
    if (name == "NONE") {
        return Operator::NONE;
    } else if (name == "F_INIT") {
        return Operator::F_INIT;
    } else if (name == "O_I") {
        return Operator::O_I;
    } else if (name == "S") {
        return Operator::S;
    } else if (name == "O_F") {
        return Operator::O_F;
    }
    throw std::invalid_argument("Unknown operator name: " + name);
}

Port::Port(Identifier const & name, Operator oper)
    : name(name)
    , oper(oper)
{}

} }

