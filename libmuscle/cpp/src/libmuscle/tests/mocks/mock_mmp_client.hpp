#pragma once

#include <string>
#include <tuple>
#include <unordered_map>
#include <vector>

#include <libmuscle/logging.hpp>
#include <libmuscle/profiling.hpp>
#include <libmuscle/snapshot.hpp>
#include <libmuscle/timestamp.hpp>
#include <libmuscle/util.hpp>

#include <ymmsl/ymmsl.hpp>


namespace libmuscle { namespace impl {

class MockMMPClient {
    public:
        explicit MockMMPClient(
                ymmsl::Reference const & instance_id, std::string const & location);

        void close();

        void submit_log_message(LogMessage const & message);

        void submit_profile_events(std::vector<ProfileEvent> const & event);

        void submit_snapshot_metadata(SnapshotMetadata const & snapshot_metadata);

        ymmsl::Settings get_settings();

        auto get_checkpoint_info() ->
            std::tuple<
                double,
                DataConstRef,
                Optional<std::string>,
                Optional<std::string>
            >;

        void register_instance(
                std::vector<std::string> const & locations,
                std::vector<::ymmsl::Port> const & ports);

        auto request_peers() ->
            std::tuple<
                std::vector<::ymmsl::Conduit>,
                std::unordered_map<::ymmsl::Reference, std::vector<int>>,
                std::unordered_map<::ymmsl::Reference, std::vector<std::string>>
            >;

        void deregister_instance();

        static void reset();

        static ::ymmsl::Reference last_instance_id;
        static int num_constructed;
        static std::string last_location;
        static std::vector<std::string> last_registered_locations;
        static std::vector<::ymmsl::Port> last_registered_ports;
        static LogMessage last_submitted_log_message;
        static std::vector<ProfileEvent> last_submitted_profile_events;
        static Optional<SnapshotMetadata> last_submitted_snapshot_metadata;
};

using MMPClient = MockMMPClient;

} }

