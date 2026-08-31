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
            NAME_MOCK_MEM_FUN(MockTimelineManager, check_pre_received_iteration_counts);
            NAME_MOCK_MEM_FUN(MockTimelineManager, check_receive_s);
            NAME_MOCK_MEM_FUN(MockTimelineManager, record_received_s_message_mock);
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

        MockFun<
            Val<IterationCount>,
            Val<std::vector<IterationCount>>> check_pre_received_iteration_counts;

        MockFun<Void, Val<std::string const &>, Val<Optional<int>>> check_receive_s;

        MockFun<
            Val<IterationCount const &>, Val<std::string const &>, Val<Optional<int>>,
            Val<IterationCount const &>, Val<std::size_t>> record_received_s_message_mock;
        
        IterationCount const & record_received_s_message(
                std::string const & port_name, Optional<int> slot,
                IterationCount const & iteration, std::size_t num_repeat_filters = 0)
        {
            return record_received_s_message_mock(port_name, slot, iteration, num_repeat_filters);
        }

        MockFun<Void> reset;

        MockFun<Val<Optional<IterationCount>>> start_reuse_iteration;

        MockFun<Val<TimelineState>> get_state;

        MockFun<Void, Val<TimelineState const &>> restore_state;
};

using TimelineManager = MockTimelineManager;

} }
