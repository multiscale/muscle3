#pragma once

#include <functional>
#include <ostream>
#include <string>
#include <vector>


namespace ymmsl {
    class Identifier;
}

namespace std {
    template<> struct hash<::ymmsl::Identifier> {
        typedef ::ymmsl::Identifier argument_type;
        typedef size_t result_type;

        std::size_t operator()(::ymmsl::Identifier const &) const noexcept;
    };
}


namespace ymmsl {

/** A custom string type that represents an identifier.
 *
 * An identifier may consist of upper- and lowercase characters, digits, and
 * underscores.
 */
class Identifier {
    public:
        /** Create an Identifier.
         *
         * This creates a new identifier object, using the string
         * representation of whichever object you pass.
         *
         * @param contents The contents of the identifier.
         *
         * @throws std::invalid_argument if contents is not a valid identifier.
         */
        Identifier(std::string const & contents);

        /** Implicit conversion to std::string.
         *
         * This is a custom string class, so that's appropriate.
         *
         * @return The string representation of this Identifier.
         */
        operator std::string() const;

        /** Compare for equality.
         *
         * @param rhs The Identifier to compare against.
         *
         * @return True iff both Identifiers are equal.
         */
        bool operator==(Identifier const & rhs) const;

        /** Compare for equality against a string.
         *
         * @param rhs The string to compare against.
         *
         * @return True iff the Identifier matches the string.
         */
        bool operator==(std::string const & rhs) const;

        /** Compare for inequality.
         *
         * @param rhs The Identifier to compare against.
         *
         * @return True iff both Identifiers are different.
         */
        bool operator!=(Identifier const & rhs) const;

        /** Compare for inequality against a string.
         *
         * @param rhs The string to compare against.
         *
         * @return True iff the Identifier is different from the string.
         */
        bool operator!=(std::string const & rhs) const;


    private:
        friend bool operator==(std::string const & lhs, Identifier const & rhs);
        friend bool operator!=(std::string const & lhs, Identifier const & rhs);
        friend std::ostream & operator<<(std::ostream & os, Identifier const & i);
        friend ::std::size_t ::std::hash<::ymmsl::Identifier>::operator()(
                ::ymmsl::Identifier const & id) const;
        std::string data_;
};

/** Concatenate an Identifier onto a string.
 *
 * @param lhs A string.
 * @param rhs An identifier to add onto it.
 * @return A string containing the concatenation of the given string and the
 *         string form of the Identifier.
 */
std::string operator+(std::string const & lhs, Identifier const & rhs);

/** Concatenate a string onto an Identifier.
 *
 * @param lhs An Identifier.
 * @param rhs A string to add onto it.
 * @return A string containing the concatenation of the string form of the
 *         given Identifier and the string.
 */
std::string operator+(Identifier const & lhs, std::string const & rhs);


/** An item in a Reference.
 */
class ReferencePart {
    public:
        /** Create a ReferencePart containing an Identifier.
         *
         * This is implicit, so that you can give an Identifier wherever a
         * ReferencePart is required.
         *
         * @param i The Identifier to store.
         */
        ReferencePart(Identifier const & i);

        /** Create a ReferencePart containing an index.
         *
         * This is implicit, so that you can give an int wherever a
         * ReferencePart is required.
         *
         * @param index The index to store.
         */
        ReferencePart(int index);

        /** Returns whether this Part holds an Identifier.
         *
         * @return True iff this holds an Identifier.
         */
        bool is_identifier() const;

        /** Returns whether this Part holds an index.
         *
         * @return True iff this holds an index.
         */
        bool is_index() const;

        /** Returns the Identifier value.
         *
         * @return The identifier value.
         *
         * @throws std::runtime_error if this object does not hold an Identifier.
         */
        Identifier const & identifier() const;

        /** Returns the index value.
         *
         * @return The index value.
         *
         * @throws std::runtime_error if this object does not hold an index.
         */
        int index() const;

        /** Compares for equality.
         *
         * @param rhs The ReferencePart to compare with.
         *
         * @return True if both type and value match.
         */
        bool operator==(ReferencePart const & rhs) const;

    private:
        Identifier identifier_;
        int index_;
};


/** A reference to an object in the MMSL execution model.
 *
 * References in string form are written as either:
 *
 * - an Identifier,
 * - a Reference followed by a period and an Identifier, or
 * - a Reference followed by an integer enclosed in square brackets.
 *
 * In object form, they consist of a list of Identifiers and ints. The first
 * list item is always an Identifier. For the rest of the list, an Identifier
 * represents a period operator with that argument, while an int represents the
 * indexing operator with that argument.
 *
 * Reference objects act like a list of Identifiers and ints, you can get their
 * length using length(), iterate through the parts using cbegin() and cend(),
 * and get individual items using []. Note that the sublist has to be a valid
 * Reference, so it cannot start with an int.

 * References can be compared for equality to each other or to a
 * plain string, and they can be used as dictionary keys. Reference
 * objects are immutable (or they're supposed to be anyway), so do not
 * try to change any of the elements. Instead, make a new Reference.
 * Especially References that are used as dictionary keys must not be
 * modified, this will get your dictionary in a very confused state.
 */
class Reference {
    public:
        /** Random access iterator type for a Reference.
         */
        typedef std::vector<ReferencePart>::const_iterator const_iterator;

