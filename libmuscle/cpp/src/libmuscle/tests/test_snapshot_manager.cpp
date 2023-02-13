// Inject mocks
#define LIBMUSCLE_MOCK_COMMUNICATOR <mocks/mock_communicator.hpp>
#define LIBMUSCLE_MOCK_LOGGER <mocks/mock_logger.hpp>
#define LIBMUSCLE_MOCK_MMP_CLIENT <mocks/mock_mmp_client.hpp>
#define LIBMUSCLE_MOCK_PROFILER <mocks/mock_profiler.hpp>

// into the real implementation,
#include <ymmsl/ymmsl.hpp>

#include <libmuscle/close_port.cpp>
#include <libmuscle/data.cpp>
#include <libmuscle/instance.cpp>
#include <libmuscle/logging.cpp>
#include <libmuscle/mcp/data_pack.cpp>
#include <libmuscle/message.cpp>
#include <libmuscle/port.cpp>
#include <libmuscle/settings_manager.cpp>
#include <libmuscle/snapshot_manager.cpp>
#include <libmuscle/timestamp.cpp>

// then add mock implementations as needed.
#include <mocks/mock_communicator.cpp>
#include <mocks/mock_logger.cpp>
#include <mocks/mock_mmp_client.cpp>
#include <mocks/mock_profiler.cpp>

// Test code dependencies
#include <cstdio>
#include <iostream>
#include <memory>
#include <stdexcept>
#include <typeinfo>

#include <gtest/gtest.h>
#include <libmuscle/snapshot_manager.hpp>

// Note: using POSIX for filesystem calls
// Could be upgraded to std::filesystem when targeting C++17 or later
#include <unistd.h>
#include <ftw.h>

using libmuscle::impl::Data;
using libmuscle::impl::Message;
using libmuscle::impl::MockCommunicator;
using libmuscle::impl::MockLogger;
using libmuscle::impl::MockMMPClient;
using libmuscle::impl::MockProfiler;
using libmuscle::impl::Optional;
using libmuscle::impl::Snapshot;
using libmuscle::impl::SnapshotMetadata;
using libmuscle::impl::SnapshotManager;
using ymmsl::Reference;

int main(int argc, char *argv[]) {
    ::testing::InitGoogleTest(&argc, argv);
    return RUN_ALL_TESTS();
}

/* Mocks have internal state, which needs to be reset before each test. This
 * means that the tests are not reentrant, and cannot be run in parallel.
 * It's all fast enough, so that's not a problem.
 */
void reset_mocks() {
    MockCommunicator::reset();
    MockMMPClient::reset();
}

MockLogger & mock_logger() {
    static MockLogger logger;
    return logger;
}

MockProfiler & mock_profiler() {
    static MockProfiler profiler;
    return profiler;
}

class libmuscle_snapshot_manager : public ::testing::Test {
    protected:
        void SetUp() override {
            auto tmpnam = std::tmpnam(nullptr);
            temp_dir_ = std::string(tmpnam);
            if (mkdir(tmpnam, 0777) < 0)
                throw std::runtime_error(strerror(errno));
            std::cerr << "DEBUG: using temp dir " << temp_dir_ << std::endl;
        }

        void TearDown() override {
            // simulate rm -rf `temp_dir_` using a file-tree-walk
            if (nftw(temp_dir_.c_str(),
                     [](const char *fpath, const struct stat *sb,
                            int tflag, struct FTW *ftwbuf)->int{
                        if (tflag == FTW_DP) {
                            std::cerr << "DEBUG: removing dir " << fpath << std::endl;
                            return rmdir(fpath);
                        }
                        if (tflag == FTW_F) {
                            std::cerr << "DEBUG: removing file " << fpath << std::endl;
                            return unlink(fpath);
                        }
                        std::cerr << "DEBUG: unknown file type " << fpath << std::endl;
                        return -1;
                     },
                     3,
                     FTW_DEPTH) < 0) {
                throw std::runtime_error(strerror(errno));
            }
            temp_dir_.clear();
        }

        std::string temp_dir_;
};

TEST_F(libmuscle_snapshot_manager, test_no_checkpointing) {
    reset_mocks();

    MockCommunicator communicator("test", {}, {}, mock_logger(), mock_profiler());
    MockMMPClient manager("instance", "");
    SnapshotManager snapshot_manager("test", manager, communicator, mock_logger());

    snapshot_manager.prepare_resume({}, temp_dir_);
    ASSERT_FALSE(snapshot_manager.resuming_from_intermediate());
    ASSERT_FALSE(snapshot_manager.resuming_from_final());
}

