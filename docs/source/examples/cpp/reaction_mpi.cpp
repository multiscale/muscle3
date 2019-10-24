#include <cstdlib>

#include <mpi.h>

#include <libmuscle/libmuscle.hpp>
#include <ymmsl/ymmsl.hpp>


using libmuscle::Data;
using libmuscle::DataConstRef;
using libmuscle::Instance;
using libmuscle::Message;
using ymmsl::Operator;


/** A simple exponential reaction model on a 1D grid. MPI version.
 */
void reaction(int argc, char * argv[]) {
    const int root_rank = 0;
    int rank, num_ranks;
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    MPI_Comm_size(MPI_COMM_WORLD, &num_ranks);

    Instance instance(argc, argv, {
            {Operator::F_INIT, {"initial_state"}},  // list of double
            {Operator::O_F, {"final_state"}}},      // list of double
            MPI_COMM_WORLD, root_rank);

    while (instance.reuse_instance()) {
        // F_INIT
        double t_max = instance.get_setting_as<double>("t_max");
        double dt = instance.get_setting_as<double>("dt");
        double k = instance.get_setting_as<double>("k");

        std::vector<double> U, U_all;
        int U_size;
        double t_cur, t_end;

        auto msg = instance.receive("initial_state");

        if (rank == root_rank) {
            DataConstRef data(msg.data());
            U_all.resize(data.size());
            for (int i = 0; i < data.size(); ++i)
                U_all[i] = data[i].as<double>();

            t_cur = msg.timestamp();
            t_end = t_cur + t_max;

            U_size = U_all.size() / num_ranks;
            if (U_size * num_ranks != U_all.size()) {
                instance.error_shutdown("State does not divide evenly");
                throw std::runtime_error("State does not divide evenly");
            }
        }
        MPI_Bcast(&U_size, 1, MPI_INT, root_rank, MPI_COMM_WORLD);
        U.resize(U_size);
        MPI_Scatter(U_all.data(), U_size, MPI_DOUBLE,
                    U.data(), U_size, MPI_DOUBLE,
                    root_rank, MPI_COMM_WORLD);

        MPI_Bcast(&t_cur, 1, MPI_DOUBLE, root_rank, MPI_COMM_WORLD);
        MPI_Bcast(&t_end, 1, MPI_DOUBLE, root_rank, MPI_COMM_WORLD);

        while (t_cur + dt < t_end) {
            // O_I

            // S
            for (double & u : U)
                u += k * u * dt;
            t_cur += dt;
        }

        // O_F
        MPI_Gather(U.data(), U_size, MPI_DOUBLE,
                   U_all.data(), U_size, MPI_DOUBLE,
                   root_rank, MPI_COMM_WORLD);

        if (rank == 0) {
            auto result = Data::nils(U_all.size());
            for (int i = 0; i < U_all.size(); ++i)
                result[i] = U_all[i];
            instance.send("final_state", Message(t_cur, result));
        }
    }
}


int main(int argc, char * argv[]) {
    MPI_Init(&argc, &argv);
    reaction(argc, argv);
    MPI_Finalize();
    return EXIT_SUCCESS;
}

