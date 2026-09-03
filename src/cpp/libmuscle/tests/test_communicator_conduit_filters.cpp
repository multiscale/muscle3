// Inject mocks
#define LIBMUSCLE_MOCK_LOGGER <mocks/mock_logger.hpp>
#define LIBMUSCLE_MOCK_MMP_CLIENT <mocks/mock_mmp_client.hpp>
#define LIBMUSCLE_MOCK_MPP_CLIENT <mocks/mock_mpp_client.hpp>
#define LIBMUSCLE_MOCK_MPP_SERVER <mocks/mock_mpp_server.hpp>
#define LIBMUSCLE_MOCK_PROFILER <mocks/mock_profiler.hpp>

// into the real implementation under test
#include <ymmsl/ymmsl.hpp>

#include <libmuscle/data.cpp>   // needs to be above milestone.cpp
#include <libmuscle/communicator.cpp>
#include <libmuscle/endpoint.cpp>
#include <libmuscle/mark.cpp>
#include <libmuscle/mcp/data_pack.cpp>
#include <libmuscle/mpp_message.cpp>
#include <libmuscle/mcp/tcp_util.cpp>
#include <libmuscle/mcp/transport_client.cpp>
#include <libmuscle/message.cpp>
#include <libmuscle/milestone.cpp>
#include <libmuscle/peer_info.cpp>
#include <libmuscle/port.cpp>
#include <libmuscle/profiling.cpp>
#include <libmuscle/receive_timeout_handler.cpp>
#include <libmuscle/timeline_manager.cpp>
#include <libmuscle/timestamp.cpp>
#include <libmuscle/util.cpp>

// Test code dependencies
#include <memory>
#include <stdexcept>
#include <gtest/gtest.h>
#include <libmuscle/communicator.hpp>
#include <libmuscle/namespace.hpp>
#include <mocks/mock_mmp_client.hpp>
#include <mocks/mock_mpp_client.hpp>
#include <mocks/mock_mpp_server.hpp>
#include <mocks/mock_logger.hpp>
#include <mocks/mock_profiler.hpp>


int main(int argc, char *argv[]) {
    ::testing::InitGoogleTest(&argc, argv);
    return RUN_ALL_TESTS();
}


using libmuscle::_MUSCLE_IMPL_NS::encode_iteration;
using libmuscle::_MUSCLE_IMPL_NS::Communicator;
using libmuscle::_MUSCLE_IMPL_NS::DataConstRef;
using libmuscle::_MUSCLE_IMPL_NS::IterationCount;
using libmuscle::_MUSCLE_IMPL_NS::Message;
using libmuscle::_MUSCLE_IMPL_NS::MPPMessage;
using libmuscle::_MUSCLE_IMPL_NS::MockLogger;
using libmuscle::_MUSCLE_IMPL_NS::MockProfiler;
using libmuscle::_MUSCLE_IMPL_NS::MockMMPClient;
using libmuscle::_MUSCLE_IMPL_NS::MockMPPClient;
using libmuscle::_MUSCLE_IMPL_NS::MockMPPServer;
using libmuscle::_MUSCLE_IMPL_NS::PeerInfo;
using libmuscle::_MUSCLE_IMPL_NS::PortClosed;
using libmuscle::_MUSCLE_IMPL_NS::PortManager;
using libmuscle::_MUSCLE_IMPL_NS::mcp::ProfileData;
using libmuscle::_MUSCLE_IMPL_NS::mcp::TimeoutHandler;

using ymmsl::Conduit;
using ymmsl::ConduitFilter;
using ymmsl::Operator;
using ymmsl::Port;
using ymmsl::Timeline;

struct libmuscle_repeater_communicator
    : ::testing::TestWithParam<std::string>
{
    RESET_MOCKS(MockLogger, MockMMPClient, MockMPPClient, MockMPPServer, MockProfiler);
    
    MockProfiler profiler_;
    MockMMPClient manager_;

    PortManager port_manager_;
    Communicator communicator_;

    libmuscle_repeater_communicator()
        : port_manager_({}, {})
        , communicator_("component", {}, port_manager_, profiler_, manager_)
    {
        manager_.get_timeline.return_value = Timeline(":parent3:parent2:parent1");
        std::string repeat_filter = GetParam();
        PeerInfo peer_info(
            "component",
            {},
            {
                Conduit("parent1.out", "component.unfiltered"),
                Conduit("parent2.out", "component.repeated", repeat_filter),
                Conduit("parent2.out", "component.twicerepeated", repeat_filter + " " + repeat_filter)
            },
            {{"parent1", {}}, {"parent2", {}}, {"parent3", {}}},
            {{"parent1", {}}, {"parent2", {}}, {"parent3", {}}},
            {
                Port("unfiltered", Operator::F_INIT),
                Port("repeated", Operator::F_INIT),
                Port("twicerepeated", Operator::F_INIT)
            }
        );
        port_manager_.connect_ports(peer_info);
        communicator_.set_peer_info(peer_info);
    }

    void TearDown() override {
        communicator_.shutdown();
    }
};

