#include <echolib.hpp>

#include <cassert>
#include <stdexcept>

#include <iostream>
#include <ostream>


namespace echolib {


Echo::Echo(int argc, char const * const * argv) {}

void Echo::echo_nothing() const {}

int Echo::echo_int(int value) const {
    assert(value == 42);
    return value;
}

int64_t Echo::echo_int64_t(int64_t value) const {
    assert(value == 4242424242424242l);
    return value;
}

double Echo::echo_double(double value) const {
    assert(value == 1.0000000001);
    return value;
}

bool Echo::echo_bool(bool value) const {
    assert(value);
    return value;
}

Color Echo::echo_enum(Color value) const {
    assert(value == Color::GREEN);
    return value;
}

std::string Echo::echo_string(std::string const & value) const {
    assert(value == "Testing");
    return value;
}

std::vector<double> Echo::echo_double_vec(
        std::vector<double> const & value) const
{
    assert(value[0] == 1.414213562373095);
    assert(value[1] == 3.141592653589793);
    return value;
}

std::vector<std::vector<double>> Echo::echo_double_vec2(
        std::vector<std::vector<double>> const & value) const
{
    assert(value[0][0] == 1.0);
    assert(value[1][0] == 2.0);
    assert(value[2][0] == 3.0);
    assert(value[0][1] == 4.0);
    assert(value[1][1] == 5.0);
    assert(value[2][1] == 6.0);
    return value;
}

Echo Echo::echo_object(Echo const & value) const {
    assert(this == &value);
    return value;
}

std::vector<char> Echo::echo_bytes(std::vector<char> const & value) const {
    assert(value[0] == 'T');
    assert(value[1] == 'e');
    assert(value[2] == 's');
    assert(value[3] == 't');
    assert(value[4] == 'i');
    assert(value[5] == 'n');
    assert(value[6] == 'g');
    return value;
}

std::string Echo::echo_error(double value) const {
    throw std::runtime_error("Testing exceptions");
}


template int Echo::echo_template<int>(int const & value) const;
template double Echo::echo_template<double>(double const & value) const;
template std::string Echo::echo_template<std::string>(
        std::string const & value) const;

}

