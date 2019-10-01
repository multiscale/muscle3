#include <ymmsl/settings.hpp>

#include <typeinfo>
#include <utility>

#include <ymmsl/identity.hpp>


namespace ymmsl {

ParameterValue::ParameterValue()
    : type_(ParameterValue::Type_::INACTIVE)
{}

ParameterValue::ParameterValue(std::string const & value)
    : type_(ParameterValue::Type_::STRING)
{
    new (&string_value_) std::string(value);
}

ParameterValue::ParameterValue(char const * value)
    : type_(ParameterValue::Type_::STRING)
{
    new (&string_value_) std::string(value);
}

ParameterValue::ParameterValue(int value)
    : type_(ParameterValue::Type_::INT)
    , int_value_(value)
{}

ParameterValue::ParameterValue(int64_t value)
    : type_(ParameterValue::Type_::INT)
    , int_value_(value)
{}

ParameterValue::ParameterValue(double value)
    : type_(ParameterValue::Type_::FLOAT)
    , float_value_(value)
{}

ParameterValue::ParameterValue(bool value)
    : type_(ParameterValue::Type_::BOOL)
    , bool_value_(value)
{}

ParameterValue::ParameterValue(std::initializer_list<double> value)
    : type_(ParameterValue::Type_::LIST_FLOAT)
{
    new (&list_value_) std::vector<double>(value);
}

ParameterValue::ParameterValue(std::vector<double> const & value)
    : type_(ParameterValue::Type_::LIST_FLOAT)
{
    new (&list_value_) std::vector<double>(value);
}

ParameterValue::ParameterValue(std::initializer_list<std::vector<double>> const & value)
    : type_(ParameterValue::Type_::LIST_LIST_FLOAT)
{
    new (&list_list_value_) std::vector<std::vector<double>>(value);
}

ParameterValue::ParameterValue(std::vector<std::vector<double>> const & value)
    : type_(ParameterValue::Type_::LIST_LIST_FLOAT)
{
    new (&list_list_value_) std::vector<std::vector<double>>(value);
}

ParameterValue::ParameterValue(ParameterValue const & other)
    : type_(other.type_)
{
    copy_value_from_(other);
}

ParameterValue::ParameterValue(ParameterValue && other)
    : type_(other.type_)
{
    move_value_from_(std::move(other));
    other.deactivate_();
}

ParameterValue const & ParameterValue::operator=(ParameterValue const & other) {
    deactivate_();
    copy_value_from_(other);
    type_ = other.type_;
    return *this;
}

ParameterValue const & ParameterValue::operator=(ParameterValue && other) {
    deactivate_();
    move_value_from_(std::move(other));
    type_ = other.type_;
    other.deactivate_();
    return *this;
}

ParameterValue::~ParameterValue() {
    deactivate_();
}

bool ParameterValue::operator==(ParameterValue const & rhs) const {
    switch (type_) {
        case Type_::INACTIVE:
            return rhs.type_ == Type_::INACTIVE;
        case Type_::STRING:
            return (rhs.type_ == Type_::STRING) && (string_value_ == rhs.string_value_);
        case Type_::INT:
            return (rhs.type_ == Type_::INT) && (int_value_ == rhs.int_value_);
        case Type_::FLOAT:
            return (rhs.type_ == Type_::FLOAT) && (float_value_ == rhs.float_value_);
        case Type_::BOOL:
            return (rhs.type_ == Type_::BOOL) && (bool_value_ == rhs.bool_value_);
        case Type_::LIST_FLOAT:
            return (rhs.type_ == Type_::LIST_FLOAT) && (list_value_ == rhs.list_value_);
        case Type_::LIST_LIST_FLOAT:
            return (rhs.type_ == Type_::LIST_LIST_FLOAT) && (list_list_value_ == rhs.list_list_value_);
    }
    return false;
}

bool ParameterValue::operator!=(ParameterValue const & rhs) const {
    return !(*this == rhs);
}

void ParameterValue::deactivate_() noexcept {
    switch (type_) {
        case Type_::STRING:
            string_value_.~basic_string();
            break;
        case Type_::LIST_FLOAT:
            list_value_.~vector();
            break;
        case Type_::LIST_LIST_FLOAT:
            list_list_value_.~vector();
            break;
        default:
            break;
    }
    type_ = Type_::INACTIVE;
}

void ParameterValue::copy_value_from_(ParameterValue const & other) {
    switch (other.type_) {
        case Type_::INACTIVE:
            break;
        case Type_::STRING:
            new (&string_value_) std::string(other.string_value_);
            break;
        case Type_::INT:
            int_value_ = other.int_value_;
            break;
        case Type_::FLOAT:
            float_value_ = other.float_value_;
            break;
        case Type_::BOOL:
            bool_value_ = other.bool_value_;
            break;
        case Type_::LIST_FLOAT:
            new (&list_value_) std::vector<double>(other.list_value_);
            break;
        case Type_::LIST_LIST_FLOAT:
            new (&list_list_value_) std::vector<std::vector<double>>(other.list_list_value_);
            break;
    }
}

void ParameterValue::move_value_from_(ParameterValue && other) {
    switch (other.type_) {
        case Type_::INACTIVE:
            break;
        case Type_::STRING:
            new (&string_value_) std::string(std::move(other.string_value_));
            break;
        case Type_::INT:
            int_value_ = other.int_value_;
            break;
        case Type_::FLOAT:
            float_value_ = other.float_value_;
            break;
        case Type_::BOOL:
            bool_value_ = other.bool_value_;
            break;
        case Type_::LIST_FLOAT:
            new (&list_value_) std::vector<double>(std::move(other.list_value_));
            break;
        case Type_::LIST_LIST_FLOAT:
            new (&list_list_value_) std::vector<std::vector<double>>(std::move(other.list_list_value_));
            break;
    }
}

namespace {

void write_vec_double(std::ostream & os, std::vector<double> const & val) {
    bool first = true;
    os << "[";
    for (double d : val) {
        if (!first)
            os << ", ";
        os << d;
        first = false;
    }
    os << "]";
}

}

std::ostream & operator<<(std::ostream & os, ymmsl::ParameterValue const & val) {
    if (val.is_a<std::string>())
        os << "\"" << val.as<std::string>() << "\"";
    else if (val.is_a<int64_t>())
        os << val.as<int64_t>();
    else if (val.is_a<double>())
        os << val.as<double>();
    else if (val.is_a<bool>())
        os << std::boolalpha << val.as<bool>();
    else if (val.is_a<std::vector<double>>())
        write_vec_double(os, val.as<std::vector<double>>());
    else if (val.is_a<std::vector<std::vector<double>>>()) {
        bool first = true;
        os << "[";
        for (auto const & vec : val.as<std::vector<std::vector<double>>>()) {
            if (!first)
                os << ", ";
            write_vec_double(os, vec);
            first = false;
        }
        os << "]";
    }
    return os;
}


bool Settings::operator==(Settings const & rhs) const {
    return store_ == rhs.store_;
}

bool Settings::operator!=(Settings const & rhs) const {
    return store_ != rhs.store_;
}

std::size_t Settings::size() const {
    return store_.size();
}

bool Settings::empty() const {
    return store_.empty();
}

bool Settings::contains(Reference const & setting) const {
    return store_.count(setting) != 0u;
}

ParameterValue const & Settings::at(Reference const & setting) const {
    return store_.at(setting);
}

ParameterValue & Settings::operator[](Reference const & setting) {
    return store_[setting];
}

std::size_t Settings::erase(std::string const & setting) {
    return store_.erase(Reference(setting));
}

void Settings::clear() {
    store_.clear();
}

Settings::const_iterator Settings::begin() const {
    return store_.cbegin();
}

Settings::const_iterator Settings::end() const {
    return store_.cend();
}

std::ostream & operator<<(std::ostream & os, ymmsl::Settings const & settings) {
    bool first = true;
    os << "Settings(";
    for (auto const & setting : settings) {
        if (!first)
            os << ", ";
        os << setting.first << ": " << setting.second;
        first = false;
    }
    os << ")";
    return os;
}

}

