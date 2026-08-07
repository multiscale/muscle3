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

class MockTriggerManager : public MockClass<MockTriggerManager> {
    public:
        MockTriggerManager(ReturnValue) {
            NAME_MOCK_MEM_FUN(MockTriggerManager, constructor);
            NAME_MOCK_MEM_FUN(MockTriggerManager, set_checkpoint_info);
            NAME_MOCK_MEM_FUN(MockTriggerManager, elapsed_walltime);
            NAME_MOCK_MEM_FUN(MockTriggerManager, checkpoints_considered_until);
            NAME_MOCK_MEM_FUN(MockTriggerManager, has_checkpoints);
            NAME_MOCK_MEM_FUN(MockTriggerManager, harmonise_wall_time);
            NAME_MOCK_MEM_FUN(MockTriggerManager, should_save_snapshot);
            NAME_MOCK_MEM_FUN(MockTriggerManager, should_save_final_snapshot);
            NAME_MOCK_MEM_FUN(MockTriggerManager, update_checkpoints);
            NAME_MOCK_MEM_FUN(MockTriggerManager, get_triggers);
        }

        MockTriggerManager() {
            init_from_return_value();
            constructor();
        }

        MockFun<Void> constructor;

        MockFun<Void, Val<double>, Val<Data const &>> set_checkpoint_info;

        MockFun<Val<double>> elapsed_walltime;

        MockFun<Val<double>> checkpoints_considered_until;

        MockFun<Val<bool>> has_checkpoints;

        MockFun<Void, Val<double>> harmonise_wall_time;

        MockFun<Val<bool>, Val<double>> should_save_snapshot;

        MockFun<Val<bool>, Val<bool>, Val<Optional<double>>> should_save_final_snapshot;

        MockFun<Void, Val<double>> update_checkpoints;

        MockFun<Val<std::vector<std::string>>> get_triggers;
};

using TriggerManager = MockTriggerManager;

} }

