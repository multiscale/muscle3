/* This is a part of the integration test suite, and is run from a Python
 * test in /integration_test. It is not a unit test.
 */
#include <cassert>

#include <libmuscle/libmuscle.hpp>
#include <ymmsl/ymmsl.hpp>

#include <mpi.h>


using libmuscle::Data;
using libmuscle::DataConstRef;
using libmuscle::Instance;
using libmuscle::InstanceFlags;
using libmuscle::Message;
using ymmsl::Operator;


void mpi_micro(int argc, char * argv[]) {
    MPI_Init(&argc, &argv);
    int rank, num_ranks;
    MPI_Comm_size(MPI_COMM_WORLD, &num_ranks);
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);

    Instance instance(
            argc, argv, {
                {Operator::F_INIT, {"f_i"}},
                {Operator::O_F, {"o_f"}}},
            InstanceFlags::USES_CHECKPOINT_API,
            MPI_COMM_WORLD, 0);

    while (instance.reuse_instance()) {
        double dt = instance.get_setting_as<double>("dt");
        double t_max = instance.get_setting_as<double>("t_max");
        double t_cur, t_stop;
        int i;

        if (instance.resuming()) {
            if (rank == 0) {
                auto msg = instance.load_snapshot();
                // load state from message
                t_cur = msg.timestamp();
                i = msg.data()[0].as<int>();
                t_stop = msg.data()[1].as<double>();
                // and broadcast
                MPI_Bcast(&t_cur, 1, MPI_DOUBLE, 0, MPI_COMM_WORLD);
                MPI_Bcast(&i, 1, MPI_INT, 0, MPI_COMM_WORLD);
                MPI_Bcast(&t_stop, 1, MPI_DOUBLE, 0, MPI_COMM_WORLD);
            } else {
                MPI_Bcast(&t_cur, 1, MPI_DOUBLE, 0, MPI_COMM_WORLD);
                MPI_Bcast(&i, 1, MPI_INT, 0, MPI_COMM_WORLD);
                MPI_Bcast(&t_stop, 1, MPI_DOUBLE, 0, MPI_COMM_WORLD);
            }
        }

        if (instance.should_init()) {
            if (rank == 0) {
                auto msg = instance.receive("f_i");
                t_cur = msg.timestamp();
                i = msg.data().as<int>();
                t_stop = t_cur + t_max;
                MPI_Bcast(&t_cur, 1, MPI_DOUBLE, 0, MPI_COMM_WORLD);
                MPI_Bcast(&i, 1, MPI_INT, 0, MPI_COMM_WORLD);
                MPI_Bcast(&t_stop, 1, MPI_DOUBLE, 0, MPI_COMM_WORLD);
            } else {
                MPI_Bcast(&t_cur, 1, MPI_DOUBLE, 0, MPI_COMM_WORLD);
                MPI_Bcast(&i, 1, MPI_INT, 0, MPI_COMM_WORLD);
                MPI_Bcast(&t_stop, 1, MPI_DOUBLE, 0, MPI_COMM_WORLD);
            }
        }

        while (t_cur <= t_stop) {
            // faux time-integration for testing snapshots
            t_cur += dt;

            if (instance.should_save_snapshot(t_cur)) {
                // [Optional] collectively gather state
                if (rank == 0) {
                    // Only root can save
                    instance.save_snapshot(Message(t_cur, Data::list(i, t_stop)));
                }
            }
        }

        // Message is only sent from root process
        instance.send("o_f", Message(t_cur, i));

        if (instance.should_save_final_snapshot()) {
            // [Optional] collectively gather state
            if (rank == 0) {
                // Only root can save
                instance.save_final_snapshot(Message(t_cur, Data::list(i, t_stop)));
            }
        }
    }
}


int main(int argc, char * argv[]) {
    mpi_micro(argc, argv);
    return EXIT_SUCCESS;
}

