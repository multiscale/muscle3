// Template implementation. Do not include directly!

#include <memory>
#include <stdexcept>
#include <string>
#include <utility>

#include <msgpack.hpp>


namespace libmuscle {

namespace mcp {


template <typename T>
bool DataConstRef::is_a() const {
    return false;
}

template <typename T>
T DataConstRef::as() const {
    if (!is_a<T>())
        throw std::runtime_error("Tried to convert a DataConstRef or Data to"
                " a type that does not match its value. Did you receive data"
                " of a type you were not expecting?");
    return mp_obj_->as<T>();
}

template <typename T>
T * DataConstRef::zone_alloc_(uint32_t size) {
    auto num_bytes = sizeof(T) * size;
    return static_cast<T*>(mp_zones_[0]->allocate_align(
                num_bytes, MSGPACK_ZONE_ALIGNOF(T)));
}

template <typename... Args>
Data Data::dict(Args const & ... args) {
    Data dict;
    dict.init_dict_(0u, args...);
    return dict;
}

template <typename... Args>
Data Data::list(Args const & ... args) {
    Data list;
    list.init_list_(0u, args...);
    return list;
}

template <typename... Args>
void Data::init_dict_(uint32_t offset, std::string const & key, DataConstRef const & value,
                Args const & ... args)
{
    init_dict_(offset + 1, args...);
    mp_obj_->via.map.ptr[offset].key = msgpack::object(key, *mp_zones_[0]);
    mp_obj_->via.map.ptr[offset].val = msgpack::object(value, *mp_zones_[0]);
    mp_zones_.insert(mp_zones_.end(), value.mp_zones_.cbegin(), value.mp_zones_.cend());
}

template <typename... Args>
void Data::init_dict_(uint32_t offset, std::string const & key, Data const & value,
                Args const & ... args)
{
    init_dict_(offset + 1, args...);
    mp_obj_->via.map.ptr[offset].key = msgpack::object(key, *mp_zones_[0]);
    mp_obj_->via.map.ptr[offset].val = msgpack::object(value, *mp_zones_[0]);
    mp_zones_.insert(mp_zones_.end(), value.mp_zones_.cbegin(), value.mp_zones_.cend());
}

template <typename Arg, typename... Args>
void Data::init_dict_(uint32_t offset, std::string const & key, Arg const & value,
                Args const & ... args)
{
    init_dict_(offset + 1, args...);
    mp_obj_->via.map.ptr[offset].key = msgpack::object(key, *mp_zones_[0]);
    mp_obj_->via.map.ptr[offset].val = msgpack::object(value, *mp_zones_[0]);
}

template <typename... Args>
void Data::init_list_(uint32_t offset, DataConstRef const & value,
                      Args const &...args) {
    init_list_(offset + 1, args...);
    mp_obj_->via.array.ptr[offset] = msgpack::object(value, *mp_zones_[0]);
    mp_zones_.insert(mp_zones_.end(), value.mp_zones_.cbegin(), value.mp_zones_.cend());
}

template <typename... Args>
void Data::init_list_(uint32_t offset, Data const & value,
                      Args const &...args) {
    init_list_(offset + 1, args...);
    mp_obj_->via.array.ptr[offset] = msgpack::object(value, *mp_zones_[0]);
    mp_zones_.insert(mp_zones_.end(), value.mp_zones_.cbegin(), value.mp_zones_.cend());
}

template <typename Arg, typename... Args>
void Data::init_list_(uint32_t offset, Arg const & value,
                      Args const &...args) {
    init_list_(offset + 1, args...);
    mp_obj_->via.array.ptr[offset] = msgpack::object(value, *mp_zones_[0]);
}

}   // namespace mcp

}   // namespace libmuscle

