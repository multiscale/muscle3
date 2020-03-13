#include <cmath>
#include <cstdlib>
#include <iostream>
#include <ostream>

#include <libmuscle/libmuscle.hpp>
#include <ymmsl/ymmsl.hpp>

using libmuscle::Data;
using libmuscle::Instance;
using libmuscle::Message;
using ymmsl::Operator;


/* Calculates the Laplacian of vector Z.
 *
 * @param Z A vector representing a series of samples along a line.
 * @param dx The spacing between the samples.
 */
std::vector<double> laplacian(std::vector<double> const & Z, double dx) {
    std::vector<double> result(Z.size() - 2);
    for (std::size_t i = 0u; i < result.size(); ++i)
        result[i] = (Z[i] + Z[i+2] - 2.0 * Z[i+1]) / (dx * dx);
    return result;
}


/** A simple diffusion model on a 1d grid.
 *
 * The state of this model is a 1D grid of concentrations. It sends out the
 * state on each timestep on 'state_out', and can receive an updated state
 * on 'state_in' at each state update.
 */
void diffusion(int argc, char * argv[]) {
    Instance instance(argc, argv, {
            {Operator::O_I, {"state_out"}},
            {Operator::S, {"state_in"}},
            {Operator::O_F, {"final_state_out"}}});

    while (instance.reuse_instance()) {
        // F_INIT
        double t_max = instance.get_setting_as<double>("t_max");
        double dt = instance.get_setting_as<double>("dt");
        double x_max = instance.get_setting_as<double>("x_max");
        double dx = instance.get_setting_as<double>("dx");
        double d = instance.get_setting_as<double>("d");

        std::vector<double> U(lrint(x_max / dx), 1e-20);
        U[25] = 2.0;
        U[50] = 2.0;
        U[75] = 2.0;

        std::vector<std::vector<double>> Us;
        Us.push_back(U);

        double t_cur = 0.0;
        while (t_cur + dt <= t_max) {
            std::cerr << "t_cur: " << t_cur << ", t_max: " << t_max << std::endl;
            // O_I
            auto data = Data::nils(U.size());
            for (std::size_t i = 0u; i < U.size(); ++i)
                data[i] = U[i];

            Message cur_state_msg(t_cur, data);
            double t_next = t_cur + dt;
            if (t_next + dt <= t_max)
                cur_state_msg.set_next_timestamp(t_next);
            instance.send("state_out", cur_state_msg);

            // S
            auto msg = instance.receive("state_in", cur_state_msg);
            for (std::size_t i = 0u; i < msg.data().size(); ++i)
                U[i] = msg.data()[i].as<double>();

            std::vector<double> dU(U.size());
            auto lpl = laplacian(U, dx);
            for (std::size_t i = 1u; i < dU.size() - 1; ++i)
                dU[i] = d * lpl[i-1] * dt;
            dU[0] = dU[1];
            dU[dU.size() - 1] = dU[dU.size() - 2];

            for (std::size_t i = 0u; i < dU.size(); ++i)
                U[i] += dU[i];

            Us.push_back(U);
            t_cur += dt;
        }

        // O_F
        auto data = Data::nils(U.size());
        for (std::size_t i = 0u; i < U.size(); ++i)
            data[i] = U[i];
        instance.send("final_state_out", Message(t_cur, data));
        std::cerr << "All done" << std::endl;
    }
}


int main(int argc, char * argv[]) {
    diffusion(argc, argv);
    return EXIT_SUCCESS;
}

