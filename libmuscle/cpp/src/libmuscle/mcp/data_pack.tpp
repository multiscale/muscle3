// Template implementation, do not include directly!


namespace msgpack {

MSGPACK_API_VERSION_NAMESPACE(MSGPACK_DEFAULT_API_NS) {

namespace adaptor {

template<>
struct pack<::libmuscle::impl::DataConstRef> {
    template <typename Stream>
    packer<Stream>& operator()(
            msgpack::packer<Stream>& o,
            ::libmuscle::impl::DataConstRef const& v) const
    {
        o.pack(*v.mp_obj_);
        return o;
    }
};

template<>
struct pack<::libmuscle::impl::Data> {
    template <typename Stream>
    packer<Stream>& operator()(
            msgpack::packer<Stream>& o,
            ::libmuscle::impl::Data const& v) const
    {
        o.pack(*v.mp_obj_);
        return o;
    }
};

template <>
struct object_with_zone<::libmuscle::impl::DataConstRef> {
    void operator()(
            msgpack::object::with_zone & obj,
            ::libmuscle::impl::DataConstRef const & d) const
    {
        obj.type = d.mp_obj_->type;
        obj.via = d.mp_obj_->via;
    }
};

template <>
struct object_with_zone<::libmuscle::impl::Data> {
    void operator()(
            msgpack::object::with_zone & obj,
            ::libmuscle::impl::Data const & d) const
    {
        obj.type = d.mp_obj_->type;
        obj.via = d.mp_obj_->via;
    }
};

}   // namespace adaptor

}   // namespace MSGPACK_API_VERSION_NAMESPACE

}   // namespace msgpack

