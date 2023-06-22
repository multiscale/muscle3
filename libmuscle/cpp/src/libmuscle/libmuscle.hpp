#pragma once

#include <libmuscle/namespace.hpp>
#include <libmuscle/data.hpp>
#include <libmuscle/instance.hpp>
#include <libmuscle/mcp/data_pack.hpp>
#include <libmuscle/message.hpp>
#include <libmuscle/ports_description.hpp>


namespace libmuscle {
    using _MUSCLE_IMPL_NS::Data;
    using _MUSCLE_IMPL_NS::DataConstRef;
    using _MUSCLE_IMPL_NS::Instance;
    // Note: C++20 allows using enum, which introduces all enum members in this scope
    using _MUSCLE_IMPL_NS::InstanceFlags;
    using _MUSCLE_IMPL_NS::Message;
    using _MUSCLE_IMPL_NS::PortsDescription;
    using _MUSCLE_IMPL_NS::StorageOrder;
}

