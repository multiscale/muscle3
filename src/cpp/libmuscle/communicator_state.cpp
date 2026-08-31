#include "communicator_state.hpp"


namespace libmuscle { namespace _MUSCLE_IMPL_NS {

Data CommunicatorState::to_data() const {
    Data pmc = Data::dict();
    for (const auto & kv : port_message_counts) {
        Data counts = Data::nils(kv.second.size());
        for (std::size_t i=0; i<kv.second.size(); ++i) {
            counts[i] = kv.second[i];
        }
        pmc[kv.first] = counts;
    }

    return Data::dict(
        "port_message_counts", pmc,
        "timeline_state", timeline_state.to_data());
}

CommunicatorState CommunicatorState::from_data(DataConstRef const & data) {
    CommunicatorState state;

    auto data_pmc = data["port_message_counts"];
    for (std::size_t i=0; i<data_pmc.size(); ++i) {
        std::vector<int> counts;
        for (std::size_t j=0; j<data_pmc.value(i).size(); ++j) {
            counts.push_back(data_pmc.value(i)[j].as<int>());
        }
        state.port_message_counts[data_pmc.key(i)] = counts;
    }

    state.timeline_state = TimelineState::from_data(data["timeline_state"]);

    return state;
}

} }