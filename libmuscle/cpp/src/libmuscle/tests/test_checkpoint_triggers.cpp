#include <gtest/gtest.h>

#include <libmuscle/checkpoint_triggers.hpp>

using libmuscle::impl::TriggerManager;
using libmuscle::impl::AtCheckpointTrigger;
using libmuscle::impl::RangeCheckpointTrigger;
using libmuscle::impl::CombinedCheckpointTriggers;
using libmuscle::impl::Data;

int main(int argc, char *argv[]) {
    ::testing::InitGoogleTest(&argc, argv);
    return RUN_ALL_TESTS();
}

TEST(libmuscle_checkpoint_triggers, test_at_checkpoint_trigger) {
    std::vector<double> at = {1, 3, 4, 4.5, 9};
    AtCheckpointTrigger trigger(at);

    ASSERT_DOUBLE_EQ(trigger.next_checkpoint(0).get(), 1);
    ASSERT_FALSE(trigger.previous_checkpoint(0).is_set());

    ASSERT_DOUBLE_EQ(trigger.next_checkpoint(1).get(),  3);
    ASSERT_DOUBLE_EQ(trigger.previous_checkpoint(1).get(), 1);

    double eps = 1e-16;
    ASSERT_DOUBLE_EQ(trigger.next_checkpoint(1 - eps).get(), 1);
    ASSERT_FALSE(trigger.previous_checkpoint(1 - eps).is_set());

    ASSERT_DOUBLE_EQ(trigger.next_checkpoint(3.9).get(), 4);
    ASSERT_DOUBLE_EQ(trigger.previous_checkpoint(3.9).get(), 3);

    ASSERT_DOUBLE_EQ(trigger.next_checkpoint(4.1).get(), 4.5);
    ASSERT_DOUBLE_EQ(trigger.previous_checkpoint(4.1).get(), 4);

    ASSERT_DOUBLE_EQ(trigger.next_checkpoint(5).get(), 9);
    ASSERT_DOUBLE_EQ(trigger.previous_checkpoint(5).get(), 4.5);

    ASSERT_FALSE(trigger.next_checkpoint(9).is_set());
    ASSERT_DOUBLE_EQ(trigger.previous_checkpoint(9).get(), 9);

    ASSERT_FALSE(trigger.next_checkpoint(11).is_set());
    ASSERT_DOUBLE_EQ(trigger.previous_checkpoint(11).get(), 9);
}

TEST(libmuscle_checkpoint_triggers, test_range_checkpoint_trigger) {
    auto range = Data::dict("start", 0, "stop", 20, "every", 1.2);
    RangeCheckpointTrigger trigger(range);

    ASSERT_DOUBLE_EQ(trigger.next_checkpoint(-1).get(), 0);
    ASSERT_FALSE(trigger.previous_checkpoint(-1).is_set());

    ASSERT_DOUBLE_EQ(trigger.next_checkpoint(0).get(), 1.2);
    ASSERT_DOUBLE_EQ(trigger.previous_checkpoint(0).get(), 0);

    ASSERT_DOUBLE_EQ(trigger.next_checkpoint(8).get(), 8.4);
    ASSERT_DOUBLE_EQ(trigger.previous_checkpoint(8).get(), 7.2);

    ASSERT_DOUBLE_EQ(trigger.next_checkpoint(18.2).get(), 19.2);
    ASSERT_DOUBLE_EQ(trigger.previous_checkpoint(18.2).get(), 18);

    ASSERT_FALSE(trigger.next_checkpoint(20).is_set());
    ASSERT_DOUBLE_EQ(trigger.previous_checkpoint(20).get(), 19.2);
}

