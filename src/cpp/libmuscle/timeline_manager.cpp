#include <libmuscle/timeline_manager.hpp>

#include <cassert>
#include <sstream>
#include <algorithm>
#include "timeline_manager.hpp"


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
    if (!data[1].is_nil())
        slot = data[1].as<int>();
    return PortAndSlot(data[0].as<std::string>(), slot);
}


Data encode_participated(std::vector<PortAndSlot> const & participated) {
    Data result = Data::nils(participated.size());
    for (std::size_t i = 0; i < participated.size(); ++i)
        result[i] = encode_port_and_slot(participated[i]);
    return result;
}

std::vector<PortAndSlot> decode_participated(DataConstRef const & data) {
    std::vector<PortAndSlot> result;
    for (std::size_t i = 0; i < data.size(); ++i)
        result.push_back(decode_port_and_slot(data[i]));
    return result;
}


Data encode_iteration(Optional<IterationCount> const & iteration) {
    if (!iteration.is_set())
        return Data();
    Data result = Data::nils(iteration.get().size());
    for (std::size_t i = 0; i < iteration.get().size(); ++i)
        result[i] = iteration.get()[i];
    return result;
}

Optional<IterationCount> decode_iteration(DataConstRef const & data) {
    if (data.is_nil())
        return {};
    IterationCount result;
    for (std::size_t i = 0; i < data.size(); ++i)
        result.push_back(data[i].as<int>());
    return result;
}

bool is_subiteration(IterationCount const & it1, IterationCount const & it2) {
    if (it1.size() < it2.size())
        return false;
    for (std::size_t i = 0; i < it2.size(); ++i) {
        if (it1[i] != it2[i])
            return false;
    }
    return true;
}

std::string to_string(IterationCount const & iteration) {
    std::ostringstream oss;
    oss << "[";
    for (std::size_t i = 0; i < iteration.size(); ++i) {
        if (i > 0) oss << ", ";
        oss << iteration[i];
    }
    oss << "]";
    return oss.str();
}

IterationCount const & get_most_nested_iteration(std::vector<IterationCount> const & iterations) {
    if (iterations.empty())
        throw std::logic_error("iterations is an empty list");
    std::vector<std::reference_wrapper<IterationCount const>> sorted(iterations.begin(), iterations.end());
    std::sort(sorted.begin(), sorted.end(),
            [](auto && lhs, auto && rhs) {
                return lhs.get() < rhs.get();   // lexicographical vector comparison
            });
    for (std::size_t i = 0; i < iterations.size() - 1; ++i) {
        if (!is_subiteration(sorted[i + 1], sorted[i]))
            throw std::logic_error(
                to_string(sorted[i+1]) + " is not a subiteration of "
                + to_string(sorted[i]));
    }
    return sorted.back();
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
            "subtimeline_states", subtimelines);
}

