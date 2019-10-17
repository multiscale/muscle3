#include <cstdlib>

#include <libmuscle/libmuscle.hpp>
#include <ymmsl/ymmsl.hpp>


using libmuscle::Data;
using libmuscle::Instance;
using libmuscle::Message;
using ymmsl::Operator;


/** A simple exponential reaction model on a 1D grid.
 */
void reaction(int argc, char * argv[]) {
    Instance instance(argc, argv, {
            {Operator::F_INIT, {"initial_state"}},  // list of float
            {Operator::O_F, {"final_state"}}});     // list of float

    while (instance.reuse_instance()) {
        // F_INIT
        double t_max = instance.get_setting_as<double>("t_max");
        double dt = instance.get_setting_as<double>("dt");
        double k = instance.get_setting_as<double>("k");

        auto msg = instance.receive("initial_state");
        std::vector<double> U(msg.data().size());
        for (int i = 0; i < msg.data().size(); ++i)
            U[i] = msg.data()[i].as<double>();

        double t_cur = msg.timestamp();
        while (t_cur + dt < t_max) {
            // O_I

            // S
            for (double & u : U)
                u += k * u * dt;
            t_cur += dt;
        }

        // O_F
        auto result = Data::nils(U.size());
        for (int i = 0; i < U.size(); ++i)
            result[i] = U[i];
        instance.send("final_state", Message(t_cur, result));
    }
}


int main(int argc, char * argv[]) {
    reaction(argc, argv);
    return EXIT_SUCCESS;
}

