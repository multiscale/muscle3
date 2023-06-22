#include <cstdlib>
#include <vector>

#include <libmuscle/libmuscle.hpp>
#include <ymmsl/ymmsl.hpp>


using libmuscle::Data;
using libmuscle::DataConstRef;
using libmuscle::Instance;
using libmuscle::InstanceFlags;
using libmuscle::Message;
using ymmsl::Operator;


/** A simple exponential reaction model on a 1D grid.
 */
void reaction(int argc, char * argv[]) {
    Instance instance(argc, argv, {
            {Operator::F_INIT, {"initial_state"}},  // 1D Grid
            {Operator::O_F, {"final_state"}}},      // 1D Grid
            InstanceFlags::KEEPS_NO_STATE_FOR_NEXT_USE);

    while (instance.reuse_instance()) {

        // F_INIT
        double t_max = instance.get_setting_as<double>("t_max");
        double dt = instance.get_setting_as<double>("dt");
        double k = instance.get_setting_as<double>("k");

        auto msg = instance.receive("initial_state");
        auto data_ptr = msg.data().elements<double>();
        std::vector<double> U(data_ptr, data_ptr + msg.data().size());

        double t_cur = msg.timestamp();
        while (t_cur + dt < msg.timestamp() + t_max) {
            // O_I

            // S
            for (double & u : U)
                u += k * u * dt;
            t_cur += dt;
        }

        // O_F
        auto result = Data::grid(U.data(), {U.size()}, {"x"});
        instance.send("final_state", Message(t_cur, result));
    }
}


int main(int argc, char * argv[]) {
    reaction(argc, argv);
    return EXIT_SUCCESS;
}

