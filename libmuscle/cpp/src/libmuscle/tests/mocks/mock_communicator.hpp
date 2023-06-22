#pragma once

#include <libmuscle/data.hpp>
#include <libmuscle/logger.hpp>
#include <libmuscle/message.hpp>
#include <libmuscle/namespace.hpp>
#include <libmuscle/peer_manager.hpp>
#include <libmuscle/port.hpp>
#include <libmuscle/profiler.hpp>
#include <libmuscle/util.hpp>

#include <ymmsl/ymmsl.hpp>

#include <memory>
#include <string>
#include <unordered_map>
#include <vector>


namespace libmuscle { namespace _MUSCLE_IMPL_NS {

using PortsDescription = std::unordered_map<ymmsl::Operator, std::vector<std::string>>;


class MockCommunicator {
    public:
        using PortMessageCounts = std::unordered_map<std::string, std::vector<int>>;

        MockCommunicator(
                ymmsl::Reference const & kernel,
                std::vector<int> const & index,
                Optional<PortsDescription> const & declared_ports,
                Logger & logger, Profiler & profiler);

        std::vector<std::string> get_locations() const;

        void connect(
                std::vector<ymmsl::Conduit> const & conduits,
                PeerDims const & peer_dims,
                PeerLocations const & peer_locations);

        bool settings_in_connected() const;

        PortsDescription list_ports() const;

        bool port_exists(std::string const & port_name) const;

        Port const & get_port(std::string const & port_name) const;

        Port & get_port(std::string const & port_name);

        void send_message(
                std::string const & port_name,
                Message const & message,
                Optional<int> slot = {});

        Message receive_message(
                std::string const & port_name,
                Optional<int> slot = {},
                Optional<Message> const & default_msg = {}
                );

        void close_port(std::string const & port_name, Optional<int> slot = {});

        void shutdown();

        PortMessageCounts get_message_counts();

        void restore_message_counts(PortMessageCounts const & port_message_counts);

        static void reset();
        static int num_constructed;
        static bool settings_in_connected_return_value;
        static bool port_exists_return_value;
        static std::unordered_map<std::string, Port> get_port_return_value;
        static std::unordered_map<Reference, std::unique_ptr<Message>>
            next_received_message;
        static PortsDescription list_ports_return_value;
        static std::string last_sent_port;
        static Message last_sent_message;
        static Optional<int> last_sent_slot;
        static PortMessageCounts get_message_counts_return_value;
        static PortMessageCounts last_restored_message_counts;

    private:
        friend class TestCommunicator;
};

using Communicator = MockCommunicator;

} }

