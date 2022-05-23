#pragma once

#include "libmuscle/data.hpp"

#include <memory>

#include <msgpack.hpp>


namespace libmuscle { namespace impl {

namespace mcp {

/* Helper function that unpacks data.
 *
 * This has friend access to Data, so that it can create one from a msgpack
 * object_handle. That keeps MessagePack out of the public API, and avoids the
 * whole interface/factory rigmarole.
 *
 * @param zone Zone to allocate on
 * @param begin Pointer to beginning of buffer to read from.
 * @param buf Length of the buffer to read from.
 * @return A Data object with the unpacked data.
 */
Data unpack_data(
        std::shared_ptr<msgpack::zone> const & zone,
        char const * begin, std::size_t length);

}   // namespace mcp

} }   // namespace libmuscle::impl

#include "libmuscle/mcp/data_pack.tpp"

