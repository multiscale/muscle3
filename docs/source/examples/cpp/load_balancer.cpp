#include <cstdlib>
#include <cinttypes>
#include <random>

#include <libmuscle/libmuscle.hpp>
#include <ymmsl/ymmsl.hpp>


using libmuscle::Data;
using libmuscle::Instance;
using libmuscle::InstanceFlags;
using libmuscle::Message;
using ymmsl::Operator;
using ymmsl::Settings;


/* A proxy which divides many calls over few instances.
 *
 * Put this component between a driver and a set of models, or between a
 * macro model and a set of micro models. It will let the driver or macro-
 * model submit as many calls as it wants, and divide them over the available
 * (micro)model instances in a round-robin fashion.
 *
 * Assumes a fixed number of micro-model instances.
 */
void load_balancer(int argc, char * argv[]) {
    Instance instance(argc, argv, {
            {Operator::F_INIT, {"front_in[]"}},
            {Operator::O_I, {"back_out[]"}},
            {Operator::S, {"back_in[]"}},
            {Operator::O_F, {"front_out[]"}}},
            InstanceFlags::DONT_APPLY_OVERLAY);

    while (instance.reuse_instance()) {
        // F_INIT
        int started = 0;
        int done = 0;

        int num_calls = instance.get_port_length("front_in");
        int num_workers = instance.get_port_length("back_out");

        instance.set_port_length("front_out", num_calls);

        while (done < num_calls) {
            while ((started - done < num_workers) && (started < num_calls)) {
                auto msg = instance.receive_with_settings("front_in", started);
                instance.send("back_out", msg, started % num_workers);
                ++started;
            }
            auto msg = instance.receive_with_settings("back_in", done % num_workers);
            instance.send("front_out", msg, done);
            ++done;
        }
    }
}


int main(int argc, char * argv[]) {
    load_balancer(argc, argv);
    return EXIT_SUCCESS;
}

