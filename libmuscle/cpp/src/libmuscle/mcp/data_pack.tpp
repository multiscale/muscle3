// Template implementation, do not include directly!


namespace msgpack {

MSGPACK_API_VERSION_NAMESPACE(MSGPACK_DEFAULT_API_NS) {

namespace adaptor {

template<>
struct pack<::libmuscle::_MUSCLE_IMPL_NS::DataConstRef> {
    template <typename Stream>
    packer<Stream>& operator()(
            msgpack::packer<Stream>& o,
            ::libmuscle::_MUSCLE_IMPL_NS::DataConstRef const& v) const
    {
        o.pack(*v.mp_obj_);
        return o;
    }
};

template<>
struct pack<::libmuscle::_MUSCLE_IMPL_NS::Data> {
    template <typename Stream>
    packer<Stream>& operator()(
            msgpack::packer<Stream>& o,
            ::libmuscle::_MUSCLE_IMPL_NS::Data const& v) const
    {
        o.pack(*v.mp_obj_);
        return o;
    }
};

template <>
struct object_with_zone<::libmuscle::_MUSCLE_IMPL_NS::DataConstRef> {
    void operator()(
            msgpack::object::with_zone & obj,
            ::libmuscle::_MUSCLE_IMPL_NS::DataConstRef const & d) const
    {
        obj.type = d.mp_obj_->type;
        obj.via = d.mp_obj_->via;
    }
};

template <>
struct object_with_zone<::libmuscle::_MUSCLE_IMPL_NS::Data> {
    void operator()(
            msgpack::object::with_zone & obj,
            ::libmuscle::_MUSCLE_IMPL_NS::Data const & d) const
    {
        obj.type = d.mp_obj_->type;
        obj.via = d.mp_obj_->via;
    }
};

}   // namespace adaptor

}   // namespace MSGPACK_API_VERSION_NAMESPACE

}   // namespace msgpack

