#include <gtest/gtest.h>

#include <libmuscle/snapshot.hpp>

using libmuscle::impl::Data;
using libmuscle::impl::Message;
using libmuscle::impl::Snapshot;

int main(int argc, char *argv[]) {
    ::testing::InitGoogleTest(&argc, argv);
    return RUN_ALL_TESTS();
}

Snapshot create_snapshot() {
    ::ymmsl::Settings settings;
    settings["test"] = 1;
    return Snapshot(
            {"test triggers"},
            15.3,
            {{"in", {1}}, {"out", {4}}, {"muscle_settings_in", {0}}},
            true,
            Message(1.2, "test_data"),
            settings
            );
}

TEST(libmuscle_snapshot, test_snapshot) {
    auto snapshot = create_snapshot();

    ASSERT_EQ(snapshot.triggers_.size(), 1);
    ASSERT_STREQ(snapshot.triggers_[0].c_str(), "test triggers");
    ASSERT_DOUBLE_EQ(snapshot.wallclock_time_, 15.3);
    ASSERT_EQ(snapshot.port_message_counts_.size(), 3);
    ASSERT_EQ(snapshot.port_message_counts_.at("in"), std::vector<int>({1}));
    ASSERT_EQ(snapshot.port_message_counts_.at("out"), std::vector<int>({4}));
    ASSERT_EQ(snapshot.port_message_counts_.at("muscle_settings_in"),
              std::vector<int>({0}));
    ASSERT_TRUE(snapshot.is_final_snapshot_);
    ASSERT_TRUE(snapshot.message_.is_set());
    ASSERT_DOUBLE_EQ(snapshot.message_.get().timestamp(), 1.2);
    ASSERT_FALSE(snapshot.message_.get().has_next_timestamp());
    ASSERT_FALSE(snapshot.message_.get().has_settings());
    ASSERT_STREQ(snapshot.message_.get().data().as<std::string>().c_str(),
                 "test_data");
    ASSERT_EQ(snapshot.settings_overlay_["test"], 1);

    auto binary_snapshot = snapshot.to_bytes();
    Snapshot snapshot2 = Snapshot::from_bytes(binary_snapshot);

    ASSERT_EQ(snapshot.triggers_, snapshot2.triggers_);
    ASSERT_EQ(snapshot.wallclock_time_, snapshot2.wallclock_time_);
    ASSERT_EQ(snapshot.port_message_counts_, snapshot2.port_message_counts_);
    ASSERT_EQ(snapshot.is_final_snapshot_, snapshot2.is_final_snapshot_);
    ASSERT_EQ(snapshot.message_.get().timestamp(),
              snapshot2.message_.get().timestamp());
    ASSERT_EQ(snapshot.message_.get().data().as<std::string>(),
              snapshot2.message_.get().data().as<std::string>());
    ASSERT_EQ(snapshot.settings_overlay_, snapshot2.settings_overlay_);
}
