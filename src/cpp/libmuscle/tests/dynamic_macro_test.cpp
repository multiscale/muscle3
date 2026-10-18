/* This is a part of the integration test suite, and is run from a Python
 * test in /integration_test. It is not a unit test.
 */
#include <cassert>
#include <algorithm>

#include <libmuscle/libmuscle.hpp>
#include <ymmsl/ymmsl.hpp>


using libmuscle::Data;
using libmuscle::DataConstRef;
using libmuscle::Instance;
using libmuscle::Message;
using ymmsl::Operator;


/** A simple dynamic component for testing.
 */
void component(int argc, char * argv[]) {
    Instance instance(argc, argv);

    while (instance.reuse_instance()) {
        auto ports = instance.list_ports();

        assert(ports.at(Operator::F_INIT) == std::vector<std::string>({"f_init"}));
        // port order may be scrambled by std::unordered_map, so need to sort first...
        std::vector<std::string> oi_ports(ports.at(Operator::O_I));
        std::sort(oi_ports.begin(), oi_ports.end());
        assert(oi_ports == std::vector<std::string>({"o_i", "out2"}));
        assert(ports.at(Operator::S) == std::vector<std::string>({"s"}));
        assert(ports.at(Operator::O_F) == std::vector<std::string>({"o_f"}));

        assert(!instance.is_connected("f_init"));
        assert(instance.is_connected("o_i"));
        assert(!instance.is_connected("out2"));
        assert(instance.is_connected("s"));
        assert(!instance.is_connected("o_f"));

        // Send a message so that we're sure that dynamic_micro runs
        instance.send("o_i", Message(0.0));
        instance.receive("s");
    }
}


int main(int argc, char * argv[]) {
    component(argc, argv);
    return EXIT_SUCCESS;
}

