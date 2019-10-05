#pragma once

#include <cinttypes>
#include <string>
#include <unordered_map>
#include <utility>
#include <vector>

#include "ymmsl/identity.hpp"


namespace ymmsl {

/** Holds the value of a setting.
 *
 * This is a discriminated union containing any of a number of types. If
 * HPC machines had support for C++17, then I could use std::variant.
 */
class SettingValue {
    public:
        SettingValue();
        SettingValue(std::string const & value);
        // will take bool overload if not explicitly specified!
        SettingValue(char const * value);
        SettingValue(int value);
        SettingValue(int64_t value);
        SettingValue(double value);
        SettingValue(bool value);
        SettingValue(std::initializer_list<double> value);
        SettingValue(std::vector<double> const & value);
        SettingValue(std::initializer_list<std::vector<double>> const & value);
        SettingValue(std::vector<std::vector<double>> const & value);

        SettingValue(SettingValue const & other);
        SettingValue(SettingValue && other);

        SettingValue const & operator=(SettingValue const & other);
        SettingValue const & operator=(SettingValue && other);

        ~SettingValue();

        /** Compare against another SettingValue.
         *
         * Returns true iff both type and value are the same.
         *
         * @param rhs The value to compare with.
         */
        bool operator==(SettingValue const & rhs) const;

        /** Compare against another SettingValue.
         *
         * Returns true iff both type and value are the same.
         *
         * @param rhs The value to compare with.
         */
        bool operator!=(SettingValue const & rhs) const;

        /** Return whether this SettingValue holds a value of the given type.
         *
         * @param T A valid type, being one of std::string, int64_t, double,
         *          bool, std::vector<double>, or
         *          std::vector<std::vector<double>>.
         */
        template <typename T>
        bool is_a() const;

        /** Return the value as the given type.
         *
         * Only call if is_a<T>() returns true.
         *
         * @param T A valid type, being one of std::string, int64_t, double,
         *          bool, std::vector<double>, or
         *          std::vector<std::vector<double>>.
         *
         * @throw std::bad_cast if the type of this value does not match the
         *      template parameter.
         */
        template <typename T>
        T as() const;

    private:
        void deactivate_() noexcept;
        void copy_value_from_(SettingValue const & other);
        void move_value_from_(SettingValue && other);

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

std::ostream & operator<<(std::ostream & os, ymmsl::SettingValue const & val);


/** Settings for doing an experiment.
 *
 * An experiment is done by running a model with particular settings, e.g.
 * the submodel scales, model parameters, and any other settings.
 */
class Settings {
    using MapType_ = std::unordered_map<Reference, SettingValue>;
    public:
        // No, not going to type-erase this.
        using const_iterator = MapType_::const_iterator;

        bool operator==(Settings const & rhs) const;
        bool operator!=(Settings const & rhs) const;

        /** Return the number of settings in this object.
         */
        std::size_t size() const;

        /** Return true iff this object has no settings.
         */
        bool empty() const;

        /** Return true iff a setting with this name exists here.
         *
         * @param setting Name of the setting to check for.
         * @return true iff it exists.
         */
        bool contains(Reference const & setting) const;

        /** Get the value of a given setting.
         *
         * @param setting The name of the setting to read.
         * @return The value of that setting.
         * @throws std::out_of_range if there is no setting with that name.
         */
        SettingValue const & at(Reference const & setting) const;

        /** Set the value of a given setting.
         *
         * Adds the setting first if it does not exist.
         *
         * @param setting The name of the setting to read.
         * @return A reference to the setting's value that can be modified.
         */
        SettingValue & operator[](Reference const & setting);

        /** Removes setting with the given key.
         *
         * @param setting Key of the setting to remove.
         * @return The number of settings removed (0u or 1u).
         */
        std::size_t erase(std::string const & setting);

        /** Removes all settings.
         */
        void clear();

        /** Return an iterator to the first setting.
         *
         * The iterator dereferences to a std::pair<Reference, SettingValue>.
         */
        const_iterator begin() const;

        /** Return an iterator past the last setting.
         */
        const_iterator end() const;

    private:
        MapType_ store_;
};

std::ostream & operator<<(std::ostream & os, ymmsl::Settings const & settings);

}

#include <ymmsl/settings.tpp>

