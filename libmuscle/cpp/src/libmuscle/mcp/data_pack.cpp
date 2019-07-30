#include "libmuscle/mcp/data_pack.hpp"

namespace libmuscle {

namespace mcp {

Data unpack_data(char const * begin, std::size_t length) {
    return Data(msgpack::unpack(begin, length));
}

}   // namespace mcp

}   // namespace libmuscle