        /** Create a Reference from a string.
         *
         * Creates a Reference from a string, which will be parsed.
         *
         * @param contents A string to parse.
         *
         * @throws std::invalid_argument if the argument does not define a
         *         valid Reference.
         */
        Reference(std::string const & content);

        /** Create a Reference from a C string.
         *
         * Creates a Reference from a C string, which will be parsed.
         *
         * @param contents A string to parse.
         *
         * @throws std::invalid_argument if the argument does not define a
         *         valid Reference.
         */
        Reference(char const * content);

        /** Create a Reference from a ReferencePart range.
         *
         * *begin and *end must be of type ReferencePart.
         *
         * @param begin An iterator to the start of the range.
         * @param end An iterator to the end of the range.
         */
        template <class ForwardIt>
        Reference(ForwardIt begin, ForwardIt end);

        /** Conversion to std::string.
         *
         * @return The string representation of this Identifier.
         */
        explicit operator std::string() const;

        /** Returns the number of parts in the Reference.
         */
        std::size_t length() const;

        /** Compares for equality.
         *
         * Will compare part-by-part.
         *
         * @param rhs The Reference to compare with.
         *
         * @return True iff the two References are equal.
         */
        bool operator==(Reference const & rhs) const;

        /** Compares for equality.
         *
         * Compares string representations.
         *
         * @param rhs The string to compare with.
         *
         * @return True iff this Reference matches the given string.
         */
        bool operator==(std::string const & rhs) const;

        /** Compares for equality.
         *
         * Compares string representations.
         *
         * @param rhs The string to compare with.
         *
         * @return True iff this Reference matches the given string.
         */
        bool operator==(char const * rhs) const;

        /** Compares for inequality.
         *
         * Will compare part-by-part.
         *
         * @param rhs The Reference to compare with.
         *
         * @return True iff the two References are different.
         */
        bool operator!=(Reference const & rhs) const;

        /** Compares for inequality.
         *
         * Compares string representations.
         *
         * @param rhs The string to compare with.
         *
         * @return True iff this Reference does not match the given string.
         */
        bool operator!=(std::string const & rhs) const;

        /** Compares for inequality.
         *
         * Compares string representations.
         *
         * @param rhs The string to compare with.
         *
         * @return True iff this Reference does not match the given string.
         */
        bool operator!=(char const * rhs) const;

        /** Returns a const_iterator to the beginning of the Reference.
         */
        const_iterator cbegin() const;

        /** Returns a const_iterator to one-past-the-end of the Reference.
         */
        const_iterator cend() const;

        /** Returns a const_iterator to the beginning of the Reference.
         */
        const_iterator begin() const;

        /** Returns a const_iterator to one-past-the-end of the Reference.
         */
        const_iterator end() const;

        /** Returns the ReferencePart at the given index.
         *
         * @param i The index to dereference.
         * @return The ReferencePart at that index.
         */
        ReferencePart const & operator[](int i) const;

        /** Append a part to this Reference.
         *
         * @param rhs The part to append.
         * @return A reference to this (updated) object.
         */
        Reference const & operator+=(ReferencePart const & rhs);

        /** Append a list of indexes to this Reference.
         *
         * @param rhs The indexes to append.
         *
         * @return A reference to this (updated) object.
         */
        Reference const & operator+=(std::vector<int> const & rhs);

        /** Concatenate two References.
         *
         * @param rhs The Reference to append to this one to produce the new
         *        Reference.
         */
        Reference operator+(Reference const & rhs) const;

        /** Append a ReferencePart to this Reference to create a new one.
         *
         * @param rhs The ReferencePart to append to this one to produce the
         *        new Reference.
         */
        Reference operator+(ReferencePart const & rhs) const;

    private:
        friend std::ostream & operator<<(std::ostream & os, Reference const & r);

        std::vector<ReferencePart> parts_;

        Reference(std::vector<ReferencePart> && parts);
        static std::vector<ReferencePart> string_to_parts_(
                std::string const & text);
        static std::string parts_to_string_(
                std::vector<ReferencePart> const & parts);
};

/** Compare a string with a Reference for equality.
 *
 * @param lhs The left-hand side of the comparison.
 * @param rhs The right-hand side of the comparison.
 *
 * @return True iff the string matches the Reference.
 */
bool operator==(std::string const & lhs, Reference const & rhs);

/** Compare a string with a Reference for equality.
 *
 * @param lhs The left-hand side of the comparison.
 * @param rhs The right-hand side of the comparison.
 *
 * @return True iff the string does not match the Reference.
 */
bool operator!=(std::string const & lhs, Reference const & rhs);

}

namespace std {
    template<> struct hash<::ymmsl::ReferencePart> {
        typedef ::ymmsl::ReferencePart argument_type;
        typedef size_t result_type;

        result_type operator()(argument_type const & refpart) const noexcept {
            if (refpart.is_identifier())
                return hash<::ymmsl::Identifier>()(refpart.identifier());
            return hash<int>()(refpart.index());
        }
    };

    template<> struct hash<::ymmsl::Reference> {
        typedef ::ymmsl::Reference argument_type;
        typedef size_t result_type;

        result_type operator()(argument_type const & ref) const noexcept {
            result_type res = 0ul;
            for (auto const & part : ref)
                res ^= hash<::ymmsl::ReferencePart>()(part) + 0x9e3779b9 + (res << 6) + (res >> 2);
            return res;
        }
    };
}

namespace ymmsl {

template <class ForwardIt>
Reference::Reference(ForwardIt begin, ForwardIt end)
    : parts_(begin, end)
{}

}

