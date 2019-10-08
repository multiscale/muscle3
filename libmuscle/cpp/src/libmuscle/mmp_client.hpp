#pragma once

#ifdef LIBMUSCLE_MOCK_MMP_CLIENT
#include LIBMUSCLE_MOCK_MMP_CLIENT
#else


#include <memory>
#include <string>
#include <tuple>
#include <unordered_map>
#include <vector>

#include <libmuscle/logging.hpp>
#include <muscle_manager_protocol/muscle_manager_protocol.grpc.pb.h>
#include <ymmsl/ymmsl.hpp>


namespace libmuscle {

/** The client for the MUSCLE Manager Protocol.
 *
 * This class connects to the Manager and communicates with it on behalf of the
 * rest of libmuscle.
 *
 * It manages the connection, and converts between our native types and the
 * gRPC generated types.
 */
class MMPClient {
    public:
        /** Create an MMPClient.
         *
         * @param location A connection string of the form hostname:port.
         */
        MMPClient(std::string const & location);

        /** Send a log message to the manager.
         *
         * @param message The message to send.
         */
        void submit_log_message(LogMessage const & message);

        /** Get the global settings from the manager.
         *
         * @return A Settings object with the global settings.
         */
        ymmsl::Settings get_settings();

        /** Register a compute element instance with the manager.
         *
         * @param name Name of the instance in the simulation.
         * @param locations List of places where the instance can be reached.
         * @param ports List of ports of this instance.
         */
        void register_instance(
                ::ymmsl::Reference const & name,
                std::vector<std::string> const & locations,
                std::vector<::ymmsl::Port> const & ports);

        /** Request connection information about peers.
         *
         * This will repeat the request at an exponentially increasing query
         * interval at first, until it reaches the interval specified by
         * peer_interval_min and peer_interval_max. From there on, intervals
         * are drawn randomly from that range.
         *
         * @param name Name of the current instance.
         * @return A tuple containng a list of conduits that this instance is
         *      attached to, a dictionary of peer dimensions, which is indexed
         *      by Reference to the peer kernel and specifies how many
         *      instances of the kernel there are, and a dictionary of peer
         *      instance locations, indexed by Reference to a peer instance and
         *      containing for each peer instance a list of network location
         *      strings at which it can be reached.
         */
        auto request_peers(::ymmsl::Reference const & name) ->
            std::tuple<
                std::vector<::ymmsl::Conduit>,
                std::unordered_map<::ymmsl::Reference, std::vector<int>>,
                std::unordered_map<::ymmsl::Reference, std::vector<std::string>>
            >;

        void deregister_instance(::ymmsl::Reference const & name);

    private:
        std::unique_ptr<muscle_manager_protocol::MuscleManager::Stub> client_;
};

}

#endif