struct libmuscle_reducer_communicator
    : ::testing::Test
{
    RESET_MOCKS(MockLogger, MockMMPClient, MockMPPClient, MockMPPServer, MockProfiler);
    
    MockProfiler profiler_;
    MockMMPClient manager_;

    PortManager port_manager_;
    Communicator communicator_;

    libmuscle_reducer_communicator()
        : port_manager_({}, {})
        , communicator_("component", {}, port_manager_, profiler_, manager_)
    {
        manager_.get_timeline.return_value = Timeline(":parent");
        PeerInfo peer_info(
            "component",
            {},
            {
                Conduit("parent.out", "component.init"),
                Conduit("component.final", "parent.in"),
                Conduit("component.final", "sibling.in2"),
                // Reducer filter on O_I port
                Conduit("component.out", "sibling.in", "last"),
                // Reducer filter on O_F port
                Conduit("component.final", "aunt.init", "last"),
                // Double reducer filter on O_I port
                Conduit("component.out", "uncle.init", "last last"),
            },
            {{"parent", {}}, {"aunt", {}}, {"uncle", {}}, {"sibling", {}}},
            {{"parent", {}}, {"aunt", {}}, {"uncle", {}}, {"sibling", {}}},
            {
                Port("init", Operator::F_INIT),
                Port("out", Operator::O_I, Timeline("component")),
                Port("final", Operator::O_F)
            }
        );
        port_manager_.connect_ports(peer_info);
        communicator_.set_peer_info(peer_info);
    }

    void TearDown() override {
        communicator_.shutdown();
    }
};

class IterationOrMilestone {
    public:
        IterationCount iteration;
        bool is_milestone;
};

IterationOrMilestone M(IterationCount iteration) {
    return {iteration, true};
}

IterationOrMilestone I(IterationCount iteration) {
    return {iteration, false};
}



/** Helper method to mock MPPClient.receiev ,so it gives data with correct message
 * numbers and iteration counts.
 */
void mock_receive_messages(
    std::unordered_map<Reference, std::vector<IterationOrMilestone>> const & data)
{
    std::unordered_map<Reference, int> idx_per_port;
    std::unordered_map<Reference, int> num_per_port;

    for (auto & item : data) {
        idx_per_port.emplace(item.first, 0);
        num_per_port.emplace(item.first, 0);
    }

    // Capture a copy of the data, the local variables go out-of-scope at the end of
    // this method:
    MockMPPClient::return_value.receive.side_effect = [data, idx_per_port, num_per_port](
            Reference ref, TimeoutHandler *handler
        ) mutable -> std::tuple<std::vector<char>, ProfileData>
    {
        int & idx = idx_per_port.at(ref);
        int & num = num_per_port.at(ref);
        auto iteration_or_milestone = data.at(ref).at(idx);
        auto & iteration = iteration_or_milestone.iteration;

        DataConstRef dcr = iteration_or_milestone.is_milestone ? 
            DataConstRef(Milestone(iteration)) : DataConstRef(encode_iteration(iteration));

        MPPMessage msg("snd", "recv", {}, 0.0, {}, Settings(), num, dcr, iteration);
        auto encoded = msg.encoded();

        ++idx;
        if (!iteration_or_milestone.is_milestone) ++num;
        return {encoded, ProfileData()};
    };
}