TEST(libmuscle_checkpoint_triggers, test_range_checkpoint_trigger_default_stop) {
    auto range = Data::dict("start", 1, "stop", Data(), "every", 1.2);
    RangeCheckpointTrigger trigger(range);

    ASSERT_DOUBLE_EQ(trigger.next_checkpoint(-1.).get(), 1);
    ASSERT_FALSE(trigger.previous_checkpoint(-1.).is_set());

    ASSERT_DOUBLE_EQ(trigger.next_checkpoint(148148.).get(), 148148.2);
    ASSERT_DOUBLE_EQ(trigger.previous_checkpoint(148148.).get(), 148147);

    ASSERT_DOUBLE_EQ(trigger.next_checkpoint(148148148.).get(), 148148149);
    ASSERT_DOUBLE_EQ(trigger.previous_checkpoint(148148148.).get(), 148148147.8);
}

TEST(libmuscle_checkpoint_triggers, test_range_checkpoint_trigger_default_start) {
    auto range = Data::dict("start", Data(), "stop", 10, "every", 1.2);
    RangeCheckpointTrigger trigger(range);

    ASSERT_FALSE(trigger.next_checkpoint(10).is_set());
    ASSERT_DOUBLE_EQ(trigger.previous_checkpoint(10).get(), 9.6);

    ASSERT_DOUBLE_EQ(trigger.next_checkpoint(0.0).get(), 1.2);
    ASSERT_DOUBLE_EQ(trigger.previous_checkpoint(0.0).get(), 0.0);

    ASSERT_DOUBLE_EQ(trigger.next_checkpoint(-148148.).get(), -148147.2);
    ASSERT_DOUBLE_EQ(trigger.previous_checkpoint(-148148.).get(), -148148.4);
}

TEST(libmuscle_checkpoint_triggers, test_combined_checkpoint_trigger_every_at) {
    auto rules = Data::nils(2);
    rules[0] = Data::dict("start", Data(), "stop", Data(), "every", 10);
    rules[1] = Data::dict("at", Data::list(3, 7, 13, 17));
    CombinedCheckpointTriggers trigger(rules);

    ASSERT_DOUBLE_EQ(trigger.next_checkpoint(-11.).get(), -10);
    ASSERT_DOUBLE_EQ(trigger.previous_checkpoint(-11).get(), -20);

    ASSERT_DOUBLE_EQ(trigger.next_checkpoint(0.).get(), 3);
    ASSERT_DOUBLE_EQ(trigger.previous_checkpoint(0.).get(), 0);

    ASSERT_DOUBLE_EQ(trigger.next_checkpoint(8.3).get(), 10);
    ASSERT_DOUBLE_EQ(trigger.previous_checkpoint(8.3).get(), 7);

    ASSERT_DOUBLE_EQ(trigger.next_checkpoint(14.2).get(), 17);
    ASSERT_DOUBLE_EQ(trigger.previous_checkpoint(14.2).get(), 13);

    ASSERT_DOUBLE_EQ(trigger.next_checkpoint(25.2).get(), 30);
    ASSERT_DOUBLE_EQ(trigger.previous_checkpoint(25.2).get(), 20);
}

TEST(libmuscle_checkpoint_triggers, test_combined_checkpoint_trigger_at_ranges) {
    auto rules = Data::nils(3);
    rules[0] = Data::dict("at", Data::list(3, 7, 13, 17));
    rules[1] = Data::dict("start", 0, "stop", 20, "every", 5);
    rules[2] = Data::dict("start", 20, "stop", 100, "every", 20);
    CombinedCheckpointTriggers trigger(rules);

    ASSERT_DOUBLE_EQ(trigger.next_checkpoint(-11.).get(), 0);
    ASSERT_FALSE(trigger.previous_checkpoint(-11).is_set());

    ASSERT_DOUBLE_EQ(trigger.next_checkpoint(0.).get(), 3);
    ASSERT_DOUBLE_EQ(trigger.previous_checkpoint(0.).get(), 0);

    ASSERT_DOUBLE_EQ(trigger.next_checkpoint(8.3).get(), 10);
    ASSERT_DOUBLE_EQ(trigger.previous_checkpoint(8.3).get(), 7);

    ASSERT_DOUBLE_EQ(trigger.next_checkpoint(14.2).get(), 15);
    ASSERT_DOUBLE_EQ(trigger.previous_checkpoint(14.2).get(), 13);

    ASSERT_DOUBLE_EQ(trigger.next_checkpoint(19.3).get(), 20);
    ASSERT_DOUBLE_EQ(trigger.previous_checkpoint(19.3).get(), 17);

    ASSERT_DOUBLE_EQ(trigger.next_checkpoint(25.2).get(), 40);
    ASSERT_DOUBLE_EQ(trigger.previous_checkpoint(25.2).get(), 20);

    ASSERT_DOUBLE_EQ(trigger.next_checkpoint(95.2).get(), 100);
    ASSERT_DOUBLE_EQ(trigger.previous_checkpoint(95.2).get(), 80);

    ASSERT_FALSE(trigger.next_checkpoint(125.2).is_set());
    ASSERT_DOUBLE_EQ(trigger.previous_checkpoint(125.2).get(), 100);
}