TimelineState TimelineState::from_data(DataConstRef const & data) {
    TimelineState state;
    state.iteration = decode_iteration(data["iteration"]);
    state.send_participated = decode_participated(data["send_participated"]);

    auto subtimelines = data["subtimeline_states"];
    for (std::size_t i = 0; i < subtimelines.size(); ++i)
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
    if (slots.size() <= 1)
        return port_ref(port, slots.empty() ? Optional<int>() : slots[0]);

    std::string name(port.name);
    std::ostringstream oss;
    oss << ::ymmsl::operator_name(port.oper) << " port '" << name << "' (slots ";
    for (std::size_t i = 0; i < slots.size(); ++i) {
        if (i != 0)
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

void expected_actions(
        TimelinePorts const * send, TimelinePorts const * receive, ExpectedActions & result,
        bool missing_only = true) {
    if (send) {
        auto pr_list = missing_only ? send->missing_ports() : send->all_ports();
        for (auto const & pr : pr_list)
            result.emplace_back("send", pr.first, pr.second);
    }
    if (receive) {
        auto pr_list = missing_only ? receive->missing_ports() : receive->all_ports();
        for (auto const & pr : pr_list)
            result.emplace_back("receive", pr.first, pr.second);
    }
}

}   // anonymous namespace


PortBlocked::PortBlocked(Port const & port, Optional<int> slot, ExpectedActions expected)
    : TimelineError(expected_message(
            std::string(::ymmsl::allows_sending(port.oper) ? "send" : "receive")
                    + " a message on " + port_ref(port, slot),
            expected))
    , action(::ymmsl::allows_sending(port.oper) ? "send" : "receive")
    , port(port)
    , slot(slot)
    , expected(std::move(expected))
{}

ReuseLoopIncomplete::ReuseLoopIncomplete(ExpectedActions expected)
    : TimelineError(expected_message("call reuse_instance()", expected))
    , expected(std::move(expected))
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


TimelinePorts::TimelinePorts(PortManager::PortReferences ports_in)
    : ports(ports_in)
    , participated()
{}

void TimelinePorts::participate(std::string const & port_name, Optional<int> slot) {
    if (!has_participated(port_name, slot))
        participated.emplace_back(port_name, slot);
}

bool TimelinePorts::has_participated(std::string const & port_name, Optional<int> slot) const {
    PortAndSlot key(port_name, slot);
    return std::find(participated.begin(), participated.end(), key) != participated.end();
}

bool TimelinePorts::all_participated() const {
    std::size_t num_slots = 0;
    for (Port const & port : ports) // ports is a copy, not a reference!!!!!!!!!!!
        num_slots += port.is_vector() ? static_cast<std::size_t>(port.get_length()) : 1;
    return participated.size() == num_slots;
}

std::vector<std::pair<Port, std::vector<int>>> TimelinePorts::missing_ports() const {
    std::vector<std::pair<Port, std::vector<int>>> result;
    for (Port const & port : ports) {
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
        if (port.get().is_vector())
            for (int slot = 0; slot < port.get().get_length(); ++slot)
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
        if (first_operator_.get() == Operator::S && !receive_.all_participated()) {
            ExpectedActions expected;
            expected_actions(nullptr, &receive_, expected);
            throw PortBlocked(port, slot, expected);
        }
    } else {
        if (!(first_operator_.get() == Operator::O_I)) {
            ExpectedActions expected;
            expected_actions(nullptr, &receive_, expected, false);
            throw PortBlocked(port, slot, expected);
        }
        if (!is_complete()) {
            ExpectedActions expected;
            expected_actions(&send_, &receive_, expected);
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
            ExpectedActions expected;
            expected_actions(&send_, nullptr, expected);
            throw PortBlocked(port, slot, expected);
        }
    } else {
        if (!(first_operator_.get() == Operator::S)) {
            ExpectedActions expected;
            expected_actions(&send_, nullptr, expected, false);
            throw PortBlocked(port, slot, expected);
        }
        if (!(send_.all_participated() && receive_.all_participated())) {
            ExpectedActions expected;
            expected_actions(&send_, &receive_, expected);
            throw PortBlocked(port, slot, expected);
        }
    }
}

IterationCount const & SubTimelineManager::record_received_message(
        Port const & port, Optional<int> slot, IterationCount const & iteration,
        IterationCount const & component_iteration, int num_repeat_filters) {
    std::string port_name = std::string(port.name);

    if (!iteration_.is_set()) {
        if (num_repeat_filters > 0) {
            // Handle cases with multiple levels of repeat filters, for example:
            // - cached message iteration count: [2], with 2 repeat filters
            // - component iteration count: [2, 1]
            // Our iteration count needs to become [2, 1, 0]
            iteration_ = component_iteration;
            iteration_.get().push_back(0);
        } else {
            iteration_ = iteration;
        }
        first_operator_ = Operator::S;
    } else if (!receive_.has_participated(port_name, slot)) {
        if (num_repeat_filters == 0 && iteration != iteration_.get())
            throw MessageOutOfSync(port, slot);
    } else {
        if (num_repeat_filters > 0)
            ++iteration_.get().back();
        else if (iteration <= iteration_.get())
            throw MessageOutOfSync(port, slot);
        else
            iteration_ = iteration;
        send_.reset();
        receive_.reset();
    }

    receive_.participate(port_name, slot);
    return iteration_.get();
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

void SubTimelineManager::missing_actions(ExpectedActions & result) const {
    expected_actions(&send_, &receive_, result);
}


// Unlike Communicator/PortManager, this file also holds SubTimelineManager and
// the (Sub)TimelineState code, which are never mocked and must stay compiled even
// when a test mocks TimelineManager but still includes this file for them.
#ifndef LIBMUSCLE_MOCK_TIMELINE_MANAGER

TimelineManager::TimelineManager(PortManager const & port_manager)
    : port_manager_(port_manager)
    , receive_(port_manager.get_connected_ports(Operator::F_INIT, Optional<Timeline>()))
    , send_(port_manager.get_connected_ports(Operator::O_F, Optional<Timeline>()))
    , submanagers_()
    , iteration_()
{
    for (auto const & tl : port_manager_.list_subtimelines())
        submanagers_.emplace(tl, SubTimelineManager(tl, port_manager_));
}

IterationCount TimelineManager::check_send_message(
        std::string const & port_name, Optional<int> slot) {
    Port const & port = port_manager_.get_port(port_name);

    if (port.oper == Operator::O_F)
        return check_send_o_f_(port, slot);

    return submanagers_.at(port.timeline).check_send_message(port, slot, iteration_.get());
}

IterationCount TimelineManager::check_pre_received_iteration_counts(
        std::vector<IterationCount> const & iterations)
{
    IterationCount new_iteration;
    if (iterations.empty()) {
        assert(!port_manager_.has_f_init_connections());
    } else {
        new_iteration = get_most_nested_iteration(iterations);
    }
    if (iteration_.is_set() && new_iteration <= iteration_.get())
        throw std::runtime_error(
            "Internal error: received F_INIT iteration count " + to_string(new_iteration)
            + " is not newer than the previous iteration " + to_string(iteration_.get()));
    iteration_ = new_iteration;
    return new_iteration;
}

IterationCount TimelineManager::check_send_o_f_(Port const & port, Optional<int> slot) {
    std::string port_name = std::string(port.name);

    ExpectedActions expected;
    for (auto const & item : submanagers_) {
        if (!item.second.is_complete())
            item.second.missing_actions(expected);
    }
    if (!expected.empty())
        throw PortBlocked(port, slot, expected);

    if (send_.has_participated(port_name, slot))
        throw AlreadyParticipated(port, slot);
    send_.participate(port_name, slot);

    return iteration_.get();
}

void TimelineManager::check_receive_s(std::string const & port_name, Optional<int> slot) {
    Port const & port = port_manager_.get_port(port_name);
    assert(port.oper == Operator::S);
    submanagers_.at(port.timeline).check_receive(port, slot);
}

IterationCount const & TimelineManager::record_received_s_message(
        std::string const & port_name, Optional<int> slot,
        IterationCount const & iteration, int num_repeat_filters) {
    Port const & port = port_manager_.get_port(port_name);
    assert(port.oper == Operator::S);
    return submanagers_.at(port.timeline).record_received_message(
            port, slot, iteration, iteration_.get(), num_repeat_filters);
}

void TimelineManager::reset() {
    send_.reset();
    for (auto & item : submanagers_)
        item.second.reset();
}

Optional<IterationCount> TimelineManager::start_reuse_iteration() {
    auto iteration = iteration_;
    bool subtimelines_complete = true;
    for (auto const & item : submanagers_) {
        if (!item.second.is_complete()) {
            subtimelines_complete = false;
            break;
        }
    }

    if (!iteration.is_set() || (
            send_.all_participated()
            && subtimelines_complete )) {
        reset();
        return iteration;
    }

    ExpectedActions expected;
    expected_actions(&send_, nullptr, expected);
    for (auto const & item : submanagers_) {
        if (!item.second.is_complete())
            item.second.missing_actions(expected);
    }

    throw ReuseLoopIncomplete(expected);
}

TimelineState TimelineManager::get_state() const {
    TimelineState state;
    state.iteration = iteration_;
    state.send_participated = send_.participated;
    for (auto const & item : submanagers_)
        state.subtimeline_states.emplace(
                static_cast<std::string>(item.first), item.second.get_state());
    return state;
}

void TimelineManager::restore_state(TimelineState const & state) {
    iteration_ = state.iteration;
    send_.participated = state.send_participated;
    for (auto & item : submanagers_) {
        auto it = state.subtimeline_states.find(static_cast<std::string>(item.first));
        if (it != state.subtimeline_states.end())
            item.second.restore_state(it->second);
    }
}

#endif

} }
