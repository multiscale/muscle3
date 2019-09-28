#include <libmuscle/instance.hpp>

#include <ymmsl/identity.hpp>

#include <stdexcept>


using ymmsl::Reference;

namespace libmuscle {

Instance::Instance(int argc, char const * const argv[])
    : instance_name_(make_full_name_(argc, argv))
{}



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

}