TEST(libmuscle_checkpoint_triggers, test_trigger_manager_reference_time) {
    auto encoded_checkpoints = Data::dict(
        "at_end", true,
        "wallclock_time", Data::list(),
        "simulation_time", Data::list()
    );

    auto start = std::chrono::steady_clock::now();
    double ref_elapsed = 15.0;

    TriggerManager trigger_manager;
    trigger_manager.set_checkpoint_info(ref_elapsed, encoded_checkpoints);
    double elapsed_walltime = trigger_manager.elapsed_walltime();
    auto duration = std::chrono::steady_clock::now() - start;
    double duration_d = std::chrono::duration<double>(duration).count();

    ASSERT_LT(ref_elapsed, elapsed_walltime);
    ASSERT_LT(elapsed_walltime, ref_elapsed + duration_d);
}

TEST(libmuscle_checkpoint_triggers, test_trigger_manager) {
    double ref_elapsed = 0.0;
    TriggerManager trigger_manager;

    auto wallclock_time_list = Data::nils(1);
    wallclock_time_list[0] = Data::dict("at", Data::list(1e-12));
    auto simulation_time_list = Data::nils(1);
    simulation_time_list[0] = Data::dict("at", Data::list(1, 3, 5));
    auto encoded_checkpoints = Data::dict(
        "at_end", true,
        "wallclock_time", wallclock_time_list,
        "simulation_time", simulation_time_list
    );
    trigger_manager.set_checkpoint_info(ref_elapsed, encoded_checkpoints);

    ASSERT_TRUE(trigger_manager.should_save_snapshot(0.1));
    auto triggers = trigger_manager.get_triggers();
    ASSERT_EQ(triggers.size(), 1);
    ASSERT_NE(triggers[0].find("wallclock_time"), std::string::npos);
    trigger_manager.update_checkpoints(0.1);

    ASSERT_FALSE(trigger_manager.should_save_snapshot(0.99));

    ASSERT_TRUE(trigger_manager.should_save_snapshot(3.2));
    triggers = trigger_manager.get_triggers();
    ASSERT_EQ(triggers.size(), 1);
    ASSERT_NE(triggers[0].find("simulation_time"), std::string::npos);
    trigger_manager.update_checkpoints(3.2);

    ASSERT_TRUE(trigger_manager.should_save_final_snapshot(true, 7.0));
    ASSERT_GT(trigger_manager.get_triggers().size(), 0);
    trigger_manager.update_checkpoints(7.0);

    ASSERT_FALSE(trigger_manager.should_save_snapshot(7.1));

    ASSERT_TRUE(trigger_manager.should_save_final_snapshot(false, {}));
    trigger_manager.update_checkpoints(7.1);
}

TEST(libmuscle_checkpoint_triggers, test_no_checkpointing) {
    TriggerManager trigger_manager;
    auto encoded_checkpoints = Data::dict(
        "at_end", false,
        "wallclock_time", Data::list(),
        "simulation_time", Data::list()
    );
    trigger_manager.set_checkpoint_info(0.0, encoded_checkpoints);
    ASSERT_FALSE(trigger_manager.should_save_snapshot(1));
    ASSERT_FALSE(trigger_manager.should_save_snapshot(5000));
    ASSERT_FALSE(trigger_manager.should_save_final_snapshot(false, {}));
}
