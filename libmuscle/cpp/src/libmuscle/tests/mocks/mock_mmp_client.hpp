#pragma once

#include <string>
#include <tuple>
#include <unordered_map>
#include <vector>

#include <libmuscle/logging.hpp>
#include <libmuscle/namespace.hpp>
#include <libmuscle/profiling.hpp>
#include <libmuscle/snapshot.hpp>
#include <libmuscle/timestamp.hpp>
#include <libmuscle/util.hpp>

#include <ymmsl/ymmsl.hpp>

#include <libmuscle/tests/mocks/mock_support.hpp>


namespace libmuscle { namespace _MUSCLE_IMPL_NS {

class MockMMPClient : public MockClass<MockMMPClient> {
    public:
        MockMMPClient(ReturnValue) {
            NAME_MOCK_MEM_FUN(MockMMPClient, constructor);
            NAME_MOCK_MEM_FUN(MockMMPClient, close);
            NAME_MOCK_MEM_FUN(MockMMPClient, submit_log_message);
            NAME_MOCK_MEM_FUN(MockMMPClient, submit_profile_events);
            NAME_MOCK_MEM_FUN(MockMMPClient, submit_snapshot_metadata);
            NAME_MOCK_MEM_FUN(MockMMPClient, get_settings);
            NAME_MOCK_MEM_FUN(MockMMPClient, get_checkpoint_info);
            NAME_MOCK_MEM_FUN(MockMMPClient, register_instance);
            NAME_MOCK_MEM_FUN(MockMMPClient, request_peers);
            NAME_MOCK_MEM_FUN(MockMMPClient, deregister_instance);

            // Create some empty return objects for return values with a complex
            // structure, to make it easier to set them in the tests or fixtures.
            std::vector<::ymmsl::Conduit> conduits;
            std::unordered_map<::ymmsl::Reference, std::vector<int>> peer_dimensions;
            std::unordered_map<::ymmsl::Reference, std::vector<std::string>> peer_locations;
            request_peers.return_value = std::make_tuple(
                    std::move(conduits),
                    std::move(peer_dimensions),
                    std::move(peer_locations));

            get_settings.return_value = ymmsl::Settings();

            get_checkpoint_info.return_value = std::make_tuple(
                    0.1,
                    // no checkpoints defined:
                    Data::dict(
                            "at_end", false,
                            "wallclock_time", Data::list(),
                            "simulation_time", Data::list()),
                    Optional<std::string>(),
                    Optional<std::string>());
        }

        MockMMPClient() {
            init_from_return_value();
        }

        MockMMPClient(
                ymmsl::Reference const & instance_id, std::string const & location)
        {
            init_from_return_value();
            constructor(instance_id, location);
        }

        MockFun<
            Void, Val<ymmsl::Reference const &>, Val<std::string const &>> constructor;
        MockFun<Void> close;
        MockFun<Void, Val<LogMessage const &>> submit_log_message;
        MockFun<Void, Val<std::vector<ProfileEvent> const &>> submit_profile_events;
        MockFun<Void, Val<SnapshotMetadata const &>> submit_snapshot_metadata;
        MockFun<Val<ymmsl::Settings>> get_settings;

        // We use Data here instead of DataConstRef because DCR isn't assignable,
        // not even move-assignable, and so we wouldn't be able to set the return
        // value, and MockFun isn't smart enough to recursively traverse the tuple
        // and replace the type automatically.
        MockFun<Val<std::tuple<
            double, Data, Optional<std::string>, Optional<std::string>
            >>> get_checkpoint_info;

        MockFun<
            Void, Val<std::vector<std::string> const &>,
            Val<std::vector<::ymmsl::Port> const &>
            > register_instance;

        MockFun<Val<std::tuple<
            std::vector<::ymmsl::Conduit>,
            std::unordered_map<::ymmsl::Reference, std::vector<int>>,
            std::unordered_map<::ymmsl::Reference, std::vector<std::string>>
            >>> request_peers;

        MockFun<Void> deregister_instance;
};

using MMPClient = MockMMPClient;

} }

