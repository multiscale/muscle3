#include "tooling.hpp"

Tooling::Tooling()
    : test_variable_(42)
{}

int Tooling::get_test_variable() const {
    return test_variable_;
}

