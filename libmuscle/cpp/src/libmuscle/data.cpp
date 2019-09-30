#include <cstring>
#include <memory>
#include <stdexcept>
#include <string>
#include <utility>

#include <msgpack.hpp>

#include "libmuscle/data.hpp"
#include "libmuscle/mcp/data_pack.hpp"
#include "libmuscle/mcp/ext_types.hpp"
#include "ymmsl/identity.hpp"
#include "ymmsl/settings.hpp"

using libmuscle::mcp::ExtTypeId;
using ymmsl::ParameterValue;
using ymmsl::Reference;
using ymmsl::Settings;


namespace libmuscle {

DataConstRef::DataConstRef()
    : mp_zones_(new std::vector<std::shared_ptr<msgpack::zone>>())
{
    mp_zones_->push_back(std::make_shared<msgpack::zone>());
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
    char * buf = zone_alloc_<char>(strlen(value) + 1);
    strcpy(buf, value);
    *mp_obj_ << buf;
}

DataConstRef::DataConstRef(std::string const & value)
    : DataConstRef()
{
    char * buf = zone_alloc_<char>(value.length() + 1);
    strncpy(buf, value.c_str(), value.length() + 1);
    *mp_obj_ << buf;
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

DataConstRef::DataConstRef(ParameterValue const & value)
    : DataConstRef()
{
    if (value.is_a<std::string>()) {
        std::string val_str = value.as<std::string>();
        char * buf = zone_alloc_<char>(val_str.length() + 1);
        strncpy(buf, val_str.c_str(), val_str.length() + 1);
        *mp_obj_ << buf;
    }
    else if (value.is_a<int64_t>())
        *mp_obj_ << value.as<int64_t>();
    else if (value.is_a<double>())
        *mp_obj_ << value.as<double>();
    else if (value.is_a<bool>())
        *mp_obj_ << value.as<bool>();
    else if (value.is_a<std::vector<double>>()) {
        auto vec = value.as<std::vector<double>>();
        auto list = Data::nils(vec.size());
        for (std::size_t i = 0u; i < vec.size(); ++i)
            list[i] = vec[i];
        std::swap(list.mp_obj_, mp_obj_);
        std::swap(list.mp_zones_, mp_zones_);
    }
    else if (value.is_a<std::vector<std::vector<double>>>()) {
        auto vec = value.as<std::vector<std::vector<double>>>();
        auto list = Data::nils(vec.size());
        for (std::size_t i = 0u; i < vec.size(); ++i) {
            auto list2 = Data::nils(vec[i].size());
            for (std::size_t j = 0u; j < vec[i].size(); ++j)
                list2[j] = vec[i][j];
            list[i] = list2;
        }
        std::swap(list.mp_obj_, mp_obj_);
        std::swap(list.mp_zones_, mp_zones_);
    }
}

DataConstRef::DataConstRef(Settings const & settings)
    : DataConstRef()
{
    auto settings_dict = Data::dict();
    for (auto const & kv_pair: settings)
        settings_dict[static_cast<std::string>(kv_pair.first)] = kv_pair.second;

    msgpack::sbuffer buf;
    msgpack::pack(buf, settings_dict);

    char * zoned_mem = zone_alloc_<char>(buf.size() + 1);
    zoned_mem[0] = static_cast<char>(ExtTypeId::settings);
    memcpy(zoned_mem + 1, buf.data(), buf.size());
    *mp_obj_ << msgpack::type::ext_ref(zoned_mem, buf.size() + 1);
}

void DataConstRef::reseat(DataConstRef const & target) {
    mp_zones_ = target.mp_zones_;
    mp_obj_ = target.mp_obj_;
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
bool DataConstRef::is_a<Settings>() const {
    return (mp_obj_->type == msgpack::type::EXT) &&
        (mp_obj_->via.ext.type() == static_cast<int8_t>(ExtTypeId::settings));
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

template <>
ParameterValue DataConstRef::as<ParameterValue>() const {
    DataConstRef const & self = *this;
    if (is_a<std::string>())
        return as<std::string>();
    else if (is_a<int64_t>())
        return as<int64_t>();
    else if (is_a<double>())
        return as<double>();
    else if (is_a<bool>())
        return as<bool>();
    else if (is_a_list()) {
        if (size() == 0u)
            return std::vector<double>();
        else if (self[0].is_a<double>())
            return as_vec_double_();
        else if (self[0].is_a_list()) {
            std::vector<std::vector<double>> result;
            for (std::size_t i = 0u; i < size(); ++i) {
                if (self[i].is_a_list())
                    result.push_back(self[i].as_vec_double_());
                else
                    throw std::runtime_error("Found a list of something else"
                            " than lists, which I cannot convert to a"
                            " ParameterValue.");
            }
            return result;
        }
        else
            throw std::runtime_error("Found a list of something else than"
                    " lists, which I cannot convert to a ParameterValue.");
    }
    else
        throw std::runtime_error("Tried to convert a DataConstRef or Data to"
                " a ParameterValue, which it isn't. Did you receive data of a"
                " type you were not expecting?");
}

// This uses as<ParameterValue>, so has to be below it.
template <>
bool DataConstRef::is_a<ParameterValue>() const {
    if (is_a<std::string>() ||
            is_a<int64_t>() ||
            is_a<double>() ||
            is_a<bool>())
        return true;
    // cheat, just try to convert and catch the exception
    // TODO: neater solution
    try {
        as<ParameterValue>();
    }
    catch (std::runtime_error const & e) {
        return false;
    }
    return true;
}

template <>
Settings DataConstRef::as<Settings>() const {
    if (!is_a<Settings>())
        throw std::runtime_error("Tried to convert a DataConstRef or Data to"
                " a Settings, which it isn't. Did you receive data of a type"
                " you were not expecting?");

    auto ext = mp_obj_->as<msgpack::type::ext>();
    auto oh = msgpack::unpack(ext.data(), ext.size());

    if (oh.get().type != msgpack::type::MAP)
        throw std::runtime_error("Invalid Settings format. Bug in MUSCLE 3?");

    Settings settings;
    auto zone = std::make_shared<msgpack::zone>();
    Data settings_dict(mcp::unpack_data(zone, ext.data(), ext.size()));

    for (std::size_t i = 0u; i < settings_dict.size(); ++i) {
        Reference key(settings_dict.key(i).as<std::string>());
        auto val = settings_dict.value(i).as<ParameterValue>();
        settings[key] = val;
    }
    return settings;
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

DataConstRef DataConstRef::key(std::size_t i) const {
    if (mp_obj_->type == msgpack::type::MAP) {
        if (i < size())
            return DataConstRef(&(mp_obj_->via.map.ptr[i].key), mp_zones_);
        else
            throw std::out_of_range("Index too large for this map.");
    }
    throw std::runtime_error("Tried to look up a key, but this object is not a map.");
}

DataConstRef DataConstRef::value(std::size_t i) const {
    if (mp_obj_->type == msgpack::type::MAP) {
        if (i < size())
            return DataConstRef(&(mp_obj_->via.map.ptr[i].val), mp_zones_);
        else
            throw std::out_of_range("Index too large for this map.");
    }
    throw std::runtime_error("Tried to look up a value, but this object is not a map.");
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
    : mp_zones_(new std::vector<std::shared_ptr<msgpack::zone>>())
    , mp_obj_(obj)
{
    mp_zones_->push_back(zone);
}

DataConstRef::DataConstRef(
        msgpack::object * obj,
        Zones_ const & zones)
    : mp_zones_(zones)
    , mp_obj_(obj)
{}

DataConstRef::DataConstRef(std::shared_ptr<msgpack::zone> const & zone)
    : mp_zones_(new std::vector<std::shared_ptr<msgpack::zone>>{zone})
    , mp_obj_(zone_alloc_<msgpack::object>())
{
    mp_obj_->type = msgpack::type::NIL;
}

std::vector<double> DataConstRef::as_vec_double_() const {
    std::vector<double> result;
    DataConstRef const & self = *this;
    for (std::size_t i = 0u; i < size(); ++i) {
        if (self[i].is_a<double>())
            result.push_back(self[i].as<double>());
        else
            throw std::runtime_error("Found a list containing"
                    " something else than a double.");
    }
    return result;
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

        // We can't overwrite mp_zones_ here, because mp_obj_ is allocated on
        // one of them, and we don't know which. So we just append, which is
        // suboptimal because it may keep objects alive that are no longer
        // reachable. Consider a separate shared_ptr to the zone that mp_obj_
        // is on (in a separate member), so that we can safely overwrite
        // mp_zones_.
        if (mp_zones_ != rhs.mp_zones_)
            mp_zones_->insert(mp_zones_->end(),
                    rhs.mp_zones_->cbegin(), rhs.mp_zones_->cend());
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
        new_kv.key = msgpack::object(key, *mp_zones_->front());
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

}   // namespace libmuscle

