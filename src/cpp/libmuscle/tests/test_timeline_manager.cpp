// Inject the real implementation under test.
#include <ymmsl/ymmsl.hpp>

#include <libmuscle/peer_info.cpp>
#include <libmuscle/port.cpp>
#include <libmuscle/port_manager.cpp>
#include <libmuscle/timeline_manager.cpp>

// Test code dependencies
#include <memory>
#include <unordered_map>
#include <vector>

#include <gtest/gtest.h>


int main(int argc, char *argv[]) {
    ::testing::InitGoogleTest(&argc, argv);
    return RUN_ALL_TESTS();
}


using libmuscle::_MUSCLE_IMPL_NS::is_subiteration;
using libmuscle::_MUSCLE_IMPL_NS::AlreadyParticipated;
using libmuscle::_MUSCLE_IMPL_NS::ExpectedActions;
using libmuscle::_MUSCLE_IMPL_NS::IterationCount;
using libmuscle::_MUSCLE_IMPL_NS::MessageOutOfSync;
using libmuscle::_MUSCLE_IMPL_NS::Optional;
using libmuscle::_MUSCLE_IMPL_NS::PeerDims;
using libmuscle::_MUSCLE_IMPL_NS::PeerInfo;
using libmuscle::_MUSCLE_IMPL_NS::PeerLocations;
using libmuscle::_MUSCLE_IMPL_NS::Port;
using libmuscle::_MUSCLE_IMPL_NS::PortBlocked;
using libmuscle::_MUSCLE_IMPL_NS::PortManager;
using libmuscle::_MUSCLE_IMPL_NS::PortsDescription;
using libmuscle::_MUSCLE_IMPL_NS::ReuseLoopIncomplete;
using libmuscle::_MUSCLE_IMPL_NS::TimelineManager;
using libmuscle::_MUSCLE_IMPL_NS::TimelineState;

using ymmsl::Conduit;
using ymmsl::Identifier;
using ymmsl::Operator;
using ymmsl::Reference;
using ymmsl::Timeline;


namespace {

/* Build a PortManager with the given declared ports, connected via synthetic conduits, one
 * peer component per port so that vector ports can each get their own peer dimensions.
 *
 * timelines maps a (stripped, no "[]") port name to the Timeline it should be on; ports not
 * listed default to the root timeline. peer_dims maps a port name to the peer's dimensions
 * (default {} for a scalar peer). */
std::unique_ptr<PortManager> make_port_manager(
        PortsDescription const & declared_ports,
        std::unordered_map<std::string, Timeline> const & timelines = {},
        std::unordered_map<std::string, std::vector<int>> const & peer_dims_by_port = {},
        bool include_settings = false) {
    auto port_manager = std::make_unique<PortManager>(std::vector<int>(), declared_ports);

    Reference component_id("component");
    std::vector<Conduit> conduits;
    std::vector<::ymmsl::Port> ymmsl_ports;
    PeerDims peer_dims;
    PeerLocations peer_locations;

    for (auto const & item : declared_ports) {
        for (auto const & port_desc : item.second) {
            std::string port_name = port_desc;
            if (port_name.size() > 2 && port_name.substr(port_name.size() - 2) == "[]")
                port_name = port_name.substr(0, port_name.size() - 2);

            std::string peer_name = "peer_" + port_name;
            if (::ymmsl::allows_receiving(item.first))
                conduits.emplace_back(peer_name + "." + port_name, "component." + port_name);
            else
                conduits.emplace_back("component." + port_name, peer_name + "." + port_name);

            auto dims_it = peer_dims_by_port.find(port_name);
            peer_dims[Reference(peer_name)] =
                    (dims_it != peer_dims_by_port.end()) ? dims_it->second : std::vector<int>();
            peer_locations[Reference(peer_name)] = {"direct:test"};

            auto tl_it = timelines.find(port_name);
            Timeline tl = (tl_it != timelines.end()) ? tl_it->second : Timeline("");
            ymmsl_ports.emplace_back(Identifier(port_name), item.first, tl);
        }
    }

    if (include_settings) {
        conduits.emplace_back(
                "peer_muscle_settings_in.muscle_settings_in", "component.muscle_settings_in");
        peer_dims[Reference("peer_muscle_settings_in")] = {};
        peer_locations[Reference("peer_muscle_settings_in")] = {"direct:test"};
    }

    PeerInfo peer_info(component_id, {}, conduits, peer_dims, peer_locations, ymmsl_ports);
    port_manager->connect_ports(peer_info);
    return port_manager;
}

/* check_receive_s + record_received_s_message, as Communicator::receive_message does. */
void check_received(
        TimelineManager & tm, std::string const & port_name, Optional<int> slot,
        IterationCount const & iteration) {
    tm.check_receive_s(port_name, slot);
    tm.record_received_s_message(port_name, slot, iteration);
}

}   // anonymous namespace


