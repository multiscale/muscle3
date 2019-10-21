/* This is a part of the integration test suite, and is run from a Python
 * test in /integration_test. It is not a unit test.
 */
#include <libmuscle/libmuscle.hpp>
#include <ymmsl/ymmsl.hpp>

#include <mpi.h>

#include <cassert>
#include <sstream>


using libmuscle::Instance;
using libmuscle::Message;
using ymmsl::Operator;


int main(int argc, char *argv[]) {
    MPI_Init(&argc, &argv);
    int rank, num_ranks;
    MPI_Comm_size(MPI_COMM_WORLD, &num_ranks);
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);

    Instance instance(argc, argv, {
            {Operator::F_INIT, {"in"}},
            {Operator::O_F, {"out"}}});

    int i = 0;
    while (instance.reuse_instance()) {
        // F_INIT
        assert(instance.get_setting_as<int64_t>("test1") == 13);
        assert(instance.get_setting_as<bool>("test4") == true);

        auto msg = instance.receive("in");

        std::string message;
        int size;
        if (rank == 0) {
            message = msg.data().as<std::string>();
            size = message.size();
            MPI_Bcast(&size, 1, MPI_INT, 0, MPI_COMM_WORLD);
            MPI_Bcast(&message[0], size, MPI_SIGNED_CHAR, 0, MPI_COMM_WORLD);
        }
        else {
            MPI_Bcast(&size, 1, MPI_INT, 0, MPI_COMM_WORLD);
            message = std::string(size, ' ');
            MPI_Bcast(&message[0], size, MPI_SIGNED_CHAR, 0, MPI_COMM_WORLD);
        }

        assert(message == "testing");

        // O_F
        std::ostringstream reply;
        reply << "testing back " << i;
        instance.send("out", Message(msg.timestamp(), reply.str()));
        ++i;
    }

    MPI_Finalize();
    return 0;
}

