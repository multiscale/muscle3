#include <libmuscle/timeline_manager.hpp>

#include <sstream>


using ymmsl::Operator;
using ymmsl::Timeline;


namespace libmuscle { namespace _MUSCLE_IMPL_NS {

Data encode_port_and_slot(PortAndSlot const & port_and_slot) {
    Data slot;
    if (port_and_slot.second.is_set())
        slot = port_and_slot.second.get();
    return Data::list(port_and_slot.first, slot);
}

PortAndSlot decode_port_and_slot(DataConstRef const & data) {
    Optional<int> slot;
    if (!data[1u].is_nil())
        slot = data[1u].as<int>();
    return PortAndSlot(data[0u].as<std::string>(), slot);
}


Data encode_participated(std::vector<PortAndSlot> const & participated) {
    Data result = Data::nils(participated.size());
    for (std::size_t i = 0u; i < participated.size(); ++i)
        result[i] = encode_port_and_slot(participated[i]);
    return result;
}

std::vector<PortAndSlot> decode_participated(DataConstRef const & data) {
    std::vector<PortAndSlot> result;
    for (std::size_t i = 0u; i < data.size(); ++i)
        result.push_back(decode_port_and_slot(data[i]));
    return result;
}


Data encode_iteration(Optional<IterationCount> const & iteration) {
    if (!iteration.is_set())
        return Data();
    Data result = Data::nils(iteration.get().size());
    for (std::size_t i = 0u; i < iteration.get().size(); ++i)
        result[i] = iteration.get()[i];
    return result;
}

Optional<IterationCount> decode_iteration(DataConstRef const & data) {
    if (data.is_nil())
        return {};
    IterationCount result;
    for (std::size_t i = 0u; i < data.size(); ++i)
        result.push_back(data[i].as<int>());
    return result;
}


Data SubTimelineState::to_data() const {
    Data first_op;
    if (first_operator.is_set())
        first_op = ::ymmsl::operator_name(first_operator.get());

    return Data::dict(
            "iteration", encode_iteration(iteration),
            "first_operator", first_op,
            "send_participated", encode_participated(send_participated),
            "receive_participated", encode_participated(receive_participated));
}

SubTimelineState SubTimelineState::from_data(DataConstRef const & data) {
    SubTimelineState state;
    state.iteration = decode_iteration(data["iteration"]);
    if (!data["first_operator"].is_nil())
        state.first_operator = ::ymmsl::operator_for_name(
                data["first_operator"].as<std::string>());
    state.send_participated = decode_participated(data["send_participated"]);
    state.receive_participated = decode_participated(data["receive_participated"]);
    return state;
}

Data TimelineState::to_data() const {
    Data subtimelines = Data::dict();
    for (auto const & kv : subtimeline_states)
        subtimelines[kv.first] = kv.second.to_data();

    return Data::dict(
            "iteration", encode_iteration(iteration),
            "send_participated", encode_participated(send_participated),
            "receive_participated", encode_participated(receive_participated),
            "subtimeline_states", subtimelines);
}

TimelineState TimelineState::from_data(DataConstRef const & data) {
    TimelineState state;
    state.iteration = decode_iteration(data["iteration"]);
    state.send_participated = decode_participated(data["send_participated"]);
    state.receive_participated = decode_participated(data["receive_participated"]);

    auto subtimelines = data["subtimeline_states"];
    for (std::size_t i = 0u; i < subtimelines.size(); ++i)
        state.subtimeline_states[subtimelines.key(i)] =
                SubTimelineState::from_data(subtimelines.value(i));
    return state;
}


namespace {

std::string port_ref(Port const & port, Optional<int> const & slot) {
    std::string name(port.name);
    std::ostringstream oss;
    oss << ::ymmsl::operator_name(port.oper) << " port '" << port_desc(name, slot) << "'";
    return oss.str();
}

std::string port_ref(Port const & port, std::vector<int> const & slots) {
    if (slots.size() <= 1u)
        return port_ref(port, slots.empty() ? Optional<int>() : slots[0]);

    std::string name(port.name);
    std::ostringstream oss;
    oss << ::ymmsl::operator_name(port.oper) << " port '" << name << "' (slots ";
    for (std::size_t i = 0u; i < slots.size(); ++i) {
        if (i != 0u)
            oss << ", ";
        oss << slots[i];
    }
    oss << ")";
    return oss.str();
}

std::string expected_message(std::string const & subject, ExpectedActions const & expected) {
    std::ostringstream oss;
    oss << "Not allowed to " << subject << " yet: was expecting one of the following"
        << " instead:";
    for (auto const & item : expected) {
        oss << "\n- A " << std::get<0>(item) << " on "
            << port_ref(std::get<1>(item), std::get<2>(item));
    }
    return oss.str();
}

ExpectedActions expected_actions(
        TimelinePorts const & ports, std::string const & action, bool missing_only = true) {
    ExpectedActions result;
    auto pr_list = missing_only ? ports.missing_ports() : ports.all_ports();
    for (auto const & pr : pr_list)
        result.emplace_back(action, pr.first, pr.second);
    return result;
}

}   // anonymous namespace


PortBlocked::PortBlocked(Port const & port, Optional<int> slot, ExpectedActions const & expected)
    : TimelineError(expected_message(
            std::string(::ymmsl::allows_sending(port.oper) ? "send" : "receive")
                    + " a message on " + port_ref(port, slot),
            expected))
    , action(::ymmsl::allows_sending(port.oper) ? "send" : "receive")
    , port(port)
    , slot(slot)
    , expected(expected)
{}

ReuseLoopIncomplete::ReuseLoopIncomplete(ExpectedActions const & expected)
    : TimelineError(expected_message("call reuse_instance()", expected))
    , expected(expected)
{}

AlreadyParticipated::AlreadyParticipated(Port const & port, Optional<int> slot)
    : TimelineError(
            std::string("Not allowed to ")
                    + (::ymmsl::allows_sending(port.oper) ? "send" : "receive")
                    + " another message on " + port_ref(port, slot) + " yet: it already "
                    + (::ymmsl::allows_sending(port.oper) ? "sent" : "received")
                    + " one this reuse loop iteration.")
    , action(::ymmsl::allows_sending(port.oper) ? "send" : "receive")
    , port(port)
    , slot(slot)
{}

MessageOutOfSync::MessageOutOfSync(Port const & port, Optional<int> slot)
    : TimelineError(
            std::string("Received a message on ") + port_ref(port, slot)
                    + " that this component wasn't expecting. This should not happen and may"
                      " be a bug in MUSCLE3. Please file an issue at"
                      " https://github.com/multiscale/muscle3/issues.")
    , port(port)
    , slot(slot)
{}


TimelinePorts::TimelinePorts(std::vector<Port> const & ports_in)
    : ports(ports_in)
    , num_slots(0u)
    , participated()
{
    for (auto const & port : ports)
        num_slots += port.is_vector() ? static_cast<std::size_t>(port.get_length()) : 1u;
}

void TimelinePorts::participate(std::string const & port_name, Optional<int> slot) {
    if (!has_participated(port_name, slot))
        participated.emplace_back(port_name, slot);
}

bool TimelinePorts::has_participated(std::string const & port_name, Optional<int> slot) const {
    PortAndSlot key(port_name, slot);
    for (auto const & p : participated)
        if (p == key)
            return true;
    return false;
}

bool TimelinePorts::all_participated() const {
    return participated.size() == num_slots;
}

std::vector<std::pair<Port, std::vector<int>>> TimelinePorts::missing_ports() const {
    std::vector<std::pair<Port, std::vector<int>>> result;
    for (auto const & port : ports) {
        std::string name = std::string(port.name);
        if (port.is_vector()) {
            std::vector<int> slots;
            for (int slot = 0; slot < port.get_length(); ++slot)
                if (!has_participated(name, slot))
                    slots.push_back(slot);
            if (!slots.empty())
                result.emplace_back(port, slots);
        } else if (!has_participated(name, {})) {
            result.emplace_back(port, std::vector<int>());
        }
    }
    return result;
}

std::vector<std::pair<Port, std::vector<int>>> TimelinePorts::all_ports() const {
    std::vector<std::pair<Port, std::vector<int>>> result;
    for (auto const & port : ports) {
        std::vector<int> slots;
        if (port.is_vector())
            for (int slot = 0; slot < port.get_length(); ++slot)
                slots.push_back(slot);
        result.emplace_back(port, slots);
    }
    return result;
}

void TimelinePorts::reset() {
    participated.clear();
}


SubTimelineManager::SubTimelineManager(
        Timeline const & timeline, PortManager const & port_manager)
    : timeline_(timeline)
    , iteration_()
    , first_operator_()
    , send_(port_manager.get_connected_ports(Operator::O_I, timeline))
    , receive_(port_manager.get_connected_ports(Operator::S, timeline))
{}

bool SubTimelineManager::is_complete() const {
    if (iteration_.is_set())
        return send_.all_participated() && receive_.all_participated();
    return true;
}

IterationCount SubTimelineManager::check_send_message(
        Port const & port, Optional<int> slot, IterationCount const & parent_iteration) {
    std::string port_name = std::string(port.name);

    if (!iteration_.is_set()) {
        IterationCount it(parent_iteration);
        it.push_back(0);
        iteration_ = it;
        first_operator_ = Operator::O_I;
    } else if (!send_.has_participated(port_name, slot)) {
        if (first_operator_.is_set() && first_operator_.get() == Operator::S
                && !receive_.all_participated()) {
            throw PortBlocked(port, slot, expected_actions(receive_, "receive"));
        }
    } else {
        if (!(first_operator_.is_set() && first_operator_.get() == Operator::O_I)) {
            throw PortBlocked(port, slot, expected_actions(receive_, "receive", false));
        }
        if (!is_complete()) {
            ExpectedActions expected_send = expected_actions(send_, "send");
            ExpectedActions expected_receive = expected_actions(receive_, "receive");
            ExpectedActions expected = std::move(expected_send);
            expected.insert(expected.end(), expected_receive.begin(), expected_receive.end());
            throw PortBlocked(port, slot, expected);
        }
        iteration_.get().back() += 1;
        send_.reset();
        receive_.reset();
    }

    send_.participate(port_name, slot);
    return iteration_.get();
}

void SubTimelineManager::check_receive(Port const & port, Optional<int> slot) {
    std::string port_name = std::string(port.name);

    if (!receive_.has_participated(port_name, slot)) {
        if (first_operator_.is_set() && first_operator_.get() == Operator::O_I
                && !send_.all_participated()) {
            throw PortBlocked(port, slot, expected_actions(send_, "send"));
        }
    } else {
        if (!(first_operator_.is_set() && first_operator_.get() == Operator::S)) {
            throw PortBlocked(port, slot, expected_actions(send_, "send", false));
        }
        if (!(send_.all_participated() && receive_.all_participated())) {
            ExpectedActions expected_send = expected_actions(send_, "send");
            ExpectedActions expected_receive = expected_actions(receive_, "receive");
            ExpectedActions expected = std::move(expected_send);
            expected.insert(expected.end(), expected_receive.begin(), expected_receive.end());
            throw PortBlocked(port, slot, expected);
        }
    }
}

void SubTimelineManager::record_received_message(
        Port const & port, Optional<int> slot, IterationCount const & iteration) {
    std::string port_name = std::string(port.name);

    if (!iteration_.is_set()) {
        iteration_ = iteration;
        first_operator_ = Operator::S;
    } else if (!receive_.has_participated(port_name, slot)) {
        if (iteration != iteration_.get())
            throw MessageOutOfSync(port, slot);
    } else {
        if (iteration <= iteration_.get())
            throw MessageOutOfSync(port, slot);
        iteration_ = iteration;
        send_.reset();
        receive_.reset();
    }

    receive_.participate(port_name, slot);
}

void SubTimelineManager::reset() {
    iteration_ = Optional<IterationCount>();
    first_operator_ = Optional<Operator>();
    send_.reset();
    receive_.reset();
}

SubTimelineState SubTimelineManager::get_state() const {
    SubTimelineState state;
    state.iteration = iteration_;
    state.first_operator = first_operator_;
    state.send_participated = send_.participated;
    state.receive_participated = receive_.participated;
    return state;
}

void SubTimelineManager::restore_state(SubTimelineState const & state) {
    iteration_ = state.iteration;
    first_operator_ = state.first_operator;
    send_.participated = state.send_participated;
    receive_.participated = state.receive_participated;
}


TimelineManager::TimelineManager(PortManager const & port_manager)
    : port_manager_(port_manager)
    , receive_([&port_manager] {
            auto ports = port_manager.get_connected_ports(Operator::F_INIT, Optional<Timeline>());
            if (port_manager.settings_in_connected())
                ports.push_back(port_manager.get_port("muscle_settings_in"));
            return ports;
        }())
    , send_(port_manager.get_connected_ports(Operator::O_F, Optional<Timeline>()))
    , submanagers_()
    , iteration_()
{
    for (auto const & tl : port_manager_.list_subtimelines())
        submanagers_.emplace(tl, SubTimelineManager(tl, port_manager_));

    if (!port_manager_.has_f_init_connections())
        iteration_ = IterationCount();
}

IterationCount TimelineManager::check_send_message(
        std::string const & port_name, Optional<int> slot) {
    Port const & port = port_manager_.get_port(port_name);

    if (port.oper == Operator::O_F)
        return check_send_o_f_(port, slot);

    return submanagers_.at(port.timeline).check_send_message(port, slot, iteration_.get());
}

IterationCount TimelineManager::check_send_o_f_(Port const & port, Optional<int> slot) {
    std::string port_name = std::string(port.name);

    ExpectedActions expected;
    for (auto const & item : submanagers_) {
        if (!item.second.is_complete()) {
            ExpectedActions expected_send = expected_actions(item.second.send_, "send");
            ExpectedActions expected_receive = expected_actions(item.second.receive_, "receive");
            expected.insert(expected.end(), expected_send.begin(), expected_send.end());
            expected.insert(expected.end(), expected_receive.begin(), expected_receive.end());
        }
    }
    if (!expected.empty())
        throw PortBlocked(port, slot, expected);

    if (send_.has_participated(port_name, slot))
        throw AlreadyParticipated(port, slot);
    send_.participate(port_name, slot);

    return iteration_.get();
}

void TimelineManager::check_receive(std::string const & port_name, Optional<int> slot) {
    Port const & port = port_manager_.get_port(port_name);

    if (port.oper == Operator::F_INIT) {
        if (receive_.has_participated(port_name, slot))
            throw AlreadyParticipated(port, slot);
        return;
    }
    if (port.oper == Operator::S)
        submanagers_.at(port.timeline).check_receive(port, slot);
}

void TimelineManager::record_received_message(
        std::string const & port_name, Optional<int> slot, IterationCount const & iteration) {
    Port const & port = port_manager_.get_port(port_name);

    if (port.oper == Operator::F_INIT) {
        if (!iteration_.is_set())
            iteration_ = iteration;
        else if (iteration != iteration_.get())
            throw MessageOutOfSync(port, slot);
        receive_.participate(port_name, slot);
        return;
    }

    submanagers_.at(port.timeline).record_received_message(port, slot, iteration);
}

void TimelineManager::reset() {
    iteration_ = port_manager_.has_f_init_connections() ?
            Optional<IterationCount>() : Optional<IterationCount>(IterationCount());
    send_.reset();
    receive_.reset();
    for (auto & item : submanagers_)
        item.second.reset();
}

void TimelineManager::finish_reuse_iteration() {
    bool subtimelines_complete = true;
    for (auto const & item : submanagers_) {
        if (!item.second.is_complete()) {
            subtimelines_complete = false;
            break;
        }
    }

    if (receive_.all_participated() && send_.all_participated() && subtimelines_complete) {
        reset();
        return;
    }

    ExpectedActions expected_send = expected_actions(send_, "send");
    ExpectedActions expected_receive = expected_actions(receive_, "receive");
    ExpectedActions expected = std::move(expected_send);
    expected.insert(expected.end(), expected_receive.begin(), expected_receive.end());
    for (auto const & item : submanagers_) {
        if (!item.second.is_complete()) {
            ExpectedActions sub_expected_send = expected_actions(item.second.send_, "send");
            ExpectedActions sub_expected_receive =
                    expected_actions(item.second.receive_, "receive");
            expected.insert(expected.end(), sub_expected_send.begin(), sub_expected_send.end());
            expected.insert(
                    expected.end(), sub_expected_receive.begin(), sub_expected_receive.end());
        }
    }

    throw ReuseLoopIncomplete(expected);
}

TimelineState TimelineManager::get_state() const {
    TimelineState state;
    state.iteration = iteration_;
    state.send_participated = send_.participated;
    state.receive_participated = receive_.participated;
    for (auto const & item : submanagers_)
        state.subtimeline_states.emplace(
                static_cast<std::string>(item.first), item.second.get_state());
    return state;
}

void TimelineManager::restore_state(TimelineState const & state) {
    iteration_ = state.iteration;
    send_.participated = state.send_participated;
    receive_.participated = state.receive_participated;
    for (auto & item : submanagers_) {
        auto it = state.subtimeline_states.find(static_cast<std::string>(item.first));
        if (it != state.subtimeline_states.end())
            item.second.restore_state(it->second);
    }
}

} }
