#include <stdexcept>

#include "ymmsl/identity.hpp"


namespace {
    const char * invalid_identifier_msg = (
            "Identifiers must consist only of lower- and uppercase letters,"
            " digits and underscores, must start with a letter or an"
            " underscore, and must not be empty.");
}

namespace ymmsl {

Identifier::Identifier(std::string const & contents)
    : data_(contents)
{
    if (contents.empty())
        throw std::invalid_argument(invalid_identifier_msg);

    for (auto it = data_.cbegin(); it != data_.cend(); ++it) {
        bool is_lower = (('a' <= *it) && (*it <= 'z'));
        bool is_upper = (('A' <= *it) && (*it <= 'Z'));
        bool is_digit = (('0' <= *it) && (*it <= '9'));
        bool is_under = (*it == '_');

        bool valid_first_char = is_lower || is_upper || is_under;
        if (it == data_.cbegin() && !valid_first_char)
            throw std::invalid_argument(invalid_identifier_msg);

        if (!(is_lower || is_upper || is_digit || is_under))
            throw std::invalid_argument(invalid_identifier_msg);
    }
}


std::ostream & operator<<(std::ostream & os, Identifier const & i) {
    return os << i.data_;
}

}


