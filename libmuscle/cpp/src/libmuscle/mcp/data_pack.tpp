// Template implementation, do not include directly!

#include <iostream>
#include <ostream>


namespace msgpack {

MSGPACK_API_VERSION_NAMESPACE(MSGPACK_DEFAULT_API_NS) {

namespace adaptor {

template<>
struct pack<::libmuscle::mcp::DataConstRef> {
    template <typename Stream>
    packer<Stream>& operator()(
            msgpack::packer<Stream>& o,
            ::libmuscle::mcp::DataConstRef const& v) const
    {
        o.pack(*v.mp_obj_);
        return o;
    }
};

template<>
struct pack<::libmuscle::mcp::Data> {
    template <typename Stream>
    packer<Stream>& operator()(
            msgpack::packer<Stream>& o,
            ::libmuscle::mcp::Data const& v) const
    {
        o.pack(*v.mp_obj_);
        return o;
    }
};

template <>
struct object_with_zone<::libmuscle::mcp::DataConstRef> {
    void operator()(
            msgpack::object::with_zone & obj,
            ::libmuscle::mcp::DataConstRef const & d) const
    {
        obj.type = d.mp_obj_->type;
        obj.via = d.mp_obj_->via;
    }
};

template <>
struct object_with_zone<::libmuscle::mcp::Data> {
    void operator()(
            msgpack::object::with_zone & obj,
            ::libmuscle::mcp::Data const & d) const
    {
        obj.type = d.mp_obj_->type;
        obj.via = d.mp_obj_->via;
    }
};

}   // namespace adaptor

}   // namespace MSGPACK_API_VERSION_NAMESPACE

}   // namespace msgpack

