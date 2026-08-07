#pragma once

#include <libmuscle/namespace.hpp>
#include <libmuscle/peer_info.hpp>
#include <libmuscle/port.hpp>
#include <libmuscle/util.hpp>

#include <ymmsl/ymmsl.hpp>

#include <mocks/mock_support.hpp>

#include <string>
#include <unordered_map>
#include <vector>


namespace libmuscle { namespace _MUSCLE_IMPL_NS {

using PortsDescription = std::unordered_map<ymmsl::Operator, std::vector<std::string>>;


class MockPortManager : public MockClass<MockPortManager> {
    public:
        using PortMessageCounts = std::unordered_map<std::string, std::vector<int>>;

        MockPortManager(ReturnValue) {
            NAME_MOCK_MEM_FUN(MockPortManager, constructor);
            NAME_MOCK_MEM_FUN(MockPortManager, connect_ports);
            NAME_MOCK_MEM_FUN(MockPortManager, settings_in_connected);
            NAME_MOCK_MEM_FUN(MockPortManager, has_f_init_connections);
            NAME_MOCK_MEM_FUN(MockPortManager, get_connected_ports);
            NAME_MOCK_MEM_FUN(MockPortManager, list_subtimelines);
            NAME_MOCK_MEM_FUN(MockPortManager, muscle_settings_in);
            NAME_MOCK_MEM_FUN(MockPortManager, list_ports);
            NAME_MOCK_MEM_FUN(MockPortManager, port_exists);
            NAME_MOCK_MEM_FUN(MockPortManager, get_port);
            NAME_MOCK_MEM_FUN(MockPortManager, get_message_counts);
            NAME_MOCK_MEM_FUN(MockPortManager, restore_message_counts);

            // Sensible defaults so that a freshly-constructed, unconfigured
            // mock can still be used to build a (real) TimelineManager,
            // which queries these at construction time.
            settings_in_connected.return_value = false;
            has_f_init_connections.return_value = false;
            get_connected_ports.return_value = std::vector<Port>();
            list_subtimelines.return_value = std::vector<::ymmsl::Timeline>();
        }

        MockPortManager() {
            init_from_return_value();
        }

        MockPortManager(
                std::vector<int> const & index,
                Optional<PortsDescription> const & declared_ports) {
            init_from_return_value();
            constructor(index, declared_ports);
        }

        MockFun<
            Void, Val<std::vector<int> const &>,
            Val<Optional<PortsDescription> const &>> constructor;

        MockFun<Void, Val<PeerInfo const &>> connect_ports;

        MockFun<Val<bool>> settings_in_connected;

        MockFun<Val<bool>> has_f_init_connections;

        MockFun<
            Val<std::vector<Port>>, Val<::ymmsl::Operator>,
            Val<Optional<::ymmsl::Timeline> const &>> get_connected_ports;

        MockFun<Val<std::vector<::ymmsl::Timeline>>> list_subtimelines;

        MockFun<Obj<Port &>> muscle_settings_in;

        MockFun<Val<PortsDescription>> list_ports;

        MockFun<Val<bool>, Val<std::string const &>> port_exists;

        MockFun<Obj<Port &>, Val<std::string const &>> get_port;

        MockFun<Val<PortMessageCounts>> get_message_counts;

        MockFun<Void, Val<PortMessageCounts const &>> restore_message_counts;
};

using PortManager = MockPortManager;

} }

