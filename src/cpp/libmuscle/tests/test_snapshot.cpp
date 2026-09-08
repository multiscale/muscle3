// Inject mocks
#define LIBMUSCLE_MOCK_PORT_MANAGER <mocks/mock_port_manager.hpp>

#include <gtest/gtest.h>

#include <msgpack.hpp>

#include <libmuscle/data.hpp>
#include <libmuscle/mcp/data_pack.hpp>
#include <libmuscle/namespace.hpp>
#include <libmuscle/snapshot.hpp>
#include <libmuscle/tests/fixtures.hpp>

using libmuscle::_MUSCLE_IMPL_NS::Data;
using libmuscle::_MUSCLE_IMPL_NS::Message;
using libmuscle::_MUSCLE_IMPL_NS::Optional;
using libmuscle::_MUSCLE_IMPL_NS::Snapshot;
using libmuscle::_MUSCLE_IMPL_NS::SnapshotMetadata;
using libmuscle::_MUSCLE_IMPL_NS::SubTimelineState;
using libmuscle::_MUSCLE_IMPL_NS::TimelineState;

int main(int argc, char *argv[]) {
    ::testing::InitGoogleTest(&argc, argv);
    return RUN_ALL_TESTS();
}

/* Fixture */
struct libmuscle_snapshot : CommunicatorStateFixture, ::testing::Test {
    Snapshot snapshot_;

    libmuscle_snapshot()
        : snapshot_(
            {"test triggers"},
            15.3,
            true,
            Message(1.2, "test_data"),
            ::ymmsl::Settings({{"test", 1}}),
            communicator_state_
        ) {}
};

TEST_F(libmuscle_snapshot, test_snapshot) {
    ASSERT_EQ(snapshot_.triggers.size(), 1);
    ASSERT_STREQ(snapshot_.triggers[0].c_str(), "test triggers");
    ASSERT_DOUBLE_EQ(snapshot_.wallclock_time, 15.3);
    ASSERT_TRUE(snapshot_.is_final_snapshot);
    ASSERT_TRUE(snapshot_.message.is_set());
    ASSERT_DOUBLE_EQ(snapshot_.message.get().timestamp(), 1.2);
    ASSERT_FALSE(snapshot_.message.get().has_next_timestamp());
    ASSERT_FALSE(snapshot_.message.get().has_settings());
    ASSERT_STREQ(snapshot_.message.get().data().as<std::string>().c_str(),
                 "test_data");
    ASSERT_EQ(snapshot_.settings_overlay["test"], 1);

    auto binary_snapshot = snapshot_.to_bytes();
    Snapshot snapshot2 = Snapshot::from_bytes(binary_snapshot);

    ASSERT_EQ(snapshot_.triggers, snapshot2.triggers);
    ASSERT_EQ(snapshot_.wallclock_time, snapshot2.wallclock_time);
    ASSERT_EQ(snapshot_.is_final_snapshot, snapshot2.is_final_snapshot);
    ASSERT_EQ(snapshot_.message.get().timestamp(),
              snapshot2.message.get().timestamp());
    ASSERT_EQ(snapshot_.message.get().data().as<std::string>(),
              snapshot2.message.get().data().as<std::string>());
    ASSERT_EQ(snapshot_.settings_overlay, snapshot2.settings_overlay);
    ASSERT_EQ(snapshot_.communicator_state.port_message_counts,
              snapshot2.communicator_state.port_message_counts);
    ASSERT_EQ(snapshot_.communicator_state.timeline_state.iteration.is_set(),
              snapshot2.communicator_state.timeline_state.iteration.is_set());
    ASSERT_EQ(snapshot_.communicator_state.timeline_state.iteration.get(),
              snapshot2.communicator_state.timeline_state.iteration.get());
    ASSERT_EQ(snapshot_.communicator_state.timeline_state.send_participated,
              snapshot2.communicator_state.timeline_state.send_participated);
    ASSERT_EQ(snapshot_.communicator_state.timeline_state.subtimeline_states.size(),
              snapshot2.communicator_state.timeline_state.subtimeline_states.size());
}

TEST_F(libmuscle_snapshot, test_snapshot_metadata) {
    auto metadata = SnapshotMetadata::from_snapshot(snapshot_, "test");
    ASSERT_EQ(metadata.triggers, snapshot_.triggers);
    ASSERT_EQ(metadata.wallclock_time, snapshot_.wallclock_time);
    ASSERT_EQ(metadata.port_message_counts, snapshot_.communicator_state.port_message_counts);
    ASSERT_EQ(metadata.is_final_snapshot, snapshot_.is_final_snapshot);
    ASSERT_EQ(metadata.timestamp, snapshot_.message.get().timestamp());
    ASSERT_EQ(metadata.next_timestamp.is_set(),
              snapshot_.message.get().has_next_timestamp());
    ASSERT_EQ(metadata.snapshot_filename, "test");
}

TEST_F(libmuscle_snapshot, test_message_with_settings) {
    ::ymmsl::Settings settings;
    settings["b"] = true;
    Message message(1.0, 2.0, "test_data", settings);
    Snapshot snapshot (
            {}, 0, false, message, {}, communicator_state_);
    ASSERT_TRUE(snapshot.message.get().settings().at("b").as<bool>());

    auto binary_snapshot = snapshot.to_bytes();
    Snapshot snapshot2 = Snapshot::from_bytes(binary_snapshot);

    ASSERT_TRUE(snapshot2.message.get().settings().at("b").as<bool>());
}

TEST_F(libmuscle_snapshot, test_implicit_snapshot) {
    Optional<Message> message;
    Snapshot snapshot(
            {}, 0, true, message, {}, communicator_state_);
    ASSERT_FALSE(snapshot.message.is_set());


    auto binary_snapshot = snapshot.to_bytes();
    Snapshot snapshot2 = Snapshot::from_bytes(binary_snapshot);

    ASSERT_FALSE(snapshot2.message.is_set());
}
