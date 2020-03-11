#include <cstdlib>
#include <cinttypes>
#include <random>

#include <libmuscle/libmuscle.hpp>
#include <ymmsl/ymmsl.hpp>


using libmuscle::Data;
using libmuscle::Instance;
using libmuscle::Message;
using ymmsl::Operator;
using ymmsl::Settings;

#include <iostream>
#include <ostream>


/* A driver for plain Monte Carlo Uncertainty Quantification.
 *
 * This component attaches to a collection of model instances, and feeds
 * in different parameter values generated pseudorandomly.
 *
 * Note that this uses pseudorandom numbers rather than a Sobol sequence
 * like in the Python example, so as to avoid a dependency on a Sobol
 * library. If you want to practice a bit, try splitting off the
 * Sobol-based qmc driver from the Python example into a separate file,
 * then run it instead of this component with the rest of the C++
 * simulation.
 */
void mc_driver(int argc, char * argv[]) {
    Instance instance(argc, argv, {
            {Operator::O_I, {"parameters_out[]"}},
            {Operator::S, {"states_in[]"}},
            {Operator::O_F, {"mean_out"}}});

    while (instance.reuse_instance()) {
        // F_INIT
        // get and check parameter distributions
        int64_t n_samples = instance.get_setting_as<int64_t>("n_samples");
        double d_min = instance.get_setting_as<double>("d_min");
        double d_max = instance.get_setting_as<double>("d_max");
        double k_min = instance.get_setting_as<double>("k_min");
        double k_max = instance.get_setting_as<double>("k_max");

        if (d_max < d_min) {
            instance.error_shutdown("Invalid settings: d_max < d_min");
            exit(1);
        }
        if (k_max < k_min) {
            instance.error_shutdown("Invalid settings: k_max < k_min");
            exit(1);
        }

        // generate UQ parameter values
        std::uniform_real_distribution<double> d_dist(d_min, d_max);
        std::uniform_real_distribution<double> k_dist(k_min, k_max);
        std::default_random_engine generator;
        std::vector<double> ds(n_samples), ks(n_samples);
        for (int i = 0; i < n_samples; ++i) {
            ds[i] = d_dist(generator);
            ks[i] = k_dist(generator);
        }

        // configure output port
        if (!instance.is_resizable("parameters_out")) {
                instance.error_shutdown("This component needs a resizable"
                    " parameters_out port, but it is connected to something"
                    " that cannot be resized. Maybe try adding a load"
                    " balancer.");
                exit(1);
        }

        instance.set_port_length("parameters_out", n_samples);

        std::vector<std::vector<double>> Us;

        // run ensemble
        // O_I
        for (int sample = 0; sample < n_samples; ++sample) {
            Settings uq_parameters;
            uq_parameters["d"] = ds[sample];
            uq_parameters["k"] = ks[sample];
            Message msg(0.0, uq_parameters);
            instance.send("parameters_out", msg, sample);
        }

        // S
        std::cerr << "Entering S" << std::endl;
        double t_max = 0.0;
        for (int sample = 0; sample < n_samples; ++sample) {
            std::cerr << "Receiving states_in[" << sample << "]" << std::endl;
            Message msg = instance.receive_with_settings("states_in", sample);
            auto data_ptr = msg.data().elements<double>();
            std::vector<double> U(data_ptr, data_ptr + msg.data().size());

            Us.push_back(U);
            t_max = std::max(t_max, msg.timestamp());
        }

        // calculate mean
        std::size_t domain_size = Us[0].size();
        auto means = Data::nils(domain_size);

        for (int i = 0; i < domain_size; ++i) {
            double sum = 0.0;
            for (int j = 0; j < n_samples; ++j)
                sum += Us[j][i];
            means[i] = sum / n_samples;
        }
        instance.send("mean_out", Message(t_max, means));
    }
}


int main(int argc, char * argv[]) {
    mc_driver(argc, argv);
    return EXIT_SUCCESS;
}