struct libmuscle_timeline_manager : ::testing::Test {
    std::unique_ptr<PortManager> port_manager_;
    std::unique_ptr<TimelineManager> tm_;

    void create(
            PortsDescription const & declared_ports,
            std::unordered_map<std::string, Timeline> const & timelines = {},
            bool include_settings = false) {
        port_manager_ = make_port_manager(declared_ports, timelines, {}, include_settings);
        tm_ = std::make_unique<TimelineManager>(*port_manager_);
    }
};


/* Mirrors the Python test suite's fixture: main timeline (in_f/out_f) plus two
 * sub-timelines, :A1 (one O_I port, two S ports: an O_I-leads-many-S scenario) and :A2
 * (two O_I ports, one S port: the mirror-image many-O_I-leads-one-S scenario). */
struct libmuscle_full_timeline_manager : libmuscle_timeline_manager {
    libmuscle_full_timeline_manager() {
        create(
                PortsDescription{
                    {Operator::F_INIT, {"in_f"}},
                    {Operator::O_F, {"out_f"}},
                    {Operator::O_I, {"out_a1", "out_a2", "out_a2_2"}},
                    {Operator::S, {"in_a1", "in_a1_2", "in_a2"}}},
                {
                    {"out_a1", Timeline(":A1")},
                    {"in_a1", Timeline(":A1")},
                    {"in_a1_2", Timeline(":A1")},
                    {"out_a2", Timeline(":A2")},
                    {"out_a2_2", Timeline(":A2")},
                    {"in_a2", Timeline(":A2")},
                },
                true);
    }
};


struct libmuscle_vector_timeline_manager : libmuscle_timeline_manager {
    libmuscle_vector_timeline_manager() {
        port_manager_ = make_port_manager(
                PortsDescription{{Operator::O_F, {"out_v[]"}}}, {}, {{"out_v", {3}}});
        tm_ = std::make_unique<TimelineManager>(*port_manager_);
    }
};


TEST_F(libmuscle_full_timeline_manager, is_subiteration) {
    ASSERT_TRUE(is_subiteration({}, {}));
    ASSERT_TRUE(is_subiteration({1, 2}, {1, 2}));
    ASSERT_TRUE(is_subiteration({1, 2}, {1}));
    ASSERT_TRUE(is_subiteration({1, 2}, {}));
    ASSERT_FALSE(is_subiteration({1, 2}, {1, 2, 3}));
    ASSERT_FALSE(is_subiteration({1, 2}, {1, 1}));
}

// -- Main timeline: F_INIT / O_F --

TEST_F(libmuscle_full_timeline_manager, check_finit_iterations) {
    IterationCount first = {1, 2, 3, 4};
    ASSERT_EQ(tm_->check_f_init_iterations({
        {"in_f", first},
        {"muscle_settings_in", first},
    }), first);

    ASSERT_EQ(tm_->check_send_message("out_f"), first);
}

TEST_F(libmuscle_full_timeline_manager, check_finit_iterations_when_iteration_differs) {
    ASSERT_THROW(tm_->check_f_init_iterations({
        {"in_f", {3}},
        {"muscle_settings_in", {4}},
    }), std::runtime_error);
}

TEST_F(libmuscle_timeline_manager, o_f_can_send_immediately_when_no_f_init_connections) {
    create(PortsDescription{{Operator::O_F, {"out_f"}}});

    IterationCount iteration = tm_->check_send_message("out_f");
    ASSERT_EQ(iteration, IterationCount());
    ASSERT_THROW(tm_->check_send_message("out_f"), AlreadyParticipated);
}

TEST_F(libmuscle_full_timeline_manager, o_f_blocked_while_subtimeline_incomplete) {
    tm_->check_f_init_iterations({
        {"in_f", {3}},
        {"muscle_settings_in", {3}},
    });

    tm_->check_send_message("out_a1");  // starts :A1, but doesn't complete it

    ASSERT_THROW(tm_->check_send_message("out_f"), PortBlocked);
}

