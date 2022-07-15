/* This is a part of the integration test suite, and is run from a Python
 * test in /integration_test. It is not a unit test.
 */
#include <libmuscle/libmuscle.hpp>
#include <ymmsl/ymmsl.hpp>

#include <mpi.h>

#include <cassert>
#include <iostream>


using libmuscle::Data;
using libmuscle::DataConstRef;
using libmuscle::Instance;
using libmuscle::Message;
using ymmsl::Operator;


/** A simple dummy component for testing.
 */
void component(int argc, char * argv[]) {
    int rank, num_ranks;
    MPI_Comm_size(MPI_COMM_WORLD, &num_ranks);
    assert(num_ranks == 2);
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);

    Instance instance(argc, argv, {
            {Operator::F_INIT, {"init"}},       // int
            {Operator::O_I, {"out"}},           // int
            {Operator::S, {"in"}},              // int
            {Operator::O_F, {"result"}}});      // int

    while (instance.reuse_instance()) {
        // F_INIT
        std::cout << "Before F_INIT" << std::endl;
        Message default_init_msg(0.0, Data(0));
        auto init_msg = instance.receive("init", default_init_msg);

        int cur;
        if (rank == 0) {
            cur = init_msg.data().as<int>();
            MPI_Bcast(&cur, 1, MPI_INT, 0, MPI_COMM_WORLD);
        }
        else {
            MPI_Bcast(&cur, 1, MPI_INT, 0, MPI_COMM_WORLD);
        }

        for (int i = 0; i < 10; ++i) {
            // O_I
            std::cout << "Before O_I" << std::endl;
            Message out_msg(static_cast<double>(i), Data(i));
            instance.send("out", out_msg);

            // S
            std::cout << "Before S" << std::endl;
            auto in_msg = instance.receive("in", out_msg);
        }

        // O_F
        std::cout << "Before O_F" << std::endl;
        instance.send("result", init_msg);
    }
    std::cout << "Finishing successfully" << std::endl;
}


int main(int argc, char * argv[]) {
    MPI_Init(&argc, &argv);

    component(argc, argv);

    MPI_Finalize();
    return EXIT_SUCCESS;
}

