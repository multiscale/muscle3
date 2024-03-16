// Inject mocks
#define LIBMUSCLE_MOCK_LOGGER <mocks/mock_logger.hpp>
#define LIBMUSCLE_MOCK_MMP_CLIENT <mocks/mock_mmp_client.hpp>
#define LIBMUSCLE_MOCK_PORT_MANAGER <mocks/mock_port_manager.hpp>
#define LIBMUSCLE_MOCK_PROFILER <mocks/mock_profiler.hpp>
#define LIBMUSCLE_MOCK_TRIGGER_MANAGER <mocks/mock_trigger_manager.hpp>

// into the real implementation to test.
#include <ymmsl/ymmsl.hpp>

#include <libmuscle/close_port.cpp>
#include <libmuscle/communicator.cpp>
#include <libmuscle/data.cpp>
#include <libmuscle/instance.cpp>
#include <libmuscle/logging.cpp>
#include <libmuscle/mcp/data_pack.cpp>
#include <libmuscle/message.cpp>
#include <libmuscle/port.cpp>
#include <libmuscle/settings_manager.cpp>
#include <libmuscle/snapshot_manager.cpp>
#include <libmuscle/timestamp.cpp>

// Test code dependencies
#include <cstdio>
#include <iostream>
#include <memory>
#include <stdexcept>
#include <typeinfo>

#include <gtest/gtest.h>
#include <libmuscle/namespace.hpp>
#include <libmuscle/snapshot_manager.hpp>
#include <libmuscle/tests/fixtures.hpp>
#include <mocks/mock_logger.hpp>
#include <mocks/mock_mmp_client.hpp>
#include <mocks/mock_port_manager.hpp>
#include <mocks/mock_profiler.hpp>
#include <mocks/mock_trigger_manager.hpp>


using libmuscle::_MUSCLE_IMPL_NS::Data;
using libmuscle::_MUSCLE_IMPL_NS::Message;
using PortMessageCounts = libmuscle::_MUSCLE_IMPL_NS::MockPortManager::PortMessageCounts;
using libmuscle::_MUSCLE_IMPL_NS::Optional;
using libmuscle::_MUSCLE_IMPL_NS::PortsDescription;
using libmuscle::_MUSCLE_IMPL_NS::Snapshot;
using libmuscle::_MUSCLE_IMPL_NS::SnapshotMetadata;
using libmuscle::_MUSCLE_IMPL_NS::SnapshotManager;
using libmuscle::_MUSCLE_IMPL_NS::TriggerManager;
using ymmsl::Reference;

int main(int argc, char *argv[]) {
    ::testing::InitGoogleTest(&argc, argv);
    return RUN_ALL_TESTS();
}

struct libmuscle_snapshot_manager : ::testing::Test, TempDirFixture {
    RESET_MOCKS(
            ::libmuscle::_MUSCLE_IMPL_NS::MockMMPClient,
            ::libmuscle::_MUSCLE_IMPL_NS::MockLogger,
            ::libmuscle::_MUSCLE_IMPL_NS::MockPortManager,
            ::libmuscle::_MUSCLE_IMPL_NS::MockProfiler,
            ::libmuscle::_MUSCLE_IMPL_NS::MockTriggerManager);

    // std::string temp_dir_; from TempDirFixture
    ::libmuscle::_MUSCLE_IMPL_NS::MockLogger mock_logger_;
    ::libmuscle::_MUSCLE_IMPL_NS::MockProfiler mock_profiler_;
    ::libmuscle::_MUSCLE_IMPL_NS::MockPortManager mock_port_manager_;
    ::libmuscle::_MUSCLE_IMPL_NS::MockMMPClient mock_mmp_client_;
};


TEST_F(libmuscle_snapshot_manager, test_no_checkpointing) {
    SnapshotManager snapshot_manager(
            "test", mock_mmp_client_, mock_port_manager_, mock_logger_);

    snapshot_manager.prepare_resume({}, temp_dir_);
    ASSERT_FALSE(snapshot_manager.resuming_from_intermediate());
    ASSERT_FALSE(snapshot_manager.resuming_from_final());
}