TEST_F(libmuscle_full_timeline_manager, o_f_send_records_iteration_and_participation) {
    tm_->check_f_init_iterations({
        {"in_f", {3}},
        {"muscle_settings_in", {3}},
    });

    IterationCount iteration = tm_->check_send_message("out_f");
    ASSERT_EQ(iteration, IterationCount({3}));
    ASSERT_THROW(tm_->check_send_message("out_f"), AlreadyParticipated);
}


// -- Sub-timeline O_I/S leadership races --

TEST_F(libmuscle_full_timeline_manager, o_i_leads_first_send_starts_subtimeline_at_zero) {
    tm_->check_f_init_iterations({
        {"in_f", {3}},
        {"muscle_settings_in", {3}},
    });

    IterationCount iteration = tm_->check_send_message("out_a1");
    ASSERT_EQ(iteration, IterationCount({3, 0}));
}

TEST_F(libmuscle_full_timeline_manager, o_i_leads_second_send_blocked_until_all_s_received) {
    tm_->check_f_init_iterations({
        {"in_f", {3}},
        {"muscle_settings_in", {3}},
    });

    tm_->check_send_message("out_a1");
    check_received(*tm_, "in_a1", {}, {3, 0});
    // in_a1_2 hasn't received yet

    ASSERT_THROW(tm_->check_send_message("out_a1"), PortBlocked);
}

TEST_F(libmuscle_full_timeline_manager, o_i_leads_advances_once_all_s_received) {
    tm_->check_f_init_iterations({
        {"in_f", {3}},
        {"muscle_settings_in", {3}},
    });

    IterationCount first = tm_->check_send_message("out_a1");
    check_received(*tm_, "in_a1", {}, first);
    check_received(*tm_, "in_a1_2", {}, first);

    IterationCount second = tm_->check_send_message("out_a1");
    ASSERT_EQ(first, IterationCount({3, 0}));
    ASSERT_EQ(second, IterationCount({3, 1}));
}

TEST_F(libmuscle_full_timeline_manager, s_leads_first_receive_starts_subtimeline) {
    tm_->check_f_init_iterations({
        {"in_f", {3}},
        {"muscle_settings_in", {3}},
    });

    check_received(*tm_, "in_a1", {}, {7});
    // second receive on the same port before O_I sends anything is blocked
    ASSERT_THROW(tm_->check_receive_s("in_a1"), PortBlocked);
}

TEST_F(libmuscle_full_timeline_manager, s_leads_o_i_blocked_until_all_s_received) {
    tm_->check_f_init_iterations({
        {"in_f", {3}},
        {"muscle_settings_in", {3}},
    });

    check_received(*tm_, "in_a1", {}, {7});
    // in_a1_2 hasn't received yet, so S hasn't fully led :A1 yet

    ASSERT_THROW(tm_->check_send_message("out_a1"), PortBlocked);
}

TEST_F(libmuscle_full_timeline_manager, s_leads_advances_on_strictly_later_iteration) {
    tm_->check_f_init_iterations({
        {"in_f", {3}},
        {"muscle_settings_in", {3}},
    });

    check_received(*tm_, "in_a1", {}, {7});
    check_received(*tm_, "in_a1_2", {}, {7});

    tm_->check_send_message("out_a1");

    // an equal-or-earlier iteration on the already-participated S port is out of sync
    tm_->check_receive_s("in_a1");
    ASSERT_THROW(tm_->record_received_s_message("in_a1", {}, {7}), MessageOutOfSync);

    // a strictly later one advances the sub-iteration
    check_received(*tm_, "in_a1", {}, {8});
}

TEST_F(libmuscle_full_timeline_manager, many_o_i_one_s_mirror_scenario) {
    tm_->check_f_init_iterations({
        {"in_f", {3}},
        {"muscle_settings_in", {3}},
    });

    // :A2 has two O_I ports (out_a2, out_a2_2) and one S port (in_a2)
    tm_->check_send_message("out_a2");
    ASSERT_THROW(tm_->check_send_message("out_a2"), PortBlocked);

    IterationCount iteration = tm_->check_send_message("out_a2_2");
    check_received(*tm_, "in_a2", {}, iteration);

    IterationCount second = tm_->check_send_message("out_a2");
    ASSERT_EQ(second.back(), iteration.back() + 1);
}


