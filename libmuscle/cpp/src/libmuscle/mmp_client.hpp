#pragma once

#ifdef LIBMUSCLE_MOCK_MMP_CLIENT
#include LIBMUSCLE_MOCK_MMP_CLIENT
#else


#include <memory>
#include <mutex>
#include <stdexcept>
#include <string>
#include <thread>
#include <tuple>
#include <unordered_map>
#include <vector>

#include <libmuscle/data.hpp>
#include <libmuscle/logging.hpp>
#include <libmuscle/mcp/tcp_transport_client.hpp>
#include <libmuscle/namespace.hpp>
#include <libmuscle/peer_info.hpp>
#include <libmuscle/profiling.hpp>
#include <libmuscle/snapshot.hpp>
#include <libmuscle/util.hpp>
#include <ymmsl/ymmsl.hpp>


namespace libmuscle { namespace _MUSCLE_IMPL_NS {

/** Represent a failure due to lock timeout.
 */
class ConnectionLockedError : public std::runtime_error {
    using std::runtime_error::runtime_error; };

/** The client for the MUSCLE Manager Protocol.
 *
 * This class connects to the Manager and communicates with it on behalf of the
 * rest of libmuscle.
 *
 * It manages the connection, and encodes and decodes MsgPack. Communication is
 * protected by an internal mutex, so this class can be called simultaneously
 * from different threads.
 */
class MMPClient {
    public:
        /** Create an MMPClient.
         *
         * @param location A connection string of the form hostname:port.
         */
        explicit MMPClient(
                ymmsl::Reference const & instance_id,
                std::string const & location);

        /** Close the connection
         *
         * This closes the connection. After this no other member functions
         * can be called.
         */
        void close();

        /** Send a log message to the manager.
         *
         * @param message The message to send.
         */
        void submit_log_message(LogMessage const & message);

        /** Sends profiling events to the manager.
         *
         * @param events The events to send.
         */
        void submit_profile_events(std::vector<ProfileEvent> const & events);

        /** Send snapshot metadata to the manager.
         *
         * @param snapshot_metadata Snapshot metadata to supply to the manager.
         */
        void submit_snapshot_metadata(SnapshotMetadata const & snapshot_metadata);

        /** Get the global settings from the manager.
         *
         * @return A Settings object with the global settings.
         */
        ymmsl::Settings get_settings();

        /** Get the checkpoint info from the manager.
         *
         * @return A tuple containing:
         *      elapsed_time: current elapsed wallclock time
         *      checkpoints: encoded checkpoint configuration
         *      resume: optional path to the resume snapshot
         *      snapshot_directory: optional path to store snapshots
         */
        auto get_checkpoint_info() ->
            std::tuple<
                double,
                DataConstRef,
                Optional<std::string>,
                Optional<std::string>
            >;

        /** Register a component instance with the manager.
         *
         * @param locations List of places where the instance can be reached.
         * @param ports List of ports of this instance.
         */
        void register_instance(
                std::vector<std::string> const & locations,
                std::vector<::ymmsl::Port> const & ports);

        /** Request connection information about peers.
         *
         * This will repeat the request at an exponentially increasing query
         * interval at first, until it reaches the interval specified by
         * peer_interval_min and peer_interval_max. From there on, intervals
         * are drawn randomly from that range.
         *
         * @return PeerInfo received from the manager
         */
        auto request_peers() -> PeerInfo;

        void deregister_instance();

        /** Notify the manager that we're waiting to receive a message. */
        void waiting_for_receive(
                ::ymmsl::Reference const & peer_instance_id, std::string const & port_name,
                Optional<int> slot);

        /** Notify the manager that we're done waiting to receive a message. */
        void waiting_for_receive_done(
                ::ymmsl::Reference const & peer_instance_id, std::string const & port_name,
                Optional<int> slot);

        /** Ask the manager if we're part of a deadlock. */
        bool is_deadlocked();

    private:
        ymmsl::Reference instance_id_;
        mcp::TcpTransportClient transport_client_;
        mutable std::recursive_timed_mutex mutex_;
        std::thread::id cur_owner_;

        /* Helper function that encodes/decodes and calls the manager.
         */
        DataConstRef call_manager_(DataConstRef const & request, bool timid = false);
};

} }

#endif

