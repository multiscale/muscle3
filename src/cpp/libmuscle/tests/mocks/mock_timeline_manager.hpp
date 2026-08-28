#pragma once

#include <libmuscle/namespace.hpp>
#include <libmuscle/port_manager.hpp>
#include <libmuscle/util.hpp>

#include <ymmsl/ymmsl.hpp>

#include <mocks/mock_support.hpp>

#include <string>


namespace libmuscle { namespace _MUSCLE_IMPL_NS {

class MockTimelineManager : public MockClass<MockTimelineManager> {
    public:
        MockTimelineManager(ReturnValue) {
            NAME_MOCK_MEM_FUN(MockTimelineManager, constructor);
            NAME_MOCK_MEM_FUN(MockTimelineManager, check_send_message);
            NAME_MOCK_MEM_FUN(MockTimelineManager, check_receive);
            NAME_MOCK_MEM_FUN(MockTimelineManager, record_received_message);
            NAME_MOCK_MEM_FUN(MockTimelineManager, reset);
            NAME_MOCK_MEM_FUN(MockTimelineManager, start_reuse_iteration);
            NAME_MOCK_MEM_FUN(MockTimelineManager, get_state);
            NAME_MOCK_MEM_FUN(MockTimelineManager, restore_state);
        }

        MockTimelineManager() {
            init_from_return_value();
        }

        explicit MockTimelineManager(PortManager const & port_manager) {
            init_from_return_value();
            constructor(&port_manager);
        }

        MockFun<Void, Obj<PortManager const *>> constructor;

        MockFun<
            Val<IterationCount>, Val<std::string const &>,
            Val<Optional<int>>> check_send_message;

        MockFun<Void, Val<std::string const &>, Val<Optional<int>>> check_receive;

        MockFun<
            Void, Val<std::string const &>, Val<Optional<int>>,
            Val<IterationCount const &>> record_received_message;

        MockFun<Void> reset;

        MockFun<Val<Optional<IterationCount>>> start_reuse_iteration;

        MockFun<Val<TimelineState>> get_state;

        MockFun<Void, Val<TimelineState const &>> restore_state;
};

using TimelineManager = MockTimelineManager;

} }
