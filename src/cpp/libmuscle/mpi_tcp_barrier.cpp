#include <libmuscle/mpi_tcp_barrier.hpp>
#include <libmuscle/mcp/tcp_transport_client.hpp>
#include <libmuscle/mcp/tcp_transport_server.hpp>
#include <libmuscle/post_office.hpp>

#ifdef MUSCLE_ENABLE_MPI

#include <mpi.h>

#endif

#include <memory>
#include <sstream>
#include <string>


using libmuscle::_MUSCLE_IMPL_NS::mcp::TcpTransportClient;
using libmuscle::_MUSCLE_IMPL_NS::mcp::TcpTransportServer;


namespace libmuscle { namespace _MUSCLE_IMPL_NS {


MPITcpBarrier::MPITcpBarrier(MPI_Comm const & communicator, int root)
    : root_(root)
{
#ifdef MUSCLE_ENABLE_MPI
    MPI_Comm_dup(communicator, &mpi_comm_);

    if (is_root_()) {
        server_ = std::make_unique<MPPServer>();

        std::string addr = server_->get_locations().front();
        int addr_size = addr.size();
        MPI_Bcast(&addr_size, 1, MPI_INT, root_, mpi_comm_);
        MPI_Bcast(&addr[0], addr_size, MPI_SIGNED_CHAR, root_, mpi_comm_);
    }
    else {
        int addr_size;
        MPI_Bcast(&addr_size, 1, MPI_INT, root_, mpi_comm_);
        std::string addr(addr_size, ' ');
        MPI_Bcast(&addr[0], addr_size, MPI_SIGNED_CHAR, root_, mpi_comm_);
        std::vector<std::string> addrs = {addr};
        client_ = std::make_unique<MPPClient>(addrs);
    }
#endif
}


void MPITcpBarrier::operator()() {
#ifdef MUSCLE_ENABLE_MPI
    int rank;
    MPI_Comm_rank(mpi_comm_, &rank);
    if (rank == root_) {
        int num_ranks;
        MPI_Comm_size(mpi_comm_, &num_ranks);
        for (int i = 0; i < num_ranks; ++i)
            if (i != root_) {
                std::ostringstream oss;
                oss << "rank[" << i << "]";
                std::vector<char> msg;
                server_->deposit(oss.str(), std::move(msg));
            }
    }
    else {
        std::ostringstream oss;
        oss << "rank[" << rank << "]";
        client_->receive(oss.str());
    }
#endif
}


void MPITcpBarrier::shutdown() {
#ifdef MUSCLE_ENABLE_MPI
    if (is_root_())
        server_->shutdown();
    else
        client_->close();
    MPI_Comm_free(&mpi_comm_);
#endif
}


bool MPITcpBarrier::is_root_() const {
#ifdef MUSCLE_ENABLE_MPI
    int rank;
    MPI_Comm_rank(mpi_comm_, &rank);
    return rank == root_;
#else
    return true;
#endif
}

} }

