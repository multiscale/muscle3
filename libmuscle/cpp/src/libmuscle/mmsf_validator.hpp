#pragma once

#include <string>
#include <unordered_map>
#include <vector>

#include <libmuscle/logger.hpp>
#include <libmuscle/port_manager.hpp>
#include <ymmsl/ymmsl.hpp>


namespace libmuscle { namespace _MUSCLE_IMPL_NS {

/** The MMSF Validator checks whether Instances are following the Multiscale
 *  Modelling and Simulation Framework when sending and receiving messages.
 *
 *  In particular it checks that in order:
 * 
 *  1. reuse_instance() is called
 *  2. Messages are received on all F_INIT ports
 *  3. The following sub-items happen in order, 0 or more times:
 * 
 *      a. Messages are sent on all O_I ports
 *      b. Messages are received on all S ports
 * 
 *  4. Messages are sent on all O_F ports
 * 
 *  If any message is sent or received out of order, a warning is logged to indicate
 *  that the instance is not following the MMSF pattern. In some cases (for example the
 *  time bridge in ``examples/python/interact_coupling.py``) this is expected and the
 *  warnings can be disabled by setting the SKIP_MMSF_SEQUENCE_CHECKS flag.
 * 
 *  Note:
 *      Checks on vector ports are not implemented. When the instance uses vector ports,
 *      the MMSF Validator will be disabled.
 */
class MMSFValidator {
    public:
        MMSFValidator(PortManager const & port_manager, Logger & logger);
        ~MMSFValidator() = default;

        /** Check that sending on the provided port adheres to the MMSF. */
        void check_send(std::string const & port_name, Optional<int> slot);
        /** Check that receiving on the provided port adheres to the MMSF. */
        void check_receive(std::string const & port_name, Optional<int> slot);
        /** Check that a reuse_instance() adheres to the MMSF. */
        void reuse_instance();
        /** Call when resuming from an intermediate snapshot: F_INIT is skipped. */
        void skip_f_init();

    private:
        /** Actual implementation of check_send/check_receive. */
        void check_send_receive_(std::string const & port_name, Optional<int> slot);
        /** Check that a transition to the provided operator is allowed.
         * 
         * Log a warning when the transition does not adhere to the MMSF.
         * 
         * @param op Operator to transition to.
         * @param port_name The name of the port that was sent/receveived on. This is only
         *      used for constructing the warning message.
         */
        void check_transition_(::ymmsl::Operator op, std::string const & port_name);

        PortManager const & port_manager_;
        Logger & logger_;
        std::unordered_map<::ymmsl::Operator, std::vector<std::string>> connected_ports_;
        std::unordered_map<std::string, ::ymmsl::Operator> port_operators_;
        std::unordered_map<::ymmsl::Operator, std::vector<::ymmsl::Operator>> allowed_transitions_;
        bool enabled_;

        // state tracking
        std::vector<std::string> current_ports_used_;
        ::ymmsl::Operator current_operator_;
};

} }