TEST_F(libmuscle_snapshot_manager, test_save_load_snapshot) {
    mock_port_manager_.list_ports.return_value = PortsDescription(
            {{Operator::S, {"in"}}, {Operator::O_I, {"out"}}});
    PortMessageCounts port_message_counts = {
            {"in", {1}},
            {"out", {2}},
            {"muscle_settings_in", {0}}};
    mock_port_manager_.get_message_counts.return_value = port_message_counts;
    mock_port_manager_.settings_in_connected.return_value = false;

    Reference instance_id("test[1]");

    SnapshotManager snapshot_manager(
            instance_id, mock_mmp_client_, mock_port_manager_, mock_logger_);

    snapshot_manager.prepare_resume({}, temp_dir_);
    ASSERT_FALSE(snapshot_manager.resuming_from_intermediate());
    ASSERT_FALSE(snapshot_manager.resuming_from_final());

    snapshot_manager.save_snapshot(
            Message(0.2, "test data"), false, {"test"}, 13.0, {}, {});

    ASSERT_TRUE(mock_port_manager_.get_message_counts.called_with());
    ASSERT_TRUE(mock_mmp_client_.submit_snapshot_metadata.called());
    auto const & metadata = mock_mmp_client_.submit_snapshot_metadata.call_arg<0>();
    ASSERT_EQ(metadata.triggers, std::vector<std::string>({"test"}));
    ASSERT_EQ(metadata.wallclock_time, 13.0);
    ASSERT_EQ(metadata.timestamp, 0.2);
    ASSERT_FALSE(metadata.next_timestamp.is_set());
    ASSERT_EQ(metadata.port_message_counts, port_message_counts);
    ASSERT_FALSE(metadata.is_final_snapshot);
    auto snapshot_path = metadata.snapshot_filename;
    ASSERT_EQ(snapshot_path, temp_dir_ + "/test-1_1.pack");

    SnapshotManager snapshot_manager2(
            instance_id, mock_mmp_client_, mock_port_manager_, mock_logger_);
    snapshot_manager2.prepare_resume(snapshot_path, temp_dir_);
    ASSERT_TRUE(mock_port_manager_.restore_message_counts.called_once());
    ASSERT_EQ(
            mock_port_manager_.restore_message_counts.call_arg<0>(),
            port_message_counts);

    ASSERT_TRUE(snapshot_manager2.resuming_from_intermediate());
    ASSERT_FALSE(snapshot_manager2.resuming_from_final());

    auto msg = snapshot_manager2.load_snapshot();
    ASSERT_DOUBLE_EQ(msg.timestamp(), 0.2);
    ASSERT_FALSE(msg.has_next_timestamp());
    ASSERT_EQ(msg.data().as<std::string>(), "test data");

    snapshot_manager2.save_snapshot(
            Message(0.6, "test data2"), true, {"test"}, 42.2, 1.2, {});

    ASSERT_TRUE(mock_mmp_client_.submit_snapshot_metadata.called());
    auto const & metadata2 = mock_mmp_client_.submit_snapshot_metadata.call_arg<0>();
    ASSERT_EQ(metadata2.triggers, std::vector<std::string>({"test"}));
    ASSERT_EQ(metadata2.wallclock_time, 42.2);
    ASSERT_EQ(metadata2.timestamp, 0.6);
    ASSERT_FALSE(metadata2.next_timestamp.is_set());
    ASSERT_EQ(metadata2.port_message_counts, port_message_counts);
    ASSERT_TRUE(metadata2.is_final_snapshot);
    snapshot_path = metadata2.snapshot_filename;
    ASSERT_EQ(snapshot_path, temp_dir_ + "/test-1_3.pack");
}

TEST_F(libmuscle_snapshot_manager, test_save_load_implicit_snapshot) {
    mock_port_manager_.list_ports.return_value = PortsDescription(
            {{Operator::S, {"in"}}, {Operator::O_I, {"out"}}});
    PortMessageCounts port_message_counts = {
            {"in", {1}},
            {"out", {2}},
            {"muscle_settings_in", {0}}};
    mock_port_manager_.get_message_counts.return_value = port_message_counts;
    mock_port_manager_.settings_in_connected.return_value = false;
    Reference instance_id("test[1]");

    SnapshotManager snapshot_manager(
            instance_id, mock_mmp_client_, mock_port_manager_, mock_logger_);

    snapshot_manager.prepare_resume({}, temp_dir_);
    ASSERT_FALSE(snapshot_manager.resuming_from_intermediate());
    ASSERT_FALSE(snapshot_manager.resuming_from_final());

    // save implicit snapshot, i.e. Message=not set
    snapshot_manager.save_snapshot({}, true, {"implicit"}, 1.0, 1.5, {});

    ASSERT_TRUE(mock_mmp_client_.submit_snapshot_metadata.called());
    auto const & metadata = mock_mmp_client_.submit_snapshot_metadata.call_arg<0>();
    std::string snapshot_path = metadata.snapshot_filename;
    mock_mmp_client_.submit_snapshot_metadata.call_args_list.clear();

    SnapshotManager snapshot_manager2(
            instance_id, mock_mmp_client_, mock_port_manager_, mock_logger_);

    snapshot_manager2.prepare_resume(snapshot_path, temp_dir_);
    ASSERT_TRUE(mock_port_manager_.restore_message_counts.called_once());
    ASSERT_EQ(
            mock_port_manager_.restore_message_counts.call_arg<0>(),
            port_message_counts);
    ASSERT_TRUE(mock_mmp_client_.submit_snapshot_metadata.called_once());
    mock_mmp_client_.submit_snapshot_metadata.call_args_list.clear();

    ASSERT_FALSE(snapshot_manager2.resuming_from_intermediate());
    ASSERT_FALSE(snapshot_manager2.resuming_from_final());
    snapshot_manager2.save_snapshot({}, true, {"implicit"}, 12.3, 2.5, {});
    ASSERT_TRUE(mock_mmp_client_.submit_snapshot_metadata.called_once());
}

