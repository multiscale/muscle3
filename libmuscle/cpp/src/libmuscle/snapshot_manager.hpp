#pragma once

#ifdef LIBMUSCLE_MOCK_SNAPSHOT_MANAGER
#include LIBMUSCLE_MOCK_SNAPSHOT_MANAGER
#else

#include <string>
#include <vector>

#include <libmuscle/logger.hpp>
#include <libmuscle/mmp_client.hpp>
#include <libmuscle/namespace.hpp>
#include <libmuscle/port_manager.hpp>
#include <libmuscle/snapshot.hpp>
#include <libmuscle/util.hpp>

#include <ymmsl/ymmsl.hpp>

namespace libmuscle { namespace _MUSCLE_IMPL_NS {

/** Manages information on snapshots for the Instance
 *
 * Implements the saving and loading of snapshots in the checkpointing API.
 */
class SnapshotManager {
    public:
        /** Create a new snapshot manager
         *
         * @param instance_id The id of this instance.
         * @param manager The client used to submit data to the manager.
         * @param port_manager The port manager belonging to this instance.
         */
        SnapshotManager(
                ymmsl::Reference const & instance_id,
                MMPClient & manager,
                PortManager & port_manager,
                Logger & logger);

        /** Apply checkpoint info received from the manager.
         *
         * If there is a snapshot to resume from, this loads it and does
         * any resume work that libmuscle should do, including restoring
         * message counts and storing the resumed-from snapshot again as
         * our first snapshot.
         *
         * @param resume_snapshot Snapshot to resume from (or None if not resuming)
         * @param snapshot_directory directory to save snapshots in
         * @return Optional<double> Time at which the initial snapshot was saved,
         *      if resuming.
         */
        Optional<double> prepare_resume(
                Optional<std::string> const & resume_snapshot,
                Optional<std::string> const & snapshot_directory);

        /** Get the settings overlay to be used when resuming
         */
        ::ymmsl::Settings resume_overlay() const { return resume_overlay_; }

        /** Check whether we have an intermediate snapshot.
         *
         * Doesn't say whether we should resume now, just that we were
         * given an intermediate snapshot to resume from by the manager.
         */
        bool resuming_from_intermediate();

        /** Check whether we have a final snapshot.
         *
         * Doesn't say whether we should resume now, just that we were
         * given an intermediate snapshot to resume from by the manager.
         */
        bool resuming_from_final();

        /** Get the Message to resume from.
         */
        Message load_snapshot();

        /** Save a (final) snapshot.
         *
         * @param message Message object representing the snapshot.
         * @param final True iff called from save_final_snapshot.
         * @param triggers Description of checkpoints that triggered this.
         * @param wallclock_time Wallclock time when saving.
         * @param f_init_max_timestamp Timestamp for final snapshots.
         * @param settings_overlay Current settings overlay.
         * @return double Simulation time at which the snapshot was made.
         */
        double save_snapshot(
                Optional<Message> message, bool is_final,
                std::vector<std::string> const & triggers, double wallclock_time,
                Optional<double> f_init_max_timestamp,
                ::ymmsl::Settings settings_overlay);

        /** Load a previously stored snapshot from the filesystem.
         *
         * @param snapshot_location path where the snapshot is stored.
         * @return Snapshot
         */
        Snapshot load_snapshot_from_file(std::string const & snapshot_location);

    private:
        ymmsl::Reference const & instance_id_;
        MMPClient & manager_;
        PortManager & port_manager_;
        Logger & logger_;
        Optional<Snapshot> resume_from_snapshot_;
        ::ymmsl::Settings resume_overlay_;
        int next_snapshot_num_;
        std::string snapshot_directory_;
        std::string safe_id_;

        /** Store a snapshot on the filesystem.
         *
         * @param snapshot Snapshot to store.
         * @return std::string Path where the snapshot is stored.
         */
        std::string store_snapshot_(Snapshot const & snapshot);
};

} }

#endif

