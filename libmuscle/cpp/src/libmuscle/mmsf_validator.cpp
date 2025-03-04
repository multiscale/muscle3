#include "mmsf_validator.hpp"

#include <sstream>

namespace {

template <typename Container, typename T>
inline bool contains(Container const & container, T const & value) {
    return std::find(container.begin(), container.end(), value) != container.end();
}

}

namespace libmuscle { namespace _MUSCLE_IMPL_NS {

using ::ymmsl::Operator;

MMSFValidator::MMSFValidator(PortManager const& port_manager, Logger & logger)
    : port_manager_(port_manager)
    , logger_(logger)
    , enabled_(true)
    , current_operator_(Operator::NONE)
{
    auto port_names = port_manager.list_ports();

    connected_ports_[Operator::NONE] = {};
    connected_ports_[Operator::F_INIT] = {};
    connected_ports_[Operator::O_I] = {};
    connected_ports_[Operator::S] = {};
    connected_ports_[Operator::O_F] = {};
    
    for (auto const & value : port_names) {
        auto const & op = value.first;
        std::vector<std::string> connected_ports;
        for (auto const & port_name : value.second) {
            auto const & port_obj = port_manager.get_port(port_name);
            if (port_obj.is_connected()) {
                connected_ports.push_back(port_name);
            }
            if (port_obj.is_vector()) {
                enabled_ = false;  // We don't support vector ports (yet)
            }
            port_operators_[port_name] = op;
        }
        connected_ports_[op] = connected_ports;
    }

    if (!connected_ports_[Operator::NONE].empty())
        logger_.warning(
                "This instance is using ports with Operator.NONE. This does not "
                "adhere to the Multiscale Modelling and Simulation Framework "
                "and may lead to deadlocks. You can disable this warning by "
                "setting the flag InstanceFlags::SKIP_MMSF_SEQUENCE_CHECKS "
                "when creating the libmuscle::Instance.");

    // Allowed operator transitions, the following are unconditionally allowed
    allowed_transitions_[Operator::NONE] = {Operator::NONE, Operator::F_INIT};
    allowed_transitions_[Operator::F_INIT] = {Operator::O_I, Operator::O_F};
    allowed_transitions_[Operator::O_I] = {Operator::S};
    allowed_transitions_[Operator::S] = {Operator::O_I, Operator::O_F};
    allowed_transitions_[Operator::O_F] = {Operator::NONE};
    // If there are operators without connected ports, we can skip over those
    // This logic is transitive, i.e. when there are no connected ports for both
    // F_INIT and O_I, we will also add NONE -> S to self._allowed_transition:
    for (auto const op : {Operator::F_INIT, Operator::O_I, Operator::S, Operator::O_F}) {
        if (connected_ports_[op].empty()) {
            // Find all transitions A -> op -> B and allow transition A -> B:
            for (auto & item : allowed_transitions_) {
                if (item.first == op) continue;
                auto & allowed = item.second;
                if (!contains(allowed, op))
                    continue;  // op is not in the allowed list
                for (auto const & to_op : allowed_transitions_[op]) {
                    if (!contains(allowed, to_op))
                        allowed.push_back(to_op);
                }
            }
        }
    }
    // Sort allowed transitions for more logical log messages
    for (auto & item : allowed_transitions_) {
        std::sort(item.second.begin(), item.second.end());
    }

    if (enabled_) {
        logger_.debug("MMSF Validator is enabled");
    } else {
        logger_.debug(
                "MMSF Validator is disabled: this instance uses vector ports, "
                "which are not supported by the MMSF Validator.");
    }
}

void MMSFValidator::check_send(
        std::string const& port_name, Optional<int> slot)
{
    check_send_receive_(port_name, slot);
}

void MMSFValidator::check_receive(
        std::string const& port_name, Optional<int> slot)
{
    check_send_receive_(port_name, slot);
}

void MMSFValidator::reuse_instance() {
    if (enabled_) {
        check_transition_(Operator::NONE, "");
    }
}

void MMSFValidator::skip_f_init() {
    // Pretend we're now in F_INIT and we have already received on all F_INIT ports
    current_operator_ = Operator::F_INIT;
    current_ports_used_ = connected_ports_[Operator::F_INIT];
}

void MMSFValidator::check_send_receive_(
        std::string const& port_name, Optional<int> slot)
{
    if (!enabled_) return;

    auto op = port_operators_[port_name];
    if (current_operator_ != op) {
        // Operator changed, check that all ports were used in the previous operator
        check_transition_(op, port_name);
    }

    if (contains(current_ports_used_, port_name)) {
        // We're using the same port for a second time, this is fine if:
        // 1. We're allowed to do this operator immediately again, and
        // 2. All ports of the current operator have been used
        // Both are checked by check_transition_:
        check_transition_(op, port_name);
    }

    current_ports_used_.push_back(port_name);
}

void MMSFValidator::check_transition_(
        ::ymmsl::Operator op, std::string const& port_name)
{
    std::ostringstream expected_oss;

    std::vector<std::string> unused_ports;
    for (auto const & port : connected_ports_[current_operator_]) {
        if (!contains(current_ports_used_, port)) {
            unused_ports.push_back(port);
        }
    }
    if (!unused_ports.empty()) {
        // We didn't complete the current phase
        if (::ymmsl::allows_receiving(current_operator_)) {
            expected_oss << "a receive";
        } else {
            expected_oss << "a send";
        }
        expected_oss << " on any of these " << ::ymmsl::operator_name(current_operator_) << " ports: ";
        for (std::size_t i = 0; i < unused_ports.size(); ++i) {
            if (i > 0) expected_oss << ", ";
            expected_oss << unused_ports[i];
        }
    } else if (!contains(allowed_transitions_[current_operator_], op)) {
        // Transition to the operator is not allowed
        std::size_t i = 0;
        for (auto const & to_op : allowed_transitions_[current_operator_]) {
            if (i++ > 0) expected_oss << " or ";
            if (to_op == Operator::NONE) {
                expected_oss << "a call to reuse_instance()";
            } else if (!connected_ports_[to_op].empty()) {
                if (::ymmsl::allows_receiving(to_op)) {
                    expected_oss << "a receive";
                } else {
                    expected_oss << "a send";
                }
                expected_oss << " on an " << ::ymmsl::operator_name(to_op);
                expected_oss << " port (";
                std::size_t j = 0;
                for (auto const & port : connected_ports_[to_op]) {
                    if (j++ > 0) expected_oss << ", ";
                    expected_oss << port;
                }
                expected_oss << ")";
            }
        }
    }

    std::string expected = expected_oss.str();
    if (!expected.empty())  {
        // We expected something else, log a warning
        std::string action;
        if (op == Operator::NONE) {
            action = "reuse_instance()";
        } else if (op == Operator::F_INIT || op == Operator::S) {
            action = "Receive on port '" + port_name + "'";
        } else {
            action = "Send on port '" + port_name + "'";
        }

        logger_.warning(
                action, " does not adhere to the MMSF: was expecting ", expected,
                ".\n"
                "Not adhering to the Multiscale Modelling and Simulation Framework "
                "may lead to deadlocks. You can disable this warning by "
                "setting the flag InstanceFlags::SKIP_MMSF_SEQUENCE_CHECKS "
                "when creating the libmuscle::Instance.");
    }

    current_operator_ = op;
    current_ports_used_.clear();
}

} }
