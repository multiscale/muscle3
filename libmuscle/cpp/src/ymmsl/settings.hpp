#pragma once

#include <cinttypes>
#include <string>
#include <unordered_map>
#include <utility>
#include <vector>

#include <ymmsl/identity.hpp>


namespace ymmsl { namespace impl {

/** Holds the value of a setting.
 *
 * This is a discriminated union that can contain a std::string, an int64_t,
 * a double, a bool, a std::vector<double> or a
 * std::vector<std::vector<double>>.
 *
 * Values of these types will be automatically converted wherever a
 * SettingValue is required.
 */
class SettingValue {
    public:
        /** Create an empty (and invalid) SettingValue.
         */
        SettingValue();

        /** Create a SettingValue containing a string.
         *
         * @param value The string value to hold.
         */
        SettingValue(std::string const & value);

        /** Create a SettingValue containing a string.
         *
         * @param value The string value to hold.
         */
        // will take bool overload if not explicitly specified!
        SettingValue(char const * value);

        /** Create a SettingValue containing an int64_t.
         *
         * @param value The value to hold.
         */
        SettingValue(int value);

        /** Create a SettingValue containing an int64_t.
         *
         * @param value The value to hold.
         */
        SettingValue(long int value);

        /** Create a SettingValue containing an int64_t.
         *
         * @param value The value to hold.
         */
        SettingValue(long long int value);

        /** Create a SettingValue containing a double.
         *
         * @param value The value to hold.
         */
        SettingValue(double value);

        /** Create a SettingValue containing a bool.
         *
         * @param value The value to hold.
         */
        SettingValue(bool value);

        /** Create a SettingValue containing a std::vector<double>.
         *
         * This covers SettingValue({1.0, 2.0, 3.0});
         *
         * @param value The value to hold.
         */
        SettingValue(std::initializer_list<double> value);

        /** Create a SettingValue containing a std::vector<double>.
         *
         * @param value The value to hold.
         */
        SettingValue(std::vector<double> const & value);

        /** Create a SettingValue containing a std::vector<std::vector<double>>.
         *
         * This covers SettingValue({{1.0, 2.0}, {3.0, 4.0}});
         *
         * @param value The value to hold.
         */
        SettingValue(std::initializer_list<std::vector<double>> const & value);

        /** Create a SettingValue containing a std::vector<std::vector<double>>.
         *
         * @param value The value to hold.
         */
        SettingValue(std::vector<std::vector<double>> const & value);

        /** Copy-constructs a SettingValue.
         */
        SettingValue(SettingValue const & other);

        /** Move-constructs a SettingValue.
         */
        SettingValue(SettingValue && other);

        /** Copy-assigns a SettingValue.
         */
        SettingValue & operator=(SettingValue const & other);

        /** Move-assigns a SettingValue.
         */
        SettingValue & operator=(SettingValue && other);

        /** Destructs a SettingValue.
         */
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
         * Note that for int32_t, this function will return true only if the
         * value is integer and fits in an int32_t. For double, it will return
         * true if the value is integer, even if converting it to a double
         * would reduce precision.
         *
         * Since int and long are usually equivalent to int32_t or int64_t,
         * you can use those values too.
         *
         * @param T A valid type, being one of std::string, int32_t, int64_t,
         *          double, bool, std::vector<double>, or
         *          std::vector<std::vector<double>>.
         */
        template <typename T>
        bool is_a() const;

        /** Return the value as the given type.
         *
         * Only call if is_a<T>() returns true.
         *
         * @param T A valid type, being one of std::string, int32_t, int64_t,
         *          double, bool, std::vector<double>, or
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

/** Outputs a human-readable representation of the SettingValue to a stream.
 *
 * This makes it so you can use e.g. std::cout << setting_value.
 */
std::ostream & operator<<(std::ostream & os, ymmsl::impl::SettingValue const & val);


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

        /** Create an empty Settings object. */
        Settings() = default;

        /** Create a Settings object with the given settings.
         *
         * @param settings std::unordered_map<Reference, SettingValue> with settings.
         */
        Settings(std::unordered_map<Reference, SettingValue> const & settings);

        /** Compare Settings objects for equality.
         *
         * @return True iff the Settings are equal.
         */
        bool operator==(Settings const & rhs) const;

        /** Compare Settings objects for inequality.
         *
         * @return True iff the Settings are not equal.
         */
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


/** Outputs a human-readable representation of the Settings to a stream.
 *
 * This makes it so you can use e.g. std::cout << settings.
 */
std::ostream & operator<<(std::ostream & os, ymmsl::impl::Settings const & settings);

} }

#include <ymmsl/settings.tpp>

