#include <ymmsl/settings.hpp>

#include <typeinfo>
#include <utility>

#include <ymmsl/identity.hpp>


namespace ymmsl { namespace impl {

SettingValue::SettingValue()
    : type_(SettingValue::Type_::INACTIVE)
{}

SettingValue::SettingValue(std::string const & value)
    : type_(SettingValue::Type_::STRING)
{
    new (&string_value_) std::string(value);
}

SettingValue::SettingValue(char const * value)
    : type_(SettingValue::Type_::STRING)
{
    new (&string_value_) std::string(value);
}

SettingValue::SettingValue(int value)
    : type_(SettingValue::Type_::INT)
    , int_value_(value)
{}

SettingValue::SettingValue(long int value)
    : type_(SettingValue::Type_::INT)
    , int_value_(value)
{}

SettingValue::SettingValue(long long int value)
    : type_(SettingValue::Type_::INT)
    , int_value_(value)
{}

SettingValue::SettingValue(double value)
    : type_(SettingValue::Type_::FLOAT)
    , float_value_(value)
{}

SettingValue::SettingValue(bool value)
    : type_(SettingValue::Type_::BOOL)
    , bool_value_(value)
{}

SettingValue::SettingValue(std::initializer_list<int> value)
    : type_(SettingValue::Type_::LIST_INT)
{
    new (&list_int_value_) std::vector<int64_t>();
    list_int_value_.reserve(value.size());
    for (int i : value)
        list_int_value_.push_back(i);
}

SettingValue::SettingValue(std::initializer_list<long> value)
    : type_(SettingValue::Type_::LIST_INT)
{
    new (&list_int_value_) std::vector<int64_t>();
    list_int_value_.reserve(value.size());
    for (long i : value)
        list_int_value_.push_back(i);
}

SettingValue::SettingValue(std::initializer_list<long long> value)
    : type_(SettingValue::Type_::LIST_INT)
{
    new (&list_int_value_) std::vector<int64_t>();
    list_int_value_.reserve(value.size());
    for (long long i : value)
        list_int_value_.push_back(i);
}

SettingValue::SettingValue(std::initializer_list<double> value)
    : type_(SettingValue::Type_::LIST_FLOAT)
{
    new (&list_float_value_) std::vector<double>(value);
}

SettingValue::SettingValue(std::vector<int64_t> const & value)
    : type_(SettingValue::Type_::LIST_INT)
{
    new (&list_int_value_) std::vector<int64_t>(value);
}

SettingValue::SettingValue(std::vector<double> const & value)
    : type_(SettingValue::Type_::LIST_FLOAT)
{
    new (&list_float_value_) std::vector<double>(value);
}

SettingValue::SettingValue(std::initializer_list<std::vector<double>> const & value)
    : type_(SettingValue::Type_::LIST_LIST_FLOAT)
{
    new (&list_list_float_value_) std::vector<std::vector<double>>(value);
}

SettingValue::SettingValue(std::vector<std::vector<double>> const & value)
    : type_(SettingValue::Type_::LIST_LIST_FLOAT)
{
    new (&list_list_float_value_) std::vector<std::vector<double>>(value);
}

SettingValue::SettingValue(SettingValue const & other)
    : type_(other.type_)
{
    copy_value_from_(other);
}

SettingValue::SettingValue(SettingValue && other)
    : type_(other.type_)
{
    move_value_from_(std::move(other));
    other.deactivate_();
}

SettingValue & SettingValue::operator=(SettingValue const & other) {
    deactivate_();
    copy_value_from_(other);
    type_ = other.type_;
    return *this;
}

SettingValue & SettingValue::operator=(SettingValue && other) {
    deactivate_();
    move_value_from_(std::move(other));
    type_ = other.type_;
    other.deactivate_();
    return *this;
}

SettingValue::~SettingValue() {
    deactivate_();
}

bool SettingValue::operator==(SettingValue const & rhs) const {
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
        case Type_::LIST_INT:
            return (rhs.type_ == Type_::LIST_INT) && (list_int_value_ == rhs.list_int_value_);
        case Type_::LIST_FLOAT:
            return (rhs.type_ == Type_::LIST_FLOAT) &&
                   (list_float_value_ == rhs.list_float_value_);
        case Type_::LIST_LIST_FLOAT:
            return (rhs.type_ == Type_::LIST_LIST_FLOAT) &&
                   (list_list_float_value_ == rhs.list_list_float_value_);
    }
    return false;
}

bool SettingValue::operator!=(SettingValue const & rhs) const {
    return !(*this == rhs);
}

void SettingValue::deactivate_() noexcept {
    switch (type_) {
        case Type_::STRING:
            string_value_.~basic_string();
            break;
        case Type_::LIST_INT:
            list_int_value_.~vector();
            break;
        case Type_::LIST_FLOAT:
            list_float_value_.~vector();
            break;
        case Type_::LIST_LIST_FLOAT:
            list_list_float_value_.~vector();
            break;
        default:
            break;
    }
    type_ = Type_::INACTIVE;
}

void SettingValue::copy_value_from_(SettingValue const & other) {
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
        case Type_::LIST_INT:
            new (&list_int_value_) std::vector<int64_t>(other.list_int_value_);
            break;
        case Type_::LIST_FLOAT:
            new (&list_float_value_) std::vector<double>(other.list_float_value_);
            break;
        case Type_::LIST_LIST_FLOAT:
            new (&list_list_float_value_) std::vector<std::vector<double>>(
                    other.list_list_float_value_);
            break;
    }
}

void SettingValue::move_value_from_(SettingValue && other) {
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
        case Type_::LIST_INT:
            new (&list_int_value_) std::vector<int64_t>(std::move(other.list_int_value_));
            break;
        case Type_::LIST_FLOAT:
            new (&list_float_value_) std::vector<double>(std::move(other.list_float_value_));
            break;
        case Type_::LIST_LIST_FLOAT:
            new (&list_list_float_value_) std::vector<std::vector<double>>(std::move(other.list_list_float_value_));
            break;
    }
}

namespace {

template <typename T>
void write_vec(std::ostream & os, std::vector<T> const & val) {
    bool first = true;
    os << "[";
    for (T d : val) {
        if (!first)
            os << ", ";
        os << d;
        first = false;
    }
    os << "]";
}

}

std::ostream & operator<<(std::ostream & os, ymmsl::impl::SettingValue const & val) {
    if (val.is_a<std::string>())
        os << "\"" << val.as<std::string>() << "\"";
    else if (val.is_a<int64_t>())
        os << val.as<int64_t>();
    else if (val.is_a<double>())
        os << val.as<double>();
    else if (val.is_a<bool>())
        os << std::boolalpha << val.as<bool>();
    else if (val.is_a<std::vector<int64_t>>())
        write_vec(os, val.as<std::vector<int64_t>>());
    else if (val.is_a<std::vector<double>>())
        write_vec(os, val.as<std::vector<double>>());
    else if (val.is_a<std::vector<std::vector<double>>>()) {
        bool first = true;
        os << "[";
        for (auto const & vec : val.as<std::vector<std::vector<double>>>()) {
            if (!first)
                os << ", ";
            write_vec(os, vec);
            first = false;
        }
        os << "]";
    }
    return os;
}


Settings::Settings(std::initializer_list<MapType_::value_type> const & init)
    : store_(init)
{}

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

SettingValue const & Settings::at(Reference const & setting) const {
    return store_.at(setting);
}

SettingValue & Settings::operator[](Reference const & setting) {
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

std::ostream & operator<<(std::ostream & os, ymmsl::impl::Settings const & settings) {
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

} }

