#include <libmuscle/instance.hpp>

#include <libmuscle/mmp_client.hpp>
#include <ymmsl/identity.hpp>

#include <stdexcept>


using ymmsl::Reference;

namespace libmuscle {

Instance::Instance(int argc, char const * const argv[])
    : instance_name_(make_full_name_(argc, argv))
    , manager_(extract_manager_location_(argc, argv))
    , communicator_(name_(), index_(), {}, 0)
    , declared_ports_()
    , settings_manager_()
    , first_run_(true)
    , f_init_cache_()
{
    register_();
    connect_();
}

Instance::Instance(int argc, char const * const argv[],
                   PortsDescription const & ports)
    : instance_name_(make_full_name_(argc, argv))
    , manager_(extract_manager_location_(argc, argv))
    , communicator_(name_(), index_(), {}, 0)
    , declared_ports_(ports)
    , settings_manager_()
    , first_run_(true)
    , f_init_cache_()
{
    register_();
    connect_();
}


/* Returns instance name.
 *
 * This takes the argument to the --muscle-instance= command-line option and
 * returns it as a Reference.
 */
Reference Instance::make_full_name_(int argc, char const * const argv[]) const {
    std::string prefix_tag("--muscle-instance=");
    for (int i = 1; i < argc; ++i) {
        if (strncmp(argv[i], prefix_tag.c_str(), prefix_tag.size()) == 0) {
            std::string prefix_str(argv[i] + prefix_tag.size());
            return Reference(prefix_str);
        }
    }
    throw std::runtime_error("A --muscle-instance command line argument is"
            " required to identify this instance. Please add one.");
}

/* Gets the manager network location from the command line.
 *
 * We use a --muscle-manager=<host:port> argument to tell the MUSCLE library
 * how to connect to the manager. This function will extract this argument
 * from the command line arguments, if it is present.
 */
std::string Instance::extract_manager_location_(
        int argc, char const * const argv[]) const
{
    std::string prefix_tag("--muscle-manager=");
    for (int i = 1; i < argc; ++i)
        if (strncmp(argv[i], prefix_tag.c_str(), prefix_tag.size()) == 0)
            return std::string(argv[i] + prefix_tag.size());

    return "localhost:9000";
}

/* Returns the compute element name of this instance, i.e. without the index.
 */
Reference Instance::name_() const {
    auto it = instance_name_.cbegin();
    while (it != instance_name_.cend() && it->is_identifier())
        ++it;

    return Reference(instance_name_.cbegin(), it);
}

/* Returns the index of this instance, i.e. without the compute element.
 */
std::vector<int> Instance::index_() const {
    std::vector<int> result;
    auto it = instance_name_.cbegin();
    while (it != instance_name_.cend() && it->is_identifier())
        ++it;

    while (it != instance_name_.cend() && it->is_index()) {
        result.push_back(it->index());
        ++it;
    }
    return result;
}

/* Returns a list of declared ports for this instance.
 *
 * This returns a list of ymmsl::Port objects, which have only the name and
 * operator, not libmuscle::Port, which has more.
 */
std::vector<::ymmsl::Port> Instance::list_declared_ports_() const {
    std::vector<::ymmsl::Port> result;
    for (auto const & oper_ports : declared_ports_) {
        for (auto const & fullname : oper_ports.second) {
            std::string portname(fullname);
            if (fullname.size() > 2 && fullname.substr(fullname.size() - 2) == "[]")
                portname = fullname.substr(0, fullname.size() - 2);
            result.push_back(::ymmsl::Port(portname, oper_ports.first));
        }
    }
    return result;
}

/* Register this instance with the manager.
 */
void Instance::register_() {
    // TODO: profile this
    auto locations = communicator_.get_locations();
    auto port_list = list_declared_ports_();
    manager_.register_instance(instance_name_, locations, port_list);
    // TODO: stop profile
}

/* Connect this instance to the given peers / conduits.
 */
void Instance::connect_() {
    // TODO: profile this
    auto peer_info = manager_.request_peers(instance_name_);
    communicator_.connect(std::get<0>(peer_info), std::get<1>(peer_info), std::get<2>(peer_info));
    settings_manager_.base = manager_.get_settings();
    // TODO: stop profile
}

}

