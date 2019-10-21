#pragma once

#ifdef MUSCLE_ENABLE_MPI

#include <memory>

#include <mpi.h>

#include <libmuscle/mcp/tcp_client.hpp>
#include <libmuscle/mcp/tcp_server.hpp>
#include <libmuscle/post_office.hpp>


namespace libmuscle { namespace impl {


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

        /** Whether this process is the root process, according to this barrier.
         *
         * @returns True if we're the root process.
         */
        bool is_root() const;

        /** Waits for the barrier to clear.
         *
         * Only call if you're not the root process!
         */
        void wait();

        /** Signals the blocked processes to continue.
         *
         * Only call from the root process!
         */
        void signal();


    private:
        int root_;
        MPI_Comm mpi_comm_;

        std::unique_ptr<PostOffice> post_office_;
        std::unique_ptr<mcp::TcpServer> server_;
        std::unique_ptr<mcp::TcpClient> client_;
};


} }

#endif

