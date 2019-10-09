#include "libmuscle/mcp/data_pack.hpp"

#include <msgpack.hpp>


namespace libmuscle { namespace impl {

namespace mcp {

Data unpack_data(std::shared_ptr<msgpack::zone> const & zone, char const * begin, std::size_t length) {
    auto zoned_obj = static_cast<msgpack::object *>(zone->allocate_align(
            sizeof(msgpack::object), MSGPACK_ZONE_ALIGNOF(msgpack::object)));
    *zoned_obj = msgpack::unpack(*zone, begin, length);
    return Data(zoned_obj, zone);
}

}   // namespace mcp

} }   // namespace libmuscle::impl

