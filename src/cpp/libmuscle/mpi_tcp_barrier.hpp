#pragma once


#include <memory>

#ifdef MUSCLE_ENABLE_MPI

#include <mpi.h>

#endif

#include <libmuscle/mpp_client.hpp>
#include <libmuscle/mpp_server.hpp>
#include <libmuscle/namespace.hpp>
#include <libmuscle/util.hpp>


namespace libmuscle { namespace _MUSCLE_IMPL_NS {


/** A barrier for MPI processes that uses TCP to communicate.
 *
 * MPI spinloops on barriers, so that a model would eat all CPU while waiting
 * to receive a MUSCLE message. This provides an alternative that allows
 * blocking the processes.
 */
class MPITcpBarrier {
    public:
        /** Create an MPITcpBarrier.
         *
         * This sets up a server if we are root, and a client if we're not.
         */
        MPITcpBarrier(MPI_Comm const & communicator = MPI_COMM_WORLD, int root = 0);

        /** Apply the barrier.
         *
         * This signals on the root process and waits on all other processes.
         */
        void operator()();

        /** Shuts down the barrier, closing connections.
         */
        void shutdown();

    private:
        int root_;
        MPI_Comm mpi_comm_;

        std::unique_ptr<MPPServer> server_;
        std::unique_ptr<MPPClient> client_;

        bool is_root_() const;
};


} }