TEST_P(libmuscle_repeater_communicator, repeater_filters) {
    mock_receive_messages({
        {"component.twicerepeated", {
            I({0}), M({})
        }},
        {"component.repeated", {
            I({0, 0}), I({0, 1}), I({0, 2}), M({0}), M({})
        }},
        {"component.unfiltered", {
            I({0, 0, 0}),
            I({0, 0, 1}),
            M({0, 0}),
            // parent is allowed to send 0 messages on its O_I port in an iteration
            M({0, 1}),
            I({0, 2, 0}),
            M({0, 2}),
            M({0}),
            M({})
        }}
    });

    bool is_padded = GetParam() == "pad";

    auto cache = communicator_.pre_receive();
    ASSERT_EQ(decode_iteration(cache.at("unfiltered").data()).get(), IterationCount({0, 0, 0}));
    ASSERT_EQ(decode_iteration(cache.at("repeated").data()).get(), IterationCount({0, 0}));
    ASSERT_EQ(decode_iteration(cache.at("twicerepeated").data()).get(), IterationCount({0}));

    cache = communicator_.pre_receive();
    ASSERT_EQ(decode_iteration(cache.at("unfiltered").data()).get(), IterationCount({0, 0, 1}));
    if (is_padded) {
        ASSERT_TRUE(cache.at("repeated").data().is_nil());
        ASSERT_TRUE(cache.at("twicerepeated").data().is_nil());
    } else {
        ASSERT_EQ(decode_iteration(cache.at("repeated").data()).get(), IterationCount({0, 0}));
        ASSERT_EQ(decode_iteration(cache.at("twicerepeated").data()).get(), IterationCount({0}));
    }

    cache = communicator_.pre_receive();
    ASSERT_EQ(decode_iteration(cache.at("unfiltered").data()).get(), IterationCount({0, 2, 0}));
    ASSERT_EQ(decode_iteration(cache.at("repeated").data()).get(), IterationCount({0, 2}));
    if (is_padded) {
        ASSERT_TRUE(cache.at("twicerepeated").data().is_nil());
    } else {
        ASSERT_EQ(decode_iteration(cache.at("twicerepeated").data()).get(), IterationCount({0}));
    }

    ASSERT_THROW(communicator_.pre_receive(), PortClosed);
}

TEST_P(libmuscle_repeater_communicator, repeater_filters_discard_messages) {
    mock_receive_messages({
        {"component.twicerepeated", {
            I({0}), I({1}), I({2}), M({})
        }},
        {"component.repeated", {
            // Grandparent doesn't send on O_I in its first iteration
            M({0}),
            I({1, 0}),
            I({1, 1}),
            I({1, 2}),
            M({1}),
            I({2, 0}),
            I({2, 1}),
            M({2}),
            M({})
        }},
        {"component.unfiltered", {
            M({0}),
            // parent doesn't send messages on O_I in the first couple of iterations
            // component will need to discard the corresponding messages from the grandparent
            M({1, 0}),
            M({1, 1}),
            M({1, 2}),
            M({1}),
            I({2, 0, 0}),
            M({2, 0}),
            I({2, 1, 0}),
            I({2, 1, 1}),
            M({2, 1}),
            M({2}),
            M({})
        }}
    });

    bool is_padded = GetParam() == "pad";

    auto cache = communicator_.pre_receive();
    ASSERT_EQ(decode_iteration(cache.at("unfiltered").data()).get(), IterationCount({2, 0, 0}));
    ASSERT_EQ(decode_iteration(cache.at("repeated").data()).get(), IterationCount({2, 0}));
    ASSERT_EQ(decode_iteration(cache.at("twicerepeated").data()).get(), IterationCount({2}));

    cache = communicator_.pre_receive();
    ASSERT_EQ(decode_iteration(cache.at("unfiltered").data()).get(), IterationCount({2, 1, 0}));
    ASSERT_EQ(decode_iteration(cache.at("repeated").data()).get(), IterationCount({2, 1}));
    if (is_padded) {
        ASSERT_TRUE(cache.at("twicerepeated").data().is_nil());
    } else {
        ASSERT_EQ(decode_iteration(cache.at("twicerepeated").data()).get(), IterationCount({2}));
    }

    cache = communicator_.pre_receive();
    ASSERT_EQ(decode_iteration(cache.at("unfiltered").data()).get(), IterationCount({2, 1, 1}));
    if (is_padded) {
        ASSERT_TRUE(cache.at("repeated").data().is_nil());
        ASSERT_TRUE(cache.at("twicerepeated").data().is_nil());
    } else {
        ASSERT_EQ(decode_iteration(cache.at("repeated").data()).get(), IterationCount({2, 1}));
        ASSERT_EQ(decode_iteration(cache.at("twicerepeated").data()).get(), IterationCount({2}));
    }

    ASSERT_THROW(communicator_.pre_receive(), PortClosed);
}


INSTANTIATE_TEST_SUITE_P(
    repeated, libmuscle_repeater_communicator, ::testing::Values("repeat", "pad"));