// -- Reuse loop completion / reset --

TEST_F(libmuscle_full_timeline_manager, finish_reuse_iteration_raises_when_incomplete) {
    tm_->check_f_init_iterations({
        {"in_f", {3}},
        {"muscle_settings_in", {3}},
    });
    // out_f never sent

    ASSERT_THROW(tm_->finish_reuse_iteration(), ReuseLoopIncomplete);
}

TEST_F(libmuscle_full_timeline_manager, finish_reuse_iteration_resets_when_complete) {
    tm_->check_f_init_iterations({
        {"in_f", {3}},
        {"muscle_settings_in", {3}},
    });
    tm_->check_send_message("out_f");

    tm_->finish_reuse_iteration();

    // fully reset: the same sequence works again from scratch
    tm_->check_f_init_iterations({
        {"in_f", {4}},
        {"muscle_settings_in", {4}},
    });
    IterationCount iteration = tm_->check_send_message("out_f");
    ASSERT_EQ(iteration, IterationCount({4}));
}

TEST_F(libmuscle_full_timeline_manager, finish_reuse_iteration_ok_when_subtimeline_unused) {
    // a sub-timeline never touched this iteration doesn't block completion
    tm_->check_f_init_iterations({
        {"in_f", {3}},
        {"muscle_settings_in", {3}},
    });
    tm_->check_send_message("out_f");

    ASSERT_NO_THROW(tm_->finish_reuse_iteration());
}


// -- Snapshot state round-trip --

TEST_F(libmuscle_full_timeline_manager, get_state_and_restore_state_round_trip) {
    tm_->check_f_init_iterations({
        {"in_f", {3}},
        {"muscle_settings_in", {3}},
    });
    tm_->check_send_message("out_a1");
    check_received(*tm_, "in_a1", {}, {3, 0});
    // in_a1_2 not yet received, so :A1 is incomplete, and out_f not yet sent

    TimelineState state = tm_->get_state();

    TimelineManager restored(*port_manager_);
    restored.restore_state(state);

    TimelineState restored_state = restored.get_state();
    ASSERT_EQ(state.iteration.is_set(), restored_state.iteration.is_set());
    ASSERT_EQ(state.iteration.get(), restored_state.iteration.get());
    ASSERT_EQ(state.send_participated, restored_state.send_participated);
    ASSERT_EQ(
            state.subtimeline_states.size(), restored_state.subtimeline_states.size());
}

TEST_F(libmuscle_full_timeline_manager, state_data_round_trip_through_msgpack_shape) {
    tm_->check_f_init_iterations({
        {"in_f", {3}},
        {"muscle_settings_in", {3}},
    });
    tm_->check_send_message("out_a1");
    check_received(*tm_, "in_a1", {}, {3, 0});

    TimelineState state = tm_->get_state();
    auto data = state.to_data();
    TimelineState round_tripped = TimelineState::from_data(data);

    ASSERT_EQ(state.iteration.is_set(), round_tripped.iteration.is_set());
    ASSERT_EQ(state.iteration.get(), round_tripped.iteration.get());
    ASSERT_EQ(state.send_participated, round_tripped.send_participated);
    ASSERT_EQ(
            state.subtimeline_states.size(), round_tripped.subtimeline_states.size());
}


// -- Vector ports: per-slot participation --

TEST_F(libmuscle_vector_timeline_manager, each_slot_participates_independently) {
    tm_->check_send_message("out_v", 0);
    ASSERT_THROW(tm_->check_send_message("out_v", 0), AlreadyParticipated);

    tm_->check_send_message("out_v", 1);
    ASSERT_NO_THROW(tm_->check_send_message("out_v", 2));
}

TEST_F(libmuscle_vector_timeline_manager, reuse_loop_incomplete_lists_missing_slots) {
    tm_->check_send_message("out_v", 0);

    ASSERT_THROW(tm_->finish_reuse_iteration(), ReuseLoopIncomplete);
}

TEST_F(libmuscle_vector_timeline_manager, finish_reuse_iteration_ok_once_all_slots_sent) {
    tm_->check_send_message("out_v", 0);
    tm_->check_send_message("out_v", 1);
    tm_->check_send_message("out_v", 2);

    ASSERT_NO_THROW(tm_->finish_reuse_iteration());
}
