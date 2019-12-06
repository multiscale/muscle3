#pragma once

#include <cstdint>
#include <stdexcept>
#include <string>
#include <vector>

namespace echolib {

enum class Color {
    RED = 1,
    GREEN = 2,
    BLUE = 3
};

class Echo {
    public:
        Echo(int argc, char const * const * argv);

        void echo_nothing() const;
        int echo_int(int value) const;
        int64_t echo_int64_t(int64_t value) const;
        double echo_double(double value) const;
        bool echo_bool(bool value) const;
        Color echo_enum(Color value) const;
        std::string echo_string(std::string const & value) const;
        std::vector<double> echo_double_vec(std::vector<double> const & value) const;
        std::vector<std::vector<double>> echo_double_vec2(
                std::vector<std::vector<double>> const & value) const;
        Echo echo_object(Echo const & value) const;
        std::vector<char> echo_bytes(std::vector<char> const & value) const;

        std::string echo_error(double value) const;

        template <typename T>
        T echo_template(T const & value) const;
};

template <typename T>
T Echo::echo_template(T const & value) const {
    return value;
}

template<>
inline int Echo::echo_template<int>(int const & value) const {
    throw std::out_of_range("Testing exceptions and templates");
}

}

