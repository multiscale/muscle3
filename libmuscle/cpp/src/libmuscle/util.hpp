#pragma once

#include <cstddef>
#include <exception>
#include <ostream>
#include <stdexcept>
#include <string>

#ifdef MUSCLE_ENABLE_MPI
#include <mpi.h>
#endif

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

 * @param filename Default file name to use.
 * @return Path to the log file to write.
 */
std::string extract_log_file_location(
        int argc, char const * const argv[], std::string const & filename);


/* Helper for errors and MPI.
 *
 * When running with MPI, we sometimes do things only on the root process. If a
 * fatal error occurs in that case, then we need to propagate at least the fact that
 * it happened to the other processes so that we can shut down cleanly. This is a
 * helper for that.
 */
class Error {
    public:
        /* Create an Error representing success.
         */
        Error();

        /* Create an Error from the given exception object.
         *
         * The exception must be either std::logic_error or std::runtime_error.
         *
         * @param exc Exception to represent.
         */
        Error(std::exception const & exc);

#ifdef MUSCLE_ENABLE_MPI
        /* Broadcast the error to all MPI processes.
         *
         * There's no way to broadcast the message, as it will only get logged on the
         * root anyway.
         *
         * @param comm Communicator to broadcast on.
         * @param root Rank of the process holding the value.
         */
        void bcast(MPI_Comm & comm, int root = 0) const;
#endif

        /* Returns whether this object represents an error condition.
         *
         * @return True iff there was an error.
         */
        bool is_error() const;

        /* Returns the error message.
         *
         * @return The stored error message.
         */
        std::string const & get_message() const;

        /* Throw an exception equivalent to the one passed to the constructor.
         *
         * If this object represents success, then this function does nothing.
         */
        void throw_if_error() const;

    private:
        /* Type of exception this represents
         *
         * 0 = success, 1 = std::logic_error, 2 = std::runtime_error.
         *
         * Not using an enum here (or an exception object) because MPI doesn't
         * understand them, so we cannot broadcast them.
         */
        int type_;

        /* Description of the problem
         *
         * This is non-empty only on the root process and if type is not 0.
         */
        std::string message_;
};


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

