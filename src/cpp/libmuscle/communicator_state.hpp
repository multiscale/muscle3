#pragma once

#include "libmuscle/data.hpp"
#include "libmuscle/mpp_message.hpp"
#include "libmuscle/port_manager.hpp"
#include "libmuscle/timeline_manager.hpp"

#include "ymmsl/ymmsl.hpp"

namespace libmuscle { namespace _MUSCLE_IMPL_NS {

class CommunicatorState {
    public:
        PortManager::PortMessageCounts port_message_counts;
        TimelineState timeline_state;
        std::unordered_map<::ymmsl::Reference, MPPMessage> message_cache;

        /** Convert CommunicatorState into Data */
        Data to_data() const;

        /** Create CommunicatorState from Data */
        static CommunicatorState from_data(DataConstRef const & data);
};

} }