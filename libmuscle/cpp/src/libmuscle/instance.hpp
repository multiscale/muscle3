#pragma once

#include <libmuscle/communicator.hpp>
#include <libmuscle/mmp_client.hpp>
#include <libmuscle/settings_manager.hpp>

#include <ymmsl/identity.hpp>


namespace libmuscle {

/** Represents a compute element instance in a MUSCLE3 simulation.
 *
 * This class provides a low-level send/receive API for the instance to use.
 */
class Instance {
    public:
        /** Create an instance.
         *
         * @param argc The number of command-line arguments.
         * @param argv Command line arguments.
         */
        Instance(int argc, char const * const argv[]);

        /** Create an instance.
         *
         * A PortsDescription can be written like this:
         *
         * PortsDescription ports({
         *     {Operator::F_INIT, {"port1", "port2"}},
         *     {Operator::O_F, {"port3[]"}}
         *     });
         *
         * @param argc The number of command-line arguments.
         * @param argv Command line arguments.
         * @param ports A description of the ports that this instance has.
         */
        Instance(int argc, char const * const argv[],
                PortsDescription const & ports);

    private:
        ::ymmsl::Reference instance_name_;
        MMPClient manager_;
        Communicator communicator_;
        PortsDescription declared_ports_;
        SettingsManager settings_manager_;
        bool first_run_;
        std::unordered_map<::ymmsl::Reference, Message> f_init_cache_;

        ::ymmsl::Reference make_full_name_(int argc, char const * const argv[]) const;
        std::string extract_manager_location_(int argc, char const * const argv[]) const;
        ::ymmsl::Reference name_() const;
        std::vector<int> index_() const;
        std::vector<::ymmsl::Port> list_declared_ports_() const;
        void register_();
        void connect_();

        friend class TestInstance;
};

}

