#pragma once

#include <cstddef>
#include <ostream>
#include <string>

#include <libmuscle/namespace.hpp>


namespace libmuscle { namespace _MUSCLE_IMPL_NS {


/* Gets the log file location from the command line.
 *
 * Extracts the --muscle-log-file=<path> argument to tell the
 * MUSCLE library where to write the local log file. This
 * function will extract this argument from the command line
 * arguments if it is present. If the given path is to a
 * directory, <filename> will be written inside of that directory,
 * if the path is not an existing directory, then it will be used
 * as the name of the log file to write to. If no command line
 * argument is given, this function returns None.

 * Args:
 *     filename: Default file name to use.
 *
 * Returns:
 *     Path to the log file to write.
 */
std::string extract_log_file_location(
        int argc, char const * const argv[], std::string const & filename);


/* An optional type template.
 *
 * Since we're not doing C++17, we can't use std::optional. This is a simple
 * replacement.
 *
 * I didn't make it compatible because std::optional is quite complex, and this
 * was much quicker to implement.
 */
template <typename T>
class Optional {
    public:
        /** Create a nil optional.
         *
         * is_set() will return false for this object.
         */
        Optional();

        /** Create a nil optional.
         *
         * This allows you to write {} instead of
         * Optional<LengthyTypeName>() when you need a nil optional.
         */
        Optional(std::initializer_list<T>);

        /** Create a non-nil optional with the given value.
         *
         * is_set() will return true for this object, and get() will return it.
         * Also implicitly converts, of course.
         *
         * @param u An object to copy.
         */
        template <typename U>
        Optional(U const & u);

        /** Copy an Optional.
         *
         * @param rhs The object to copy.
         */
        Optional(Optional const & rhs);

        /** Move-construct an Optional.
         *
         * @param rhs The object to move from.
         */
        Optional(Optional && rhs);

        /** Copy-assign an Optional.
         *
         * @param rhs The object to copy from.
         */
        Optional & operator=(Optional const & rhs);

        /** Move-assign an Optional.
         *
         * @param rhs The object to move from.
         */
        Optional & operator=(Optional && rhs);

        /** Destruct an Optional.
         */
        ~Optional();

        /** Compare an Optional for equality.
         *
         * Two unset (nil) Optionals are considered equal.
         */
        bool operator==(Optional const & rhs) const;

        /** Compare an Optional for inequality.
         *
         * Two unset (nil) Optionals are considered equal.
         */
        bool operator!=(Optional const & rhs) const;

        /** Whether the Optional contains a value.
         *
         * @return true iff the Optional contains a T, false if it is nil.
         */
        bool is_set() const;

        /** Get the contained value.
         *
         * Use only if is_set() returns true!
         */
        T const & get() const;

        /** Get the contained value.
         *
         * Use only if is_set() returns true!
         */
        T & get();

    private:
        void destruct_();

        bool is_set_;
        union {
            T t_;
        };
};

template <typename T>
std::ostream & operator<<(std::ostream & os, Optional<T> const & t);

} }

#include <libmuscle/util.tpp>

