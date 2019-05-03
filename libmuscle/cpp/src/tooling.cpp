#include "tooling.hpp"

#include "muscle_manager_protocol/muscle_manager_protocol.pb.h"


Tooling::Tooling()
    : test_variable_(42)
{}

int Tooling::get_test_variable() const {
    return test_variable_;
}

