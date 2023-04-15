#include <libmuscle/close_port.hpp>

#include <libmuscle/mcp/ext_types.hpp>


using libmuscle::_MUSCLE_IMPL_NS::mcp::ExtTypeId;


namespace libmuscle { namespace _MUSCLE_IMPL_NS {

ClosePort::ClosePort()
    :  Data()
{
    char * zoned_mem = zone_alloc_<char>(1);
    zoned_mem[0] = static_cast<char>(ExtTypeId::close_port);
    *mp_obj_ << msgpack::type::ext_ref(zoned_mem, 1);
}

bool is_close_port(DataConstRef const & data) {
    return (data.mp_obj_->type == msgpack::type::EXT &&
            data.mp_obj_->via.ext.type() ==
                static_cast<int8_t>(ExtTypeId::close_port));
}

} }

