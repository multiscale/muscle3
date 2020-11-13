#include <cstring>
#include <functional>
#include <memory>
#include <numeric>
#include <stdexcept>
#include <string>
#include <utility>

#include <msgpack.hpp>

#include "libmuscle/data.hpp"
#include "libmuscle/mcp/data_pack.hpp"
#include "libmuscle/mcp/ext_types.hpp"
#include "ymmsl/identity.hpp"
#include "ymmsl/settings.hpp"

using libmuscle::impl::mcp::ExtTypeId;
using ymmsl::SettingValue;
using ymmsl::Reference;
using ymmsl::Settings;


namespace libmuscle { namespace impl {

// helper functions

template <typename Element>
ExtTypeId grid_type_id_();

template <>
ExtTypeId grid_type_id_<std::int32_t>() {
    return ExtTypeId::grid_int32;
}

template <>
ExtTypeId grid_type_id_<std::int64_t>() {
    return ExtTypeId::grid_int64;
}

template <>
ExtTypeId grid_type_id_<float>() {
    return ExtTypeId::grid_float32;
}

template <>
ExtTypeId grid_type_id_<double>() {
    return ExtTypeId::grid_float64;
}

template <>
ExtTypeId grid_type_id_<bool>() {
    return ExtTypeId::grid_bool;
}

template <typename Element>
std::string grid_type_name_();

template <>
std::string grid_type_name_<std::int32_t>() {
    return "int32";
}

template <>
std::string grid_type_name_<std::int64_t>() {
    return "int64";
}

template <>
std::string grid_type_name_<float>() {
    return "float32";
}

template <>
std::string grid_type_name_<double>() {
    return "float64";
}

template <>
std::string grid_type_name_<bool>() {
    return "bool";
}

template <typename Element>
DataConstRef DataConstRef::grid_data_(
        Element const * const data, std::size_t num_elems
) const {
    return Data::byte_array(
        reinterpret_cast<char const *>(data), num_elems * sizeof(Element));
}

template <>
DataConstRef DataConstRef::grid_data_<bool>(
        bool const * const data, std::size_t num_elems) const;

// implementation

DataConstRef::DataConstRef()
    : mp_zones_(new std::vector<std::shared_ptr<msgpack::zone>>())
{
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

/* This is here in the .cpp and instantiated explicitly, because it requires the
 * ExtTypeId, and we don't want to have that in a public header since it's a
 * detail of an internal format.
 */
template <typename Element>
DataConstRef DataConstRef::grid(
        Element const * const data,
        std::vector<std::size_t> const & shape,
        std::vector<std::string> const & indexes,
        StorageOrder storage_order
) {
    if (shape.size() != indexes.size() && !indexes.empty())
        throw std::runtime_error("Shape and indexes must have the same length");

    auto grid_dict = Data::dict();
    // type member is redundant, but useful metadata
    grid_dict["type"] = grid_type_name_<Element>();
    mcp::ExtTypeId ext_type_id = grid_type_id_<Element>();

    Data shape_list = Data::nils(shape.size());
    for (std::size_t i = 0u; i < shape.size(); ++i)
        shape_list[i] = shape[i];
    grid_dict["shape"] = shape_list;

    if (storage_order == StorageOrder::first_adjacent)
        grid_dict["order"] = "fa";
    else
        grid_dict["order"] = "la";

    std::size_t num_elems = std::accumulate(
        shape.cbegin(), shape.cend(), 1u,
        std::multiplies<std::size_t>());
    grid_dict["data"] = Data::byte_array(
        reinterpret_cast<char const *>(data), num_elems * sizeof(Element));

    if (!indexes.empty()) {
        Data indexes_list = Data::nils(indexes.size());
        for (std::size_t i = 0u; i < indexes.size(); ++i)
            indexes_list[i] = indexes[i];
        grid_dict["indexes"] = indexes_list;
    }
    else {
        grid_dict["indexes"] = Data();
    }

    return DataConstRef(static_cast<char>(ext_type_id), grid_dict);
}

#ifndef DOXYGEN_SHOULD_SKIP_THIS

template DataConstRef DataConstRef::grid<std::int32_t>(
        std::int32_t const * const data,
        std::vector<std::size_t> const & shape,
        std::vector<std::string> const & indexes,
        StorageOrder storage_order);

template DataConstRef DataConstRef::grid<std::int64_t>(
        std::int64_t const * const data,
        std::vector<std::size_t> const & shape,
        std::vector<std::string> const & indexes,
        StorageOrder storage_order);

template DataConstRef DataConstRef::grid<float>(
        float const * const data,
        std::vector<std::size_t> const & shape,
        std::vector<std::string> const & indexes,
        StorageOrder storage_order);

template DataConstRef DataConstRef::grid<double>(
        double const * const data,
        std::vector<std::size_t> const & shape,
        std::vector<std::string> const & indexes,
        StorageOrder storage_order);

template DataConstRef DataConstRef::grid<bool>(
        bool const * const data,
        std::vector<std::size_t> const & shape,
        std::vector<std::string> const & indexes,
        StorageOrder storage_order);

#endif

DataConstRef::DataConstRef(SettingValue const & value)
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
    obj_cache_ = target.obj_cache_;
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

template <typename Element>
bool DataConstRef::is_a_grid_of() const {
    if (mp_obj_->type != msgpack::type::EXT)
        return false;

    auto ext_type = static_cast<mcp::ExtTypeId>(mp_obj_->via.ext.type());
    return ext_type == grid_type_id_<Element>();
}

#ifndef DOXYGEN_SHOULD_SKIP_THIS

template bool DataConstRef::is_a_grid_of<std::int32_t>() const;

template bool DataConstRef::is_a_grid_of<std::int64_t>() const;

template bool DataConstRef::is_a_grid_of<float>() const;

template bool DataConstRef::is_a_grid_of<double>() const;

template bool DataConstRef::is_a_grid_of<bool>() const;

#endif

bool DataConstRef::is_a_byte_array() const {
    return mp_obj_->type == msgpack::type::BIN;
}

template <>
SettingValue DataConstRef::as<SettingValue>() const {
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
                            " SettingValue.");
            }
            return result;
        }
        else
            throw std::runtime_error("Found a list of something else than"
                    " lists, which I cannot convert to a SettingValue.");
    }
    else
        throw std::runtime_error("Tried to convert a DataConstRef or Data to"
                " a SettingValue, which it isn't. Did you receive data of a"
                " type you were not expecting?");
}

