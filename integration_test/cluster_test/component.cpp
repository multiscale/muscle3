#include <cstdlib>
#include <fstream>
#include <string>

#include <unistd.h>

#include "mpi.h"

#include "libmuscle/libmuscle.hpp"
#include "ymmsl/ymmsl.hpp"

using std::ofstream;
using std::to_string;

using libmuscle::Instance;
using libmuscle::Message;
using ymmsl::Operator;


/** A simple dummy component. */
void component(int argc, char * argv[]) {
    const int root_rank = 0;
    int rank;
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);

    char nodeid[1024];
    gethostname(nodeid, sizeof(nodeid));

    {
        ofstream outfile("out_" + to_string(rank) + ".txt");
        outfile << nodeid << std::endl;
    }

    Instance instance(argc, argv, {
            {Operator::F_INIT, {"init_in"}},
            {Operator::O_I, {"inter_out"}},
            {Operator::S, {"inter_in"}},
            {Operator::O_F, {"final_out"}}},
            MPI_COMM_WORLD, root_rank);

    // outfile << "Starting reuse loop" << std::endl;
    while (instance.reuse_instance()) {
        // F_INIT

        int64_t steps = instance.get_setting_as<int64_t>("steps");

        instance.receive("init_in", Message(0.0));

        for (int step = 0; step < steps; ++step) {
            // O_I
            if (rank == root_rank) {
                instance.send("inter_out", Message(step));
            }

            // S
            instance.receive("inter_in", Message(0.0));
        }

        // O_F
        if (rank == root_rank) {
            instance.send("final_out", Message(steps));
        }
    }
}


int main(int argc, char * argv[]) {
    MPI_Init(&argc, &argv);
    component(argc, argv);
    MPI_Finalize();
    return EXIT_SUCCESS;
}