TEST_F(libmuscle_reducer_communicator, reducer_filters) {
    mock_receive_messages({{"component.init", {I({0}), I({1}), M({})}}});

    auto & deposit = communicator_.server_.deposit;

    auto cache = communicator_.pre_receive();
    ASSERT_EQ(decode_iteration(cache.at("init").data()).get(), IterationCount({0}));
    // Send some messages on O_I
    for (std::size_t i = 0; i < 5; ++i) {
        communicator_.send_message("out", Message(i, Data(i), Settings()));
        ASSERT_FALSE(deposit.called());
    }
    // Send on O_F
    communicator_.send_message("final", Message(5, Data("data"), Settings()));
    ASSERT_EQ(deposit.call_args_list.size(), 2);
    ASSERT_EQ(std::get<0>(deposit.call_args_list[0]), "parent.in");
    ASSERT_EQ(std::get<0>(deposit.call_args_list[1]), "sibling.in2");
    deposit.call_args_list.clear();

    // Pre-receive will send cached LAST message to sibling.in
    cache = communicator_.pre_receive();
    ASSERT_EQ(decode_iteration(cache.at("init").data()).get(), IterationCount({1}));
    // N.B. we don't send the [1] milestone to sibling.in due to the LAST filter, only
    // the cached message
    ASSERT_EQ(deposit.call_args_list.size(), 1);
    ASSERT_EQ(std::get<0>(deposit.call_args_list[0]), "sibling.in");
    auto sent_message = std::get<1>(deposit.call_args_list[0]);
    ASSERT_EQ(sent_message->timestamp, 4.0);
    deposit.call_args_list.clear();

    // Skip O_I and send on O_F
    communicator_.send_message("final", Message(10, Data("data"), Settings()));
    ASSERT_EQ(deposit.call_args_list.size(), 2);
    ASSERT_EQ(std::get<0>(deposit.call_args_list[0]), "parent.in");
    ASSERT_EQ(std::get<0>(deposit.call_args_list[1]), "sibling.in2");
    deposit.call_args_list.clear();

    // Pre-receive will first send cached LAST message to sibling.in, then receive
    // Milestone([]) and trigger:
    // - Cached LAST message on "final" to aunt.init
    // - Cached LAST LAST message on "out" to uncle.init
    // - Milestone([]) to sibling.in, sibling.in2, parent.in
    ASSERT_THROW(communicator_.pre_receive(), PortClosed);
    ASSERT_EQ(deposit.call_args_list.size(), 6.0);

    std::unordered_map<std::string, std::vector<std::shared_ptr<MPPMessage>>> messages_per_peer_port;
    for (auto & call : deposit.call_args_list) {
        std::string peer_port(std::get<0>(call));
        std::shared_ptr<MPPMessage> message(std::get<1>(call));
        auto it = messages_per_peer_port.find(peer_port);
        if (it == messages_per_peer_port.end()) {
            // Not found
            messages_per_peer_port.emplace(
                    peer_port, std::vector<std::shared_ptr<MPPMessage>>({message}));
        } else {
            it->second.emplace_back(message);
        }
    }

    // O_I -> last -> sibling.in
    auto & messages = messages_per_peer_port.at("sibling.in");
    ASSERT_EQ(messages.size(), 2);
    // No message was sent on O_I this reuse loop, so LAST generates an empty message
    ASSERT_EQ(messages[0]->timestamp, -std::numeric_limits<double>::infinity());
    ASSERT_TRUE(messages[0]->data.is_nil());
    ASSERT_TRUE(is_milestone(messages[1]->data));
    ASSERT_TRUE(Milestone(messages[1]->data).is_final_milestone());

    // Just milestones
    for (auto & peer_port : {"sibling.in2", "parent.in"}) {
        messages = messages_per_peer_port.at(peer_port);
        ASSERT_EQ(messages.size(), 1);
        ASSERT_TRUE(is_milestone(messages[0]->data));
        ASSERT_TRUE(Milestone(messages[0]->data).is_final_milestone());
    }

    // O_I -> last last -> uncle.init
    ASSERT_EQ(messages_per_peer_port.at("uncle.init").size(), 1);
    ASSERT_EQ(messages_per_peer_port.at("uncle.init")[0]->timestamp, 4.0);

    // O_F -> last -> aunt.init
    ASSERT_EQ(messages_per_peer_port.at("aunt.init").size(), 1);
    ASSERT_EQ(messages_per_peer_port.at("aunt.init")[0]->timestamp, 10.0);
}
