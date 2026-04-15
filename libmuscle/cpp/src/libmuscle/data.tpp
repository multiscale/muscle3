// Template implementation. Do not include directly!

#include <cstdint>
#include <memory>
#include <stdexcept>
#include <string>
#include <utility>

#include <ymmsl/ymmsl.hpp>


namespace libmuscle { namespace _MUSCLE_IMPL_NS {

template <bool B>
void constness_static_assert_() {
    // Helper function to get GCC to produce a backtrace telling the user
    // where their error is. Putting this inline somehow removes the backtrace.
    static_assert(B,
        "Putting a DataConstRef into a Data::dict is not allowed,"
        " because it could allow modifying e.g. a list in the DataConstRef via"
        " the created Data object. Please use DataConstRef::dict() instead");
}

template <typename... Args>
DataConstRef DataConstRef::dict(Args const & ... args) {
    DataConstRef dict;
    dict.init_dict_(0u, args...);
    return dict;
}

template <typename... Args>
DataConstRef DataConstRef::list(Args const & ... args) {
    DataConstRef list;
    list.init_list_(0u, args...);
    return list;
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

template <>
struct DataConstRef::si_arg_type_<DataConstRef> {
    using type = DataConstRef const &;
};

template <>
struct DataConstRef::si_arg_type_<Data> {
    using type = Data const &;
};

template <>
struct DataConstRef::si_arg_type_<std::string> {
    using type = std::string const &;
};

template <typename T>
struct DataConstRef::si_arg_type_ {
    using type = T;
};

template <typename... Args>
void DataConstRef::init_dict_(
        uint32_t offset, std::string const & key, DataConstRef const & value,
        Args const & ... args)
{
    init_dict_(offset + 1, args...);
    set_dict_item_<DataConstRef>(offset, key, value);
    mp_zones_->insert(mp_zones_->end(), value.mp_zones_->cbegin(), value.mp_zones_->cend());
}

template <typename... Args>
void DataConstRef::init_dict_(
        uint32_t offset, std::string const & key, Data const & value,
        Args const & ... args)
{
    init_dict_(offset + 1, args...);
    set_dict_item_<Data>(offset, key, value);
    mp_zones_->insert(mp_zones_->end(), value.mp_zones_->cbegin(), value.mp_zones_->cend());
}

template <typename... Args>
void DataConstRef::init_dict_(
        uint32_t offset, std::string const & key, char const * value,
        Args const & ... args)
{
    init_dict_(offset + 1, args...);
    set_dict_item_<char const *>(offset, key, value);
}

template <typename Arg, typename... Args>
void DataConstRef::init_dict_(
        uint32_t offset, std::string const & key, Arg const & value,
        Args const & ... args)
{
    init_dict_(offset + 1, args...);
    set_dict_item_<Arg>(offset, key, value);
}

template <typename... Args>
void DataConstRef::init_list_(
        uint32_t offset, DataConstRef const & value, Args const &...args) {
    init_list_(offset + 1, args...);
    set_list_item_<DataConstRef>(offset, value);
    mp_zones_->insert(mp_zones_->end(), value.mp_zones_->cbegin(), value.mp_zones_->cend());
}

template <typename... Args>
void DataConstRef::init_list_(
        uint32_t offset, Data const & value, Args const &...args) {
    init_list_(offset + 1, args...);
    set_list_item_<DataConstRef>(offset, value);
    mp_zones_->insert(mp_zones_->end(), value.mp_zones_->cbegin(), value.mp_zones_->cend());
}

template <typename... Args>
void DataConstRef::init_list_(
        uint32_t offset, char const * value, Args const &...args) {
    init_list_(offset + 1, args...);
    set_list_item_<char const *>(offset, value);
}

template <typename Arg, typename... Args>
void DataConstRef::init_list_(
        uint32_t offset, Arg const & value, Args const &...args) {
    init_list_(offset + 1, args...);
    set_list_item_<Arg>(offset, value);
}

/* Note that we access value's mp_zones_ member here. mp_zones_ is protected,
 * but we're not accessing it through a this-pointer, so that is illegal
 * without a friend declaration. In order to make this exact function template
 * a friend, we need to have Data defined before DataConstRef, but that's
 * impossible because it's derived from DataConstRef, and so needs a definition
 * of DataConstRef available. The solution is to just make Data as a whole a
 * friend of DataConstRef. It's already derived from it, so that doesn't
 * change much beyond making this work.
*/
template <typename... Args>
void Data::init_dict_(uint32_t offset, std::string const & key, DataConstRef const & value,
                Args const & ... args)
{
    constness_static_assert_<false>();
}

template <typename... Args>
void Data::init_dict_(uint32_t offset, std::string const & key, Data const & value,
                Args const & ... args)
{
    init_dict_(offset + 1, args...);
    set_dict_item_<Data>(offset, key, value);
    mp_zones_->insert(mp_zones_->end(), value.mp_zones_->cbegin(), value.mp_zones_->cend());
}

template <typename... Args>
void Data::init_dict_(uint32_t offset, std::string const & key, char const * value,
                Args const & ... args)
{
    init_dict_(offset + 1, args...);
    set_dict_item_<char const *>(offset, key, value);
}

template <typename Arg, typename... Args>
void Data::init_dict_(uint32_t offset, std::string const & key, Arg const & value,
                Args const & ... args)
{
    init_dict_(offset + 1, args...);
    set_dict_item_<Arg>(offset, key, value);
}

template <typename... Args>
void Data::init_list_(uint32_t offset, DataConstRef const & value,
                      Args const &...args) {
    constness_static_assert_<false>();
}

template <typename... Args>
void Data::init_list_(uint32_t offset, Data const & value,
                      Args const &...args) {
    init_list_(offset + 1, args...);
    set_list_item_<Data>(offset, value);
    mp_zones_->insert(mp_zones_->end(), value.mp_zones_->cbegin(), value.mp_zones_->cend());
}

template <typename... Args>
void Data::init_list_(uint32_t offset, char const * value,
                      Args const &...args) {
    init_list_(offset + 1, args...);
    set_list_item_<char const *>(offset, value);
}

template <typename Arg, typename... Args>
void Data::init_list_(uint32_t offset, Arg const & value,
                      Args const &...args) {
    init_list_(offset + 1, args...);
    set_list_item_<Arg>(offset, value);
}

} }   // namespace libmuscle::_MUSCLE_IMPL_NS

