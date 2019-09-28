#include <libmuscle/instance.hpp>

#include <libmuscle/mmp_client.hpp>
#include <ymmsl/identity.hpp>

#include <stdexcept>


using ymmsl::Reference;

namespace libmuscle {

Instance::Instance(int argc, char const * const argv[])
    : instance_name_(make_full_name_(argc, argv))
    , manager_(extract_manager_location_(argc, argv))
{}


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

}