TEST_F(libmuscle_snapshot_manager, test_save_load_snapshot) {
    reset_mocks();

    MockCommunicator communicator("test", {}, {}, mock_logger(), mock_profiler());
    MockMMPClient manager("instance", "");
    Reference instance_id("test[1]");

    SnapshotManager snapshot_manager(instance_id, manager, communicator, mock_logger());

    snapshot_manager.prepare_resume({}, temp_dir_);
    ASSERT_FALSE(snapshot_manager.resuming_from_intermediate());
    ASSERT_FALSE(snapshot_manager.resuming_from_final());

    snapshot_manager.save_snapshot(
            Message(0.2, "test data"), false, {"test"}, 13.0, {}, {});

    // TODO: need to implement this on the mocks
    // communicator.get_message_counts.assert_called_with()
    // manager.submit_snapshot_metadata.assert_called()
    // instance, metadata = manager.submit_snapshot_metadata.call_args[0]
    // assert instance == instance_id
    // assert isinstance(metadata, SnapshotMetadata)
    // assert metadata.triggers == ['test']
    // assert metadata.wallclock_time == 13.0
    // assert metadata.timestamp == 0.2
    // assert metadata.next_timestamp is None
    // assert metadata.port_message_counts == port_message_counts
    // ASSERT_FALSE(metadata.is_final_snapshot);
    // snapshot_path = Path(metadata.snapshot_filename)
    // assert snapshot_path.parent == tmp_path
    // assert snapshot_path.name == 'test-1_1.pack'

    // TODO: get from snapshot metadata instead of hardcoding
    std::string snapshot_path = temp_dir_ + "/test-1_1.pack";

    SnapshotManager snapshot_manager2(
            instance_id, manager, communicator, mock_logger());
    snapshot_manager2.prepare_resume(snapshot_path, temp_dir_);

    ASSERT_TRUE(snapshot_manager2.resuming_from_intermediate());
    ASSERT_FALSE(snapshot_manager2.resuming_from_final());

    auto msg = snapshot_manager2.load_snapshot();
    ASSERT_DOUBLE_EQ(msg.timestamp(), 0.2);
    ASSERT_FALSE(msg.has_next_timestamp());
    ASSERT_EQ(msg.data().as<std::string>(), "test data");

    snapshot_manager2.save_snapshot(
            Message(0.6, "test data2"), true, {"test"}, 42.2, 1.2, {});

    // TODO: need to implement this on the mocks
    // instance, metadata = manager.submit_snapshot_metadata.call_args[0]
    // assert instance == instance_id
    // assert isinstance(metadata, SnapshotMetadata)
    // assert metadata.triggers == ['test']
    // assert metadata.wallclock_time == 42.2
    // assert metadata.timestamp == 0.6
    // assert metadata.next_timestamp is None
    // assert metadata.port_message_counts == port_message_counts
    // assert metadata.is_final_snapshot
    // snapshot_path = Path(metadata.snapshot_filename)
    // assert snapshot_path.parent == tmp_path
    // assert snapshot_path.name == 'test-1_3.pack'

    ASSERT_TRUE(snapshot_manager2.resuming_from_intermediate());
    ASSERT_FALSE(snapshot_manager2.resuming_from_final());
    snapshot_manager2.load_snapshot();
    ASSERT_TRUE(snapshot_manager2.resuming_from_intermediate());
    ASSERT_FALSE(snapshot_manager2.resuming_from_final());
}

TEST_F(libmuscle_snapshot_manager, test_save_load_implicit_snapshot) {
    reset_mocks();

    MockCommunicator communicator("test", {}, {}, mock_logger(), mock_profiler());
    MockMMPClient manager("instance", "");
    Reference instance_id("test[1]");

    SnapshotManager snapshot_manager(instance_id, manager, communicator, mock_logger());

    snapshot_manager.prepare_resume({}, temp_dir_);
    ASSERT_FALSE(snapshot_manager.resuming_from_intermediate());
    ASSERT_FALSE(snapshot_manager.resuming_from_final());

    // save implicit snapshot, i.e. Message=not set
    snapshot_manager.save_snapshot({}, true, {"implicit"}, 1.0, 1.5, {});

    // TODO: need to implement this on the mocks
    // manager.submit_snapshot_metadata.assert_called_once()
    // instance, metadata = manager.submit_snapshot_metadata.call_args[0]
    // assert instance == instance_id
    // assert isinstance(metadata, SnapshotMetadata)
    // snapshot_path = Path(metadata.snapshot_filename)
    // manager.submit_snapshot_metadata.reset_mock()

    // TODO: get from snapshot metadata instead of hardcoding
    std::string snapshot_path = temp_dir_ + "/test-1_1.pack";

    SnapshotManager snapshot_manager2(
            instance_id, manager, communicator, mock_logger());

    snapshot_manager2.prepare_resume(snapshot_path, temp_dir_);
    // TODO: need to implement this on the mocks
    // communicator.restore_message_counts.assert_called_with(port_message_counts)
    // manager.submit_snapshot_metadata.assert_called_once()
    // manager.submit_snapshot_metadata.reset_mock()

    ASSERT_FALSE(snapshot_manager2.resuming_from_intermediate());
    ASSERT_FALSE(snapshot_manager2.resuming_from_final());
    snapshot_manager2.save_snapshot({}, true, {"implicit"}, 12.3, 2.5, {});
    // TODO: need to implement this on the mocks
    // manager.submit_snapshot_metadata.assert_called_once()
}
