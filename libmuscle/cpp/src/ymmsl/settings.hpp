#pragma once

#include <cinttypes>
#include <string>
#include <utility>
#include <vector>


namespace ymmsl {

/** Holds the value of a parameter.
 *
 * This is a discriminated union containing any of a number of types. If
 * HPC machines had support of C++17, then I could use std::variant.
 */
class ParameterValue {
    public:
        ParameterValue();
        ParameterValue(std::string const & value);
        // will take bool overload if not explicitly specified!
        ParameterValue(char const * value);
        ParameterValue(int64_t value);
        ParameterValue(double value);
        ParameterValue(bool value);
        ParameterValue(std::initializer_list<double> value);
        ParameterValue(std::vector<double> const & value);
        ParameterValue(std::initializer_list<std::vector<double>> const & value);
        ParameterValue(std::vector<std::vector<double>> const & value);

        ParameterValue(ParameterValue const & other);
        ParameterValue(ParameterValue && other);

        ParameterValue const & operator=(ParameterValue const & other);
        ParameterValue const & operator=(ParameterValue && other);

        ~ParameterValue();

        /** Return whether this ParameterValue holds a value of the given type.
         *
         * @param T A valid type, being one of std::string, int64_t, double,
         *          bool, std::vector<double>, or
         *          std::vector<std::vector<double>>.
         */
        template <typename T>
        bool is() const;

        /** Return the value of the given type.
         *
         * @param T A valid type, being one of std::string, int64_t, double,
         *          bool, std::vector<double>, or
         *          std::vector<std::vector<double>>.
         *
         * Only call if is<T>() returns true.
         */
        template <typename T>
        T get() const;

    private:
        void deactivate_() noexcept;
        void copy_value_from_(ParameterValue const & other);
        void move_value_from_(ParameterValue && other);

        enum class Type_ {
            INACTIVE, STRING, INT, FLOAT, BOOL, LIST_FLOAT, LIST_LIST_FLOAT
        };

        Type_ type_;
        union {
            std::string string_value_;
            int64_t int_value_;
            double float_value_;
            bool bool_value_;
            std::vector<double> list_value_;
            std::vector<std::vector<double>> list_list_value_;
        };
};

}


