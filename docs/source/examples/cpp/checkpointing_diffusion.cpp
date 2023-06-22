#include <cmath>
#include <cstdlib>
#include <iostream>
#include <ostream>
#include <vector>

#include <libmuscle/libmuscle.hpp>
#include <ymmsl/ymmsl.hpp>

using libmuscle::Data;
using libmuscle::Instance;
using libmuscle::InstanceFlags;
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


/** Utility function packing data in a message for snapshotting
 */
Message create_state_message(
        double t_cur, std::vector<std::vector<double>> const & Us)
{
    Data data = Data::nils(Us.size());
    for (std::size_t i = 0; i < data.size(); ++i)
        data[i] = Data::grid(Us[i].data(), {Us[i].size()});
    return Message(t_cur, data);
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
            {Operator::O_F, {"final_state_out"}}},
            InstanceFlags::USES_CHECKPOINT_API);

    while (instance.reuse_instance()) {
        // F_INIT
        double t_max = instance.get_setting_as<double>("t_max");
        double dt = instance.get_setting_as<double>("dt");
        double x_max = instance.get_setting_as<double>("x_max");
        double dx = instance.get_setting_as<double>("dx");
        double d = instance.get_setting_as<double>("d");

        double t_cur;
        std::vector<std::vector<double>> Us;
        std::vector<double> U(lrint(x_max / dx), 1e-20);

        if (instance.resuming()) {
            auto msg = instance.load_snapshot();
            for (int i = 0; i < msg.data().size(); ++i) {
                auto const & data_i = msg.data()[i];
                if (data_i.shape().size() != 1u || data_i.size() != U.size()) {
                    auto err_msg = "Received state of incorrect shape or size!";
                    instance.error_shutdown(err_msg);
                    throw std::runtime_error(err_msg);
                }
                std::copy_n(data_i.elements<double>(), data_i.size(), U.begin());
                Us.push_back(U);
            }
            t_cur = msg.timestamp();
        }

        if (instance.should_init()) {
            U = std::vector<double>(lrint(x_max / dx), 1e-20);
            U[25] = 2.0;
            U[50] = 2.0;
            U[75] = 2.0;

            Us.push_back(U);

            t_cur = 0.0;
        }

        while (t_cur + dt <= t_max) {
            std::cerr << "t_cur: " << t_cur << ", t_max: " << t_max << std::endl;
            // O_I
            auto data = Data::grid(U.data(), {U.size()}, {"x"});
            Message cur_state_msg(t_cur, data);
            double t_next = t_cur + dt;
            if (t_next + dt <= t_max)
                cur_state_msg.set_next_timestamp(t_next);
            instance.send("state_out", cur_state_msg);

            // S
            auto msg = instance.receive("state_in", cur_state_msg);
            if (msg.data().shape().size() != 1u || msg.data().size() != U.size()) {
                auto msg = "Received state of incorrect shape or size!";
                instance.error_shutdown(msg);
                throw std::runtime_error(msg);
            }
            std::copy_n(msg.data().elements<double>(), msg.data().size(), U.begin());

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

            if (instance.should_save_snapshot(t_cur)) {
                instance.save_snapshot(create_state_message(t_cur, Us));
            }
        }

        // O_F
        auto data = Data::grid(U.data(), {U.size()}, {"x"});
        instance.send("final_state_out", Message(t_cur, data));
        std::cerr << "All done" << std::endl;


        if (instance.should_save_final_snapshot()) {
            instance.save_snapshot(create_state_message(t_cur, Us));
        }
    }
}


int main(int argc, char * argv[]) {
    diffusion(argc, argv);
    return EXIT_SUCCESS;
}