// This uses as<SettingValue>, so has to be below it.
template <>
bool DataConstRef::is_a<SettingValue>() const {
    if (is_a<std::string>() ||
            is_a<int64_t>() ||
            is_a<double>() ||
            is_a<bool>())
        return true;
    // cheat, just try to convert and catch the exception
    // TODO: neater solution
    try {
        as<SettingValue>();
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
        Reference key(settings_dict.key(i));
        auto val = settings_dict.value(i).as<SettingValue>();
        settings[key] = val;
    }
    return settings;
}

std::size_t DataConstRef::size() const {
    if (is_a_dict())
        return mp_obj_->via.map.size;
    else if (is_a_list())
        return mp_obj_->via.array.size;
    else if (is_a_grid_()) {
        auto shape_vec = shape();
        return std::accumulate(
            shape_vec.cbegin(), shape_vec.cend(), 1u,
            std::multiplies<std::size_t>());
    }
    else if (is_a_byte_array())
        return mp_obj_->via.bin.size;
    else
        throw std::runtime_error("DataConstRef::size() called for an object that does"
                                 " not represent a list, dict, grid or byte array");
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

std::string DataConstRef::key(std::size_t i) const {
    if (mp_obj_->type == msgpack::type::MAP) {
        if (i < size())
            return DataConstRef(&(mp_obj_->via.map.ptr[i].key), mp_zones_).as<std::string>();
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

template <typename Element>
Element const * DataConstRef::elements() const {
    if (!is_a_grid_of<Element>())
        throw std::runtime_error(
                "Tried to get grid data, but this object is not a grid or"
                " not of the correct type.");
    char const * data_bytes = grid_dict_()["data"].as_byte_array();
    return reinterpret_cast<Element const *>(data_bytes);
}

#ifndef DOXYGEN_SHOULD_SKIP_THIS

template bool const * DataConstRef::elements<bool>() const;

template double const * DataConstRef::elements<double>() const;

template float const * DataConstRef::elements<float>() const;

template int const * DataConstRef::elements<int>() const;

template long const * DataConstRef::elements<long>() const;

#endif

std::vector<std::size_t> DataConstRef::shape() const {
    if (is_a_grid_()) {
        DataConstRef shape_list = grid_dict_()["shape"];
        std::vector<std::size_t> result(shape_list.size());
        for (std::size_t i = 0u; i < shape_list.size(); ++i)
            result[i] = shape_list[i].as<std::size_t>();
        return result;
    }
    else
        throw std::runtime_error("Tried to get the shape, but this object is not a grid.");
}

StorageOrder DataConstRef::storage_order() const {
    if (is_a_grid_()) {
        std::string const & order = grid_dict_()["order"].as<std::string>();
        if (order == "fa")
            return StorageOrder::first_adjacent;
        else if (order == "la")
            return StorageOrder::last_adjacent;
        throw std::runtime_error("Invalid data format received, MUSCLE 3 bug?");
    }
    else
        throw std::runtime_error("Tried to get the shape, but this object is not a grid.");
}

bool DataConstRef::has_indexes() const {
    if (is_a_grid_())
        return !grid_dict_()["indexes"].is_nil();
    else
        throw std::runtime_error("Tried to check for indexes, but this object is not a grid.");
}

std::vector<std::string> DataConstRef::indexes() const {
    if (has_indexes()) {
        DataConstRef indexes = grid_dict_()["indexes"];
        std::vector<std::string> result(indexes.size());
        for (std::size_t i = 0u; i < indexes.size(); ++i)
            result[i] = indexes[i].as<std::string>();
        return result;
    }
    else
        throw std::runtime_error("Tried to get indexes, but this grid does not have any.");
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

DataConstRef::DataConstRef(char ext_type_id, DataConstRef const & data)
    : DataConstRef()
{
    msgpack::sbuffer buf;
    msgpack::pack(buf, data);

    char * zoned_mem = zone_alloc_<char>(buf.size() + 1);
    zoned_mem[0] = ext_type_id;
    memcpy(zoned_mem + 1, buf.data(), buf.size());
    *mp_obj_ << msgpack::type::ext_ref(zoned_mem, buf.size() + 1);
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

bool DataConstRef::is_a_grid_() const {
    if (mp_obj_->type != msgpack::type::EXT)
        return false;

    auto ext_type = static_cast<mcp::ExtTypeId>(mp_obj_->via.ext.type());
    return (ext_type == mcp::ExtTypeId::grid_int32)
        || (ext_type == mcp::ExtTypeId::grid_int64)
        || (ext_type == mcp::ExtTypeId::grid_float32)
        || (ext_type == mcp::ExtTypeId::grid_float64)
        || (ext_type == mcp::ExtTypeId::grid_bool);
}

DataConstRef DataConstRef::grid_dict_() const {
    auto ext = mp_obj_->as<msgpack::type::ext>();
    auto oh = msgpack::unpack(ext.data(), ext.size());

    if (oh.get().type != msgpack::type::MAP)
        throw std::runtime_error("Invalid grid format. Bug in MUSCLE 3?");

    if (!obj_cache_)
        obj_cache_ = std::make_shared<DataConstRef>(
                mcp::unpack_data(mp_zones_->at(0), ext.data(), ext.size()));
    return *obj_cache_;
}

/* This is here in the .cpp and instantiated explicitly, because it requires the
 * ExtTypeId, and we don't want to have that in a public header since it's a
 * detail of an internal format.
 */
template <typename Element>
Data Data::grid(
        Element const * const data,
        std::vector<std::size_t> const & shape,
        std::vector<std::string> const & indexes,
        StorageOrder storage_order
) {
    if (shape.size() != indexes.size() && !indexes.empty())
        throw std::runtime_error("Shape and indexes must have the same length");

    auto grid_dict = Data::dict();
    // type member is redundant, but useful metadata
    grid_dict["type"] = grid_type_name_<Element>();
    mcp::ExtTypeId ext_type_id = grid_type_id_<Element>();

    Data shape_list = Data::nils(shape.size());
    for (std::size_t i = 0u; i < shape.size(); ++i)
        shape_list[i] = shape[i];
    grid_dict["shape"] = shape_list;

    if (storage_order == StorageOrder::first_adjacent)
        grid_dict["order"] = "fa";
    else
        grid_dict["order"] = "la";

    std::size_t num_elems = std::accumulate(
        shape.cbegin(), shape.cend(), 1u,
        std::multiplies<std::size_t>());
    grid_dict["data"] = Data::byte_array(
        reinterpret_cast<char const *>(data), num_elems * sizeof(Element));

    if (!indexes.empty()) {
        Data indexes_list = Data::nils(indexes.size());
        for (std::size_t i = 0u; i < indexes.size(); ++i)
            indexes_list[i] = indexes[i];
        grid_dict["indexes"] = indexes_list;
    }
    else {
        grid_dict["indexes"] = Data();
    }

    return Data(static_cast<char>(ext_type_id), grid_dict);
}

#ifndef DOXYGEN_SHOULD_SKIP_THIS

template Data Data::grid<std::int32_t>(
        std::int32_t const * const data,
        std::vector<std::size_t> const & shape,
        std::vector<std::string> const & indexes,
        StorageOrder storage_order);

template Data Data::grid<std::int64_t>(
        std::int64_t const * const data,
        std::vector<std::size_t> const & shape,
        std::vector<std::string> const & indexes,
        StorageOrder storage_order);

template Data Data::grid<float>(
        float const * const data,
        std::vector<std::size_t> const & shape,
        std::vector<std::string> const & indexes,
        StorageOrder storage_order);

template Data Data::grid<double>(
        double const * const data,
        std::vector<std::size_t> const & shape,
        std::vector<std::string> const & indexes,
        StorageOrder storage_order);

template Data Data::grid<bool>(
        bool const * const data,
        std::vector<std::size_t> const & shape,
        std::vector<std::string> const & indexes,
        StorageOrder storage_order);

#endif

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

Data Data::byte_array(uint32_t size) {
    Data bytes;
    bytes.mp_obj_->type = msgpack::type::BIN;
    bytes.mp_obj_->via.bin.size = size;
    bytes.mp_obj_->via.bin.ptr = bytes.zone_alloc_<char>(size);
    return bytes;
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
        obj_cache_ = rhs.obj_cache_;

        if (
                rhs.mp_obj_->type == msgpack::type::STR ||
                rhs.mp_obj_->type == msgpack::type::BIN ||
                rhs.mp_obj_->type == msgpack::type::ARRAY ||
                rhs.mp_obj_->type == msgpack::type::MAP ||
                rhs.mp_obj_->type == msgpack::type::EXT)
        {
            // The above assignment will only copy the pointer for these
            // types. So we need to add the source zones to our own to
            // ensure that the data structure pointed to by thet pointer
            // continues to exist for as long as we do.
            if (mp_zones_ != rhs.mp_zones_)
                mp_zones_->insert(mp_zones_->end(),
                        rhs.mp_zones_->cbegin(), rhs.mp_zones_->cend());
        }
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

Data Data::value(std::size_t i) const {
    if (mp_obj_->type == msgpack::type::MAP) {
        if (i < size())
            return Data(&(mp_obj_->via.map.ptr[i].val), mp_zones_);
        else
            throw std::out_of_range("Index too large for this map.");
    }
    throw std::runtime_error("Tried to look up a value, but this object is not a map.");
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

char * Data::as_byte_array() {
    if (!is_a_byte_array())
        throw std::runtime_error("Tried to access as a byte array, but this is"
                                 " not a byte array.");
    // MessagePack defines this const, probably because it doesn't need to
    // modify the data. We use this for our own purposes however, and need to
    // be able to write data into the buffer. So we cast the const away.
    return const_cast<char *>(mp_obj_->via.bin.ptr);
}

void Data::set_dict_item_(
        uint32_t offset, std::string const & key, DataConstRef const & value
) {
    mp_obj_->via.map.ptr[offset].key = msgpack::object(key, *mp_zones_->front());
    mp_obj_->via.map.ptr[offset].val = msgpack::object(value, *mp_zones_->front());
    mp_zones_->insert(mp_zones_->end(), value.mp_zones_->cbegin(), value.mp_zones_->cend());
}

void Data::set_dict_item_(
        uint32_t offset, std::string const & key, Data const & value
) {
    mp_obj_->via.map.ptr[offset].key = msgpack::object(key, *mp_zones_->front());
    mp_obj_->via.map.ptr[offset].val = msgpack::object(value, *mp_zones_->front());
    mp_zones_->insert(mp_zones_->end(), value.mp_zones_->cbegin(), value.mp_zones_->cend());
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

template <>
DataConstRef DataConstRef::grid_data_<bool>(
        bool const * const data, std::size_t num_elems
) const {
    if (sizeof(bool) == 1u)
        return Data::byte_array(
            reinterpret_cast<char const *>(data), num_elems);
    else {
        Data result = Data::byte_array(num_elems);
        char * data_copy = result.as_byte_array();
        std::copy(data, data + num_elems, data_copy);
        return result;
    }
}

} }  // namespace libmuscle::impl

