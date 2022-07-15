#pragma once

#ifdef LIBMUSCLE_MOCK_MPP_CLIENT
#include LIBMUSCLE_MOCK_MPP_CLIENT
#else

#include "libmuscle/data.hpp"
#include "libmuscle/mcp/transport_client.hpp"

#include <ymmsl/ymmsl.hpp>

#include <memory>
#include <string>
#include <vector>


namespace libmuscle { namespace impl {

/** A client that connects to an MPP server.
 *
 * This client connects to a peer to retrieve messages. It uses an MCP
 * Transport to connect.
 */
class MPPClient {
    public:
        /** Create an MPP Client for the given peer.
         *
         * The client will connect to the peer on one of its locations. It tries
         * the most efficient protocol first. Once connected, it can request
         * messages from any component and port represented by it.
         *
         * @param locations The peer's location strings
         */
        MPPClient(std::vector<std::string> const & locations);

        /** MPPClients are not copyable.
         */
        MPPClient(MPPClient const & rhs) = delete;

        /** MPPClients are not copy-assignable.
         */
        MPPClient & operator=(MPPClient const & rhs) = delete;

        /** MPPClients are not moveable.
         */
        MPPClient(MPPClient && rhs) = delete;

        /** MPPClients are not move-assignable
         */
        MPPClient & operator=(MPPClient && rhs) = delete;

        /** Receive a message from a port this client connects to.
         *
         * This returns a DataConstRef holding a byte array with the received
         * data.
         *
         * @param The receiving (local) port.
         *
         * @return The received message.
         */
        DataConstRef receive(::ymmsl::Reference const & receiver);

        /** Closes this client.
         *
         * This closes any connections this client has and/or performs other
         * shutdown activities.
         */
        void close();

    private:
        std::unique_ptr<mcp::TransportClient> transport_client_;

        template <class ClientType> void try_connect_(
                std::vector<std::string> const & locations);
};

} }

#endif

