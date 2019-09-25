// Template implementation, do not include directly!


namespace msgpack {

MSGPACK_API_VERSION_NAMESPACE(MSGPACK_DEFAULT_API_NS) {

namespace adaptor {

template<>
struct pack<::libmuscle::DataConstRef> {
    template <typename Stream>
    packer<Stream>& operator()(
            msgpack::packer<Stream>& o,
            ::libmuscle::DataConstRef const& v) const
    {
        o.pack(*v.mp_obj_);
        return o;
    }
};

template<>
struct pack<::libmuscle::Data> {
    template <typename Stream>
    packer<Stream>& operator()(
            msgpack::packer<Stream>& o,
            ::libmuscle::Data const& v) const
    {
        o.pack(*v.mp_obj_);
        return o;
    }
};

template <>
struct object_with_zone<::libmuscle::DataConstRef> {
    void operator()(
            msgpack::object::with_zone & obj,
            ::libmuscle::DataConstRef const & d) const
    {
        obj.type = d.mp_obj_->type;
        obj.via = d.mp_obj_->via;
    }
};

template <>
struct object_with_zone<::libmuscle::Data> {
    void operator()(
            msgpack::object::with_zone & obj,
            ::libmuscle::Data const & d) const
    {
        obj.type = d.mp_obj_->type;
        obj.via = d.mp_obj_->via;
    }
};

}   // namespace adaptor

}   // namespace MSGPACK_API_VERSION_NAMESPACE

}   // namespace msgpack

