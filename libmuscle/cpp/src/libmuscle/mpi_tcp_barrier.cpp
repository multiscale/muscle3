#ifdef MUSCLE_ENABLE_MPI

#include <libmuscle/mpi_tcp_barrier.hpp>
#include <libmuscle/mcp/tcp_transport_client.hpp>
#include <libmuscle/mcp/tcp_transport_server.hpp>
#include <libmuscle/post_office.hpp>

#include <mpi.h>

#include <memory>
#include <sstream>
#include <string>


using libmuscle::_MUSCLE_IMPL_NS::mcp::TcpTransportClient;
using libmuscle::_MUSCLE_IMPL_NS::mcp::TcpTransportServer;


namespace libmuscle { namespace _MUSCLE_IMPL_NS {


MPITcpBarrier::MPITcpBarrier(MPI_Comm const & communicator, int root)
    : root_(root)
{
    MPI_Comm_dup(communicator, &mpi_comm_);

    if (is_root()) {
        post_office_ = std::make_unique<PostOffice>();
        server_ = std::make_unique<TcpTransportServer>(*post_office_);

        std::string addr = server_->get_location();
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
}

void MPITcpBarrier::shutdown() {
    if (is_root())
        server_->close();
    else
        client_->close();
    MPI_Comm_free(&mpi_comm_);
}

bool MPITcpBarrier::is_root() const {
    int rank;
    MPI_Comm_rank(mpi_comm_, &rank);
    return rank == root_;
}

void MPITcpBarrier::wait() {
    int rank;
    MPI_Comm_rank(mpi_comm_, &rank);
    std::ostringstream oss;
    oss << "rank[" << rank << "]";
    client_->receive(oss.str());
}

void MPITcpBarrier::signal() {
    int num_ranks;
    MPI_Comm_size(mpi_comm_, &num_ranks);
    for (int i = 0; i < num_ranks; ++i)
        if (i != root_) {
            std::ostringstream oss;
            oss << "rank[" << i << "]";
            auto msg = Data::byte_array(0);
            post_office_->deposit(oss.str(), std::make_unique<DataConstRef>(msg));
        }
}

} }

#endif

