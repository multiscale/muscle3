#include <iostream>
#include <ostream>


#include <memory>
#include <stdexcept>
#include <string>
#include <utility>

#include <msgpack.hpp>

#include "libmuscle/mcp/data.hpp"


namespace libmuscle {

namespace mcp {


DataConstRef::DataConstRef()
    : mp_zones_()
{
    mp_zones_.push_back(std::make_shared<msgpack::zone>());
    mp_obj_ = zone_alloc_<msgpack::object>();
    mp_obj_->type = msgpack::type::NIL;
}

DataConstRef::DataConstRef(bool value)
    : DataConstRef()
{
    *mp_obj_ << value;
}

DataConstRef::DataConstRef(char const * const value)
    : DataConstRef()
{
    *mp_obj_ << value;
}

DataConstRef::DataConstRef(std::string const & value)
    : DataConstRef()
{
    *mp_obj_ << value.c_str();
}

DataConstRef::DataConstRef(int value)
    : DataConstRef()
{
    *mp_obj_ << value;
}

DataConstRef::DataConstRef(long int value)
    : DataConstRef()
{
    *mp_obj_ << value;
}

DataConstRef::DataConstRef(long long int value)
    : DataConstRef()
{
    *mp_obj_ << value;
}

DataConstRef::DataConstRef(unsigned int value)
    : DataConstRef()
{
    *mp_obj_ << value;
}

DataConstRef::DataConstRef(unsigned long int value)
    : DataConstRef()
{
    *mp_obj_ << value;
}

DataConstRef::DataConstRef(unsigned long long int value)
    : DataConstRef()
{
    *mp_obj_ << value;
}

DataConstRef::DataConstRef(float value)
    : DataConstRef()
{
    *mp_obj_ << value;
}

DataConstRef::DataConstRef(double value)
    : DataConstRef()
{
    *mp_obj_ << value;
}

template <>
bool DataConstRef::is_a<bool>() const {
    return mp_obj_->type == msgpack::type::BOOLEAN;
}

template <>
bool DataConstRef::is_a<char>() const {
    return (mp_obj_->type == msgpack::type::POSITIVE_INTEGER ||
            mp_obj_->type == msgpack::type::NEGATIVE_INTEGER);
}

template <>
bool DataConstRef::is_a<short int>() const {
    return (mp_obj_->type == msgpack::type::POSITIVE_INTEGER ||
            mp_obj_->type == msgpack::type::NEGATIVE_INTEGER);
}

template <>
bool DataConstRef::is_a<int>() const {
    return (mp_obj_->type == msgpack::type::POSITIVE_INTEGER ||
            mp_obj_->type == msgpack::type::NEGATIVE_INTEGER);
}

template <>
bool DataConstRef::is_a<long int>() const {
    return (mp_obj_->type == msgpack::type::POSITIVE_INTEGER ||
            mp_obj_->type == msgpack::type::NEGATIVE_INTEGER);
}

template <>
bool DataConstRef::is_a<long long int>() const {
    return (mp_obj_->type == msgpack::type::POSITIVE_INTEGER ||
            mp_obj_->type == msgpack::type::NEGATIVE_INTEGER);
}

template <>
bool DataConstRef::is_a<unsigned char>() const {
    return mp_obj_->type == msgpack::type::POSITIVE_INTEGER;
}

template <>
bool DataConstRef::is_a<unsigned short int>() const {
    return mp_obj_->type == msgpack::type::POSITIVE_INTEGER;
}

template <>
bool DataConstRef::is_a<unsigned int>() const {
    return mp_obj_->type == msgpack::type::POSITIVE_INTEGER;
}

template <>
bool DataConstRef::is_a<unsigned long int>() const {
    return mp_obj_->type == msgpack::type::POSITIVE_INTEGER;
}

template <>
bool DataConstRef::is_a<unsigned long long int>() const {
    return mp_obj_->type == msgpack::type::POSITIVE_INTEGER;
}

template <>
bool DataConstRef::is_a<float>() const {
    return mp_obj_->type == msgpack::type::FLOAT32;
}

template <>
bool DataConstRef::is_a<double>() const {
    return mp_obj_->type == msgpack::type::FLOAT64;
}

template <>
bool DataConstRef::is_a<std::string>() const {
    return mp_obj_->type == msgpack::type::STR;
}

bool DataConstRef::is_nil() const {
    return mp_obj_->type == msgpack::type::NIL;
}

bool DataConstRef::is_a_dict() const {
    return mp_obj_->type == msgpack::type::MAP;
}

bool DataConstRef::is_a_list() const {
    return mp_obj_->type == msgpack::type::ARRAY;
}

bool DataConstRef::is_a_byte_array() const {
    return mp_obj_->type == msgpack::type::BIN;
}

std::size_t DataConstRef::size() const {
    if (is_a_dict())
        return mp_obj_->via.map.size;
    else if (is_a_list())
        return mp_obj_->via.array.size;
    else if (is_a_byte_array())
        return mp_obj_->via.bin.size;
    else
        throw std::runtime_error("DataConstRef::size() called for an object that does"
                                 " not represent a list or dict");
}

char const * DataConstRef::as_byte_array() const {
    if (!is_a_byte_array())
        throw std::runtime_error("Tried to access as a byte array, but this is"
                                 " not a byte array.");
    return mp_obj_->via.bin.ptr;
}

DataConstRef DataConstRef::operator[](std::string const & key) const {
    if (mp_obj_->type == msgpack::type::MAP) {
        for (uint32_t i = 0; i < mp_obj_->via.map.size; ++i) {
            auto const & mkey = mp_obj_->via.map.ptr[i].key;
            if (mkey.type == msgpack::type::STR)
                if (mkey.via.str.size == key.size())
                    if (strncmp(mkey.via.str.ptr, key.data(), mkey.via.str.size) == 0)
                        return DataConstRef(&(mp_obj_->via.map.ptr[i].val), mp_zones_);
        }
        throw std::out_of_range("Key " + key + " not found in map.");
    }
    throw std::runtime_error("Tried to look up a key, but this object is not a map.");
}

DataConstRef DataConstRef::operator[](std::size_t index) const {
    if (mp_obj_->type == msgpack::type::ARRAY)
        if (index < mp_obj_->via.array.size)
            return DataConstRef(&(mp_obj_->via.array.ptr[index]), mp_zones_);
        else
            throw std::out_of_range("Array index out of range.");
    else
        throw std::runtime_error("Tried to index an object that is not a list.");
}

DataConstRef::DataConstRef(
        msgpack::object * obj,
        std::shared_ptr<msgpack::zone> const & zone)
    : mp_zones_()
    , mp_obj_(obj)
{
    mp_zones_.push_back(zone);
}

DataConstRef::DataConstRef(
        msgpack::object * obj,
        std::vector<std::shared_ptr<msgpack::zone>> const & zones)
    : mp_zones_(zones)
    , mp_obj_(obj)
{}

DataConstRef::DataConstRef(std::shared_ptr<msgpack::zone> const & zone)
    : mp_zones_({zone})
    , mp_obj_(zone_alloc_<msgpack::object>())
{
    mp_obj_->type = msgpack::type::NIL;
}

Data Data::dict() {
    Data dict;
    dict.init_dict_(0u);
    return dict;
}

Data Data::list() {
    Data list;
    list.init_list_(0u);
    return list;
}

Data Data::nils(std::size_t size) {
    Data list;
    list.init_list_(size);
    for (std::size_t i = 0u; i < size; ++i)
        list.mp_obj_->via.array.ptr[i].type = msgpack::type::NIL;
    return list;
}

Data Data::byte_array(char const * buf, uint32_t size) {
    Data bytes;
    bytes.mp_obj_->type = msgpack::type::BIN;
    bytes.mp_obj_->via.bin.size = size;
    bytes.mp_obj_->via.bin.ptr = buf;
    return bytes;
}

Data & Data::operator=(Data const & rhs) {
    if (mp_obj_ != rhs.mp_obj_) {
        *mp_obj_ = *rhs.mp_obj_;
        mp_zones_ = rhs.mp_zones_;
    }
    return *this;
}

Data Data::operator[](std::string const & key) {
    if (mp_obj_->type == msgpack::type::MAP) {
        for (uint32_t i = 0; i < mp_obj_->via.map.size; ++i) {
            auto const & mkey = mp_obj_->via.map.ptr[i].key;
            if (mkey.type == msgpack::type::STR)
                if (mkey.via.str.size == key.size())
                    if (strncmp(mkey.via.str.ptr, key.data(), mkey.via.str.size) == 0)
                        return Data(&(mp_obj_->via.map.ptr[i].val), mp_zones_);
        }

        // key is not in here, reallocate and add
        msgpack::object_kv * new_ptr = zone_alloc_<msgpack::object_kv>(mp_obj_->via.map.size + 1);
        for (uint32_t i = 0u; i < mp_obj_->via.map.size; ++i)
            new_ptr[i] = mp_obj_->via.map.ptr[i];
        mp_obj_->via.map.ptr = new_ptr;
        ++mp_obj_->via.map.size;

        // add new key
        auto & new_kv = mp_obj_->via.map.ptr[mp_obj_->via.map.size - 1];
        new_kv.key = msgpack::object(key, *mp_zones_[0]);
        new_kv.val = msgpack::object();
        return Data(&new_kv.val, mp_zones_);
    }
    throw std::runtime_error("Tried to look up a key, but this object is not a map.");
}

Data Data::operator[](std::size_t index) {
    if (mp_obj_->type == msgpack::type::ARRAY) {
        if (index < mp_obj_->via.array.size)
            return Data(&(mp_obj_->via.array.ptr[index]), mp_zones_);
        throw std::out_of_range("Tried to access index " + std::to_string(index)
                                + " on an array of size "
                                + std::to_string(mp_obj_->via.array.size));
    }
    throw std::runtime_error("Tried to index an object that is not a list.");
}

void Data::init_dict_(uint32_t size) {
    mp_obj_->type = msgpack::type::MAP;
    mp_obj_->via.map.size = size;
    mp_obj_->via.map.ptr = zone_alloc_<msgpack::object_kv>(size);
}

void Data::init_list_(uint32_t size) {
    mp_obj_->type = msgpack::type::ARRAY;
    mp_obj_->via.array.size = size;
    mp_obj_->via.array.ptr = zone_alloc_<msgpack::object>(size);
}

}   // namespace mcp

}   // namespace libmuscle

