#include <gtest/gtest.h>

#include <libmuscle/snapshot.hpp>

using libmuscle::_MUSCLE_IMPL_NS::Data;
using libmuscle::_MUSCLE_IMPL_NS::Message;
using libmuscle::_MUSCLE_IMPL_NS::Optional;
using libmuscle::_MUSCLE_IMPL_NS::Snapshot;
using libmuscle::_MUSCLE_IMPL_NS::SnapshotMetadata;

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

    ASSERT_EQ(snapshot.triggers.size(), 1);
    ASSERT_STREQ(snapshot.triggers[0].c_str(), "test triggers");
    ASSERT_DOUBLE_EQ(snapshot.wallclock_time, 15.3);
    ASSERT_EQ(snapshot.port_message_counts.size(), 3);
    ASSERT_EQ(snapshot.port_message_counts.at("in"), std::vector<int>({1}));
    ASSERT_EQ(snapshot.port_message_counts.at("out"), std::vector<int>({4}));
    ASSERT_EQ(snapshot.port_message_counts.at("muscle_settings_in"),
              std::vector<int>({0}));
    ASSERT_TRUE(snapshot.is_final_snapshot);
    ASSERT_TRUE(snapshot.message.is_set());
    ASSERT_DOUBLE_EQ(snapshot.message.get().timestamp(), 1.2);
    ASSERT_FALSE(snapshot.message.get().has_next_timestamp());
    ASSERT_FALSE(snapshot.message.get().has_settings());
    ASSERT_STREQ(snapshot.message.get().data().as<std::string>().c_str(),
                 "test_data");
    ASSERT_EQ(snapshot.settings_overlay["test"], 1);

    auto binary_snapshot = snapshot.to_bytes();
    Snapshot snapshot2 = Snapshot::from_bytes(binary_snapshot);

    ASSERT_EQ(snapshot.triggers, snapshot2.triggers);
    ASSERT_EQ(snapshot.wallclock_time, snapshot2.wallclock_time);
    ASSERT_EQ(snapshot.port_message_counts, snapshot2.port_message_counts);
    ASSERT_EQ(snapshot.is_final_snapshot, snapshot2.is_final_snapshot);
    ASSERT_EQ(snapshot.message.get().timestamp(),
              snapshot2.message.get().timestamp());
    ASSERT_EQ(snapshot.message.get().data().as<std::string>(),
              snapshot2.message.get().data().as<std::string>());
    ASSERT_EQ(snapshot.settings_overlay, snapshot2.settings_overlay);
}

TEST(libmuscle_snapshot, test_snapshot_metadata) {
    auto snapshot = create_snapshot();

    auto metadata = SnapshotMetadata::from_snapshot(snapshot, "test");
    ASSERT_EQ(metadata.triggers, snapshot.triggers);
    ASSERT_EQ(metadata.wallclock_time, snapshot.wallclock_time);
    ASSERT_EQ(metadata.port_message_counts, snapshot.port_message_counts);
    ASSERT_EQ(metadata.is_final_snapshot, snapshot.is_final_snapshot);
    ASSERT_EQ(metadata.timestamp, snapshot.message.get().timestamp());
    ASSERT_EQ(metadata.next_timestamp.is_set(),
              snapshot.message.get().has_next_timestamp());
    ASSERT_EQ(metadata.snapshot_filename, "test");
}

TEST(libmuscle_snapshot, test_message_with_settings) {
    ::ymmsl::Settings settings;
    settings["b"] = true;
    Message message(1.0, 2.0, "test_data", settings);
    Snapshot snapshot ({}, 0, {}, false, message, {});
    ASSERT_TRUE(snapshot.message.get().settings().at("b").as<bool>());

    auto binary_snapshot = snapshot.to_bytes();
    Snapshot snapshot2 = Snapshot::from_bytes(binary_snapshot);

    ASSERT_TRUE(snapshot2.message.get().settings().at("b").as<bool>());
}

TEST(libmuscle_snapshot, test_implicit_snapshot) {
    Optional<Message> message;
    Snapshot snapshot({}, 0, {}, true, message, {});
    ASSERT_FALSE(snapshot.message.is_set());


    auto binary_snapshot = snapshot.to_bytes();
    Snapshot snapshot2 = Snapshot::from_bytes(binary_snapshot);

    ASSERT_FALSE(snapshot2.message.is_set());
}
