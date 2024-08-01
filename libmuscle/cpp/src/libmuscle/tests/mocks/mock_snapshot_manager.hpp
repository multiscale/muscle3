#pragma once

#include <libmuscle/logger.hpp>
#include <libmuscle/mmp_client.hpp>
#include <libmuscle/namespace.hpp>
#include <libmuscle/port_manager.hpp>
#include <libmuscle/snapshot.hpp>
#include <libmuscle/util.hpp>

#include <ymmsl/ymmsl.hpp>

#include <mocks/mock_support.hpp>


namespace libmuscle { namespace _MUSCLE_IMPL_NS {

class MockSnapshotManager : public MockClass<MockSnapshotManager> {
    public:
        MockSnapshotManager(ReturnValue) {
            NAME_MOCK_MEM_FUN(MockSnapshotManager, constructor);
            NAME_MOCK_MEM_FUN(MockSnapshotManager, prepare_resume);
            NAME_MOCK_MEM_FUN(MockSnapshotManager, resume_overlay);
            NAME_MOCK_MEM_FUN(MockSnapshotManager, resuming_from_intermediate);
            NAME_MOCK_MEM_FUN(MockSnapshotManager, resuming_from_final);
            NAME_MOCK_MEM_FUN(MockSnapshotManager, load_snapshot);
            NAME_MOCK_MEM_FUN(MockSnapshotManager, save_snapshot);
            NAME_MOCK_MEM_FUN(MockSnapshotManager, load_snapshot_from_file);
        }

        MockSnapshotManager(
                ymmsl::Reference const & instance_id,
                MMPClient & manager,
                PortManager & port_manager,
                Logger & logger)
        {
            init_from_return_value();
            constructor(instance_id, manager, port_manager, logger);
        }

        MockFun<
            Void, Val<ymmsl::Reference const &>, Obj<MMPClient &>,
            Obj<PortManager &>, Obj<Logger &>> constructor;

        MockFun<
            Val<Optional<double>>, Val<Optional<std::string> const &>,
            Val<Optional<std::string> const &>> prepare_resume;

        MockFun<Val<::ymmsl::Settings>> resume_overlay;

        MockFun<Val<bool>> resuming_from_intermediate;

        MockFun<Val<bool>> resuming_from_final;

        MockFun<Val<Message>> load_snapshot;

        MockFun<
            Val<double>, Val<Optional<Message>>, Val<bool>,
            Val<std::vector<std::string> const &>, Val<double>, Val<Optional<double>>,
            Val<::ymmsl::Settings>> save_snapshot;

        MockFun<Val<Snapshot>, Val<std::string const &>> load_snapshot_from_file;
};

using SnapshotManager = MockSnapshotManager;

} }

