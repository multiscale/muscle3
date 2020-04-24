#pragma once

#include <cstdint>


namespace libmuscle { namespace impl { namespace mcp {

enum class ExtTypeId : int8_t {
    close_port = 0,
    settings = 1,
    grid_int32 = 2,
    grid_int64 = 3,
    grid_float32 = 4,
    grid_float64 = 5,
    grid_bool = 6
};

} } }

