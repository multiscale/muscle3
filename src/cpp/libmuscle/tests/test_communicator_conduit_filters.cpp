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
            I({}), M({})
        }},
        {"component.repeated", {
            I({0}), I({1}), I({2}), M({})
        }},
        {"component.unfiltered", {
            I({0, 0}),
            I({0, 1}),
            M({0}),
            // parent is allowed to send 0 messages on its O_I port in an iteration
            M({1}),
            I({2, 0}),
            M({2}),
            M({})
        }}
    });

    bool is_padded = GetParam() == "pad";

    auto cache = communicator_.pre_receive_f_init();
    ASSERT_EQ(decode_iteration(cache.at("unfiltered").data()).get(), IterationCount({0, 0}));
    ASSERT_EQ(decode_iteration(cache.at("repeated").data()).get(), IterationCount({0}));
    ASSERT_EQ(decode_iteration(cache.at("twicerepeated").data()).get(), IterationCount({}));
    communicator_.finish_reuse_iteration();

    cache = communicator_.pre_receive_f_init();
    ASSERT_EQ(decode_iteration(cache.at("unfiltered").data()).get(), IterationCount({0, 1}));
    if (is_padded) {
        ASSERT_TRUE(cache.at("repeated").data().is_nil());
        ASSERT_TRUE(cache.at("twicerepeated").data().is_nil());
    } else {
        ASSERT_EQ(decode_iteration(cache.at("repeated").data()).get(), IterationCount({0}));
        ASSERT_EQ(decode_iteration(cache.at("twicerepeated").data()).get(), IterationCount({}));
    }
    communicator_.finish_reuse_iteration();

    cache = communicator_.pre_receive_f_init();
    ASSERT_EQ(decode_iteration(cache.at("unfiltered").data()).get(), IterationCount({2, 0}));
    ASSERT_EQ(decode_iteration(cache.at("repeated").data()).get(), IterationCount({2}));
    if (is_padded) {
        ASSERT_TRUE(cache.at("twicerepeated").data().is_nil());
    } else {
        ASSERT_EQ(decode_iteration(cache.at("twicerepeated").data()).get(), IterationCount({}));
    }
    communicator_.finish_reuse_iteration();

    ASSERT_THROW(communicator_.pre_receive_f_init(), PortClosed);
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

    auto cache = communicator_.pre_receive_f_init();
    ASSERT_EQ(decode_iteration(cache.at("unfiltered").data()).get(), IterationCount({2, 0, 0}));
    ASSERT_EQ(decode_iteration(cache.at("repeated").data()).get(), IterationCount({2, 0}));
    ASSERT_EQ(decode_iteration(cache.at("twicerepeated").data()).get(), IterationCount({2}));
    communicator_.finish_reuse_iteration();

    cache = communicator_.pre_receive_f_init();
    ASSERT_EQ(decode_iteration(cache.at("unfiltered").data()).get(), IterationCount({2, 1, 0}));
    ASSERT_EQ(decode_iteration(cache.at("repeated").data()).get(), IterationCount({2, 1}));
    if (is_padded) {
        ASSERT_TRUE(cache.at("twicerepeated").data().is_nil());
    } else {
        ASSERT_EQ(decode_iteration(cache.at("twicerepeated").data()).get(), IterationCount({2}));
    }
    communicator_.finish_reuse_iteration();

    cache = communicator_.pre_receive_f_init();
    ASSERT_EQ(decode_iteration(cache.at("unfiltered").data()).get(), IterationCount({2, 1, 1}));
    if (is_padded) {
        ASSERT_TRUE(cache.at("repeated").data().is_nil());
        ASSERT_TRUE(cache.at("twicerepeated").data().is_nil());
    } else {
        ASSERT_EQ(decode_iteration(cache.at("repeated").data()).get(), IterationCount({2, 1}));
        ASSERT_EQ(decode_iteration(cache.at("twicerepeated").data()).get(), IterationCount({2}));
    }
    communicator_.finish_reuse_iteration();

    ASSERT_THROW(communicator_.pre_receive_f_init(), PortClosed);
}


INSTANTIATE_TEST_SUITE_P(
    repeated, libmuscle_repeater_communicator, ::testing::Values("repeat", "pad"));
