#include <ymmsl/settings.hpp>

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

template<>
bool ParameterValue::is<std::string>() const {
    return type_ == Type_::STRING;
}

template<>
bool ParameterValue::is<int64_t>() const {
    return type_ == Type_::INT;
}

template<>
bool ParameterValue::is<double>() const {
    return type_ == Type_::FLOAT;
}

template<>
bool ParameterValue::is<bool>() const {
    return type_ == Type_::BOOL;
}

template<>
bool ParameterValue::is<std::vector<double>>() const {
    return type_ == Type_::LIST_FLOAT;
}

template<>
bool ParameterValue::is<std::vector<std::vector<double>>>() const {
    return type_ == Type_::LIST_LIST_FLOAT;
}

template<>
std::string ParameterValue::get<std::string>() const {
    return string_value_;
}

template<>
int64_t ParameterValue::get<int64_t>() const {
    return int_value_;
}

template<>
double ParameterValue::get<double>() const {
    return float_value_;
}

template<>
bool ParameterValue::get<bool>() const {
    return bool_value_;
}

template<>
std::vector<double> ParameterValue::get<std::vector<double>>() const {
    return list_value_;
}

template<>
std::vector<std::vector<double>> ParameterValue::get<std::vector<std::vector<double>>>() const {
    return list_list_value_;
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

bool Settings::contains(std::string const & setting) const {
    return store_.count(Reference(setting)) != 0u;
}

bool Settings::contains(Reference const & setting) const {
    return store_.count(setting) != 0u;
}

ParameterValue const & Settings::at(std::string const & setting) const {
    return store_.at(Reference(setting));
}

ParameterValue const & Settings::at(Reference const & setting) const {
    return store_.at(setting);
}

ParameterValue & Settings::operator[](std::string const & setting) {
    return store_[Reference(setting)];
}

ParameterValue & Settings::operator[](Reference const & setting) {
    return store_[setting];
}

std::size_t Settings::erase(std::string const & setting) {
    return store_.erase(Reference(setting));
}

Settings::const_iterator Settings::begin() const {
    return store_.cbegin();
}

Settings::const_iterator Settings::end() const {
    return store_.cend();
}

}

