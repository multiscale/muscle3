#include <algorithm>
#include <iterator>
#include <sstream>
#include <stdexcept>
#include <string>

#include "ymmsl/identity.hpp"


using namespace std::string_literals;


::std::size_t ::std::hash<::ymmsl::Identifier>::operator()(
        argument_type const & id) const noexcept
{
    return hash<std::string>()(id.data_);
}

namespace ymmsl {

Identifier::Identifier(std::string const & contents)
    : data_(contents)
{
    auto msg = "'" + contents + "' is not a valid identifier. Identifiers must"
            " consist only of lower- and uppercase letters, digits and"
            " underscores, must start with a letter or an underscore, and must"
            " not be empty.";

    if (contents.empty())
        throw std::invalid_argument(msg);

    for (auto it = data_.cbegin(); it != data_.cend(); ++it) {
        bool is_lower = (('a' <= *it) && (*it <= 'z'));
        bool is_upper = (('A' <= *it) && (*it <= 'Z'));
        bool is_digit = (('0' <= *it) && (*it <= '9'));
        bool is_under = (*it == '_');

        bool valid_first_char = is_lower || is_upper || is_under;
        if (it == data_.cbegin() && !valid_first_char)
            throw std::invalid_argument(msg);

        if (!(is_lower || is_upper || is_digit || is_under))
            throw std::invalid_argument(msg);
    }
}

Identifier::Identifier(char const * const contents)
    : Identifier(std::string(contents))
{}

Identifier::operator std::string() const {
    return data_;
}

bool Identifier::operator==(Identifier const & rhs) const {
    return data_ == rhs.data_;
}

bool Identifier::operator==(std::string const & rhs) const {
    return data_ == rhs;
}

bool Identifier::operator==(char const * const rhs) const {
    return data_ == rhs;
}

bool Identifier::operator!=(Identifier const & rhs) const {
    return data_ != rhs.data_;
}

bool Identifier::operator!=(std::string const & rhs) const {
    return data_ != rhs;
}

bool Identifier::operator!=(char const * const rhs) const {
    return data_ != rhs;
}

bool operator==(std::string const & lhs, Identifier const & rhs) {
    return lhs == rhs.data_;
}

bool operator!=(std::string const & lhs, Identifier const & rhs) {
    return lhs != rhs.data_;
}

std::ostream & operator<<(std::ostream & os, Identifier const & i) {
    return os << i.data_;
}

std::string operator+(std::string const & lhs, Identifier const & rhs) {
    return lhs + static_cast<std::string>(rhs);
}

std::string operator+(Identifier const & lhs, std::string const & rhs) {
    return static_cast<std::string>(lhs) + rhs;
}

ReferencePart::ReferencePart(Identifier const & i)
    : identifier_(i)
    , index_(-1)
{}

ReferencePart::ReferencePart(int index)
    : identifier_("invalid")
    , index_(index)
{}

bool ReferencePart::is_identifier() const {
    return index_ < 0;
}

bool ReferencePart::is_index() const {
    return index_ >= 0;
}

Identifier const & ReferencePart::identifier() const {
    return identifier_;
}

int ReferencePart::index() const {
    return index_;
}

bool ReferencePart::operator==(ReferencePart const & rhs) const {
    if (is_identifier())
        return rhs.is_identifier() && (identifier_ == rhs.identifier_);
    return rhs.is_index() && (index_ == rhs.index_);
}


Reference::Reference(char const * content)
    : parts_(string_to_parts_(content))
{}

Reference::Reference(std::string const & content)
    : parts_(string_to_parts_(content))
{}

Reference::operator std::string() const {
    return Reference::parts_to_string_(parts_);
}

std::size_t Reference::length() const {
    return parts_.size();
}

bool Reference::operator==(Reference const & rhs) const {
    return std::equal(parts_.cbegin(), parts_.cend(), rhs.cbegin(), rhs.cend());
}

bool Reference::operator==(std::string const & rhs) const {
    return parts_to_string_(parts_) == rhs;
}

bool Reference::operator==(char const * rhs) const {
    return parts_to_string_(parts_) == std::string(rhs);
}

bool Reference::operator!=(Reference const & rhs) const {
    return !(*this == rhs);
}

bool Reference::operator!=(std::string const & rhs) const {
    return !(*this == rhs);
}

bool Reference::operator!=(char const * rhs) const {
    return !(*this == std::string(rhs));
}

Reference::const_iterator Reference::cbegin() const {
    return parts_.cbegin();
}

Reference::const_iterator Reference::cend() const {
    return parts_.cend();
}

Reference::const_iterator Reference::begin() const {
    return parts_.cbegin();
}

Reference::const_iterator Reference::end() const {
    return parts_.cend();
}

ReferencePart const & Reference::operator[](int i) const {
    return parts_[i];
}

Reference const & Reference::operator+=(ReferencePart const & rhs) {
    parts_.push_back(rhs);
    return *this;
}

Reference const & Reference::operator+=(std::vector<int> const & rhs) {
    std::copy(rhs.cbegin(), rhs.cend(), std::back_inserter(parts_));
    return *this;
}

Reference Reference::operator+(Reference const & rhs) const {
    std::vector<ReferencePart> new_parts(parts_);
    std::copy(rhs.cbegin(), rhs.cend(), std::back_inserter(new_parts));
    return Reference(std::move(new_parts));
}

Reference Reference::operator+(ReferencePart const & rhs) const {
    std::vector<ReferencePart> new_parts(parts_);
    new_parts.push_back(rhs);
    return Reference(std::move(new_parts));
}

Reference Reference::operator+(std::vector<int> const & rhs) const {
    std::vector<ReferencePart> new_parts(parts_);
    std::copy(rhs.cbegin(), rhs.cend(), std::back_inserter(new_parts));
    return Reference(std::move(new_parts));
}

std::ostream & operator<<(std::ostream & os, Reference const & r) {
    return os << Reference::parts_to_string_(r.parts_);
}

Reference::Reference(std::vector<ReferencePart> && parts)
    : parts_(parts)
{}

namespace {
    std::size_t find_next_op(std::string const & text, std::size_t start) {
        auto next_bracket = text.find('[', start);
        if (next_bracket == std::string::npos)
            next_bracket = text.length();
        auto next_period = text.find('.', start);
        if (next_period == std::string::npos)
            next_period = text.length();
        return std::min(next_bracket, next_period);
    }
}

std::vector<ReferencePart> Reference::string_to_parts_(std::string const & text) {
    auto parts = std::vector<ReferencePart>();
    auto end = text.length();

    auto cur_op = find_next_op(text, 0u);
    parts.push_back(Identifier(text.substr(0u, cur_op)));

    while (cur_op < end) {
        if (text[cur_op] == '.') {
            auto next_op = find_next_op(text, cur_op + 1u);
            auto id = Identifier(text.substr(cur_op + 1u, next_op - cur_op - 1u));
            parts.push_back(ReferencePart(id));
            cur_op = next_op;
        }
        else if (text[cur_op] == '[') {
            auto close_bracket = text.find(']', cur_op);
            if (close_bracket == std::string::npos)
                throw std::invalid_argument("Missing closing bracket in"
                                            " Reference " + text);
            auto index_str = text.substr(cur_op + 1, close_bracket - cur_op - 1u);
            try {
                auto index = std::stoi(index_str);
                parts.push_back(ReferencePart(index));
            }
            catch (std::invalid_argument const & e) {
                throw std::invalid_argument("Invalid index '" + index_str +
                        "' in " + text + ", expected an int.");
            }
            catch (std::out_of_range const & e) {
                throw std::invalid_argument("Invalid index '" + index_str +
                        "' in " + text + ", the value is out of range.");
            }
            cur_op = close_bracket + 1;
        }
        else {
            throw std::invalid_argument("Invalid character '"s +
                    text[cur_op] + " in Reference " + text);
        }
    }
    return parts;
}

std::string Reference::parts_to_string_(std::vector<ReferencePart> const & parts) {
    std::ostringstream oss;
    for (auto it = parts.cbegin(); it != parts.cend(); ++it) {
        if (it->is_identifier()) {
            if (it != parts.cbegin())
                oss << ".";
            oss << it->identifier();
        }
        else
            oss << "[" << it->index() << "]";
    }
    return oss.str();
}

bool operator==(::std::string const & lhs, Reference const & rhs) {
    return rhs == lhs;
}

bool operator!=(::std::string const & lhs, Reference const & rhs) {
    return rhs != lhs;
}

}

