#include <cstdlib>
#include <fstream>
#include <string>

// This is a Linux-specific API, but this test always runs on Linux so that's okay.
#define _GNU_SOURCE
#include <sched.h>
#include <unistd.h>

#include "mpi.h"

#include "libmuscle/libmuscle.hpp"
#include "ymmsl/ymmsl.hpp"

using std::ofstream;
using std::to_string;

using libmuscle::Instance;
using libmuscle::Message;
using ymmsl::Operator;


/** Log where we are running so that the test can check for it. */
void log_location() {
    int rank;
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);

    char nodeid[1024];
    gethostname(nodeid, sizeof(nodeid));

    cpu_set_t cpu_set;
    CPU_ZERO(&cpu_set);
    sched_getaffinity(0, sizeof(cpu_set_t), &cpu_set);

    {
        ofstream outfile("out_" + to_string(rank) + ".txt");
        outfile << nodeid << std::endl;

        bool first = true;
        for (int i = 0; i < CPU_SETSIZE; ++i) {
            if (CPU_ISSET(i, &cpu_set)) {
                if (!first)
                    outfile << ",";
                outfile << i;
                first = false;
            }
        }
        outfile << std::endl;
    }
}


/** A simple dummy component. */
void component(int argc, char * argv[]) {
    const int root_rank = 0;
    int rank;
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);

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
    log_location();
    component(argc, argv);
    MPI_Finalize();
    return EXIT_SUCCESS;
}

