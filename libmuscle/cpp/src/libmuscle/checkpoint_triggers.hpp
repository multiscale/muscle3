#pragma once

#ifdef LIBMUSCLE_MOCK_TRIGGER_MANAGER
#include LIBMUSCLE_MOCK_TRIGGER_MANAGER
#else

#include <libmuscle/data.hpp>
#include <libmuscle/namespace.hpp>
#include <libmuscle/util.hpp>

#include <chrono>
#include <memory>
#include <string>
#include <vector>

namespace libmuscle { namespace _MUSCLE_IMPL_NS {

/** Represents a trigger for creating snapshots
 */
class CheckpointTrigger {
    public:
        virtual ~CheckpointTrigger() = default;

        /** Calculate the next checkpoint time
         *
         * @param cur_time The current time.
         * @return Optional<double> The time when a next checkpoint should be taken, or
         *      nil if this trigger has no checkpoint after cur_time.
         */
        virtual Optional<double> next_checkpoint(double cur_time) = 0;

        /** Calculate the previous checkpoint time
         *
         * @param cur_time The current time.
         * @return Optional<double> The time when a previous checkpoint should have been
         *      taken, or nil if this trigger has no checkpoint after cur_time.
         */
        virtual Optional<double> previous_checkpoint(double cur_time) = 0;
};

/** Represents a trigger based on an "at" checkpoint rule
 *
 * This triggers at the specified times.
 */
class AtCheckpointTrigger : public CheckpointTrigger {
    public:
        /** Create an "at" checkpoint trigger
         *
         * @param at List of checkpoint moments
         */
        explicit AtCheckpointTrigger(std::vector<double> & at);

        Optional<double> next_checkpoint(double cur_time) override;
        Optional<double> previous_checkpoint(double cur_time) override;

    private:
        std::vector<double> at_;
};

/** Represents a trigger based on a "ranges" checkpoint rule
 *
 * This triggers at a range of checkpoint moments.
 *
 * Equivalent an "at" rule ``[start, start + step, start + 2*step, ...]`` for
 * as long as ``start + i*step <= stop``.
 *
 * Stop may be omitted, in which case the range is infinite.
 *
 * Start may be omitted, in which case the range is equivalent to an "at" rule
 * ``[..., -n*step, ..., -step, 0, step, 2*step, ...]`` for as long as
 * ``i*step <= stop``.
 */
class RangeCheckpointTrigger : public CheckpointTrigger {
    public:
        /** Create a "range" checkpoint trigger
         *
         * @param encoded_range_rules YMMSL CheckpointRangeRule encoded in a
         *      DataConstRef.
         */
        explicit RangeCheckpointTrigger(DataConstRef const & encoded_range_rule);

        Optional<double> next_checkpoint(double cur_time) override;
        Optional<double> previous_checkpoint(double cur_time) override;

    private:
        Optional<double> start_;
        Optional<double> stop_;
        double every_;
        Optional<double> last_;
};

/** Checkpoint trigger based on a combination of "at" and "ranges"
 */
class CombinedCheckpointTriggers : public CheckpointTrigger {
    public:
        /** Create an "at" checkpoint trigger
         *
         * @param encoded_checkpoint_rules List of YMMSL CheckpointRule encoded in a
         *      DataConstRef.
         */
        explicit CombinedCheckpointTriggers(DataConstRef const & encoded_checkpoint_rules);

        Optional<double> next_checkpoint(double cur_time) override;
        Optional<double> previous_checkpoint(double cur_time) override;

        bool has_rules() const;
    private:
        std::vector<std::unique_ptr<CheckpointTrigger>> triggers_;
};

/** Manages all checkpoint triggers and checks if a snapshot must be saved.
 */
class TriggerManager {
    public:
        TriggerManager();

        /** Register checkpoint info received from the muscle manager.
         */
        void set_checkpoint_info(
                double elapsed, DataConstRef const & encoded_checkpoints);

        /** Returns elapsed wallclock_time in seconds.
         */
        double elapsed_walltime();

        /** Return elapsed time of last should_save*
         */
        double checkpoints_considered_until();

        /** Returns whether checkpoints are defined
         */
        bool has_checkpoints() const { return has_checkpoints_; }

        /** Ensure our elapsed time is at least the given value
         */
        void harmonise_wall_time(double at_least);

        /** Handles instance.should_save_snapshot
         */
        bool should_save_snapshot(double timestamp);

        /** Handles instance.should_save_final_snapshot
         */
        bool should_save_final_snapshot(
                bool do_reuse, Optional<double> f_init_max_timestamp);

        /** Update last and next checkpoint times when a snapshot is made.
         *
         * @param timestamp timestamp as reported by the instance (or from incoming
         *      F_INIT messages for save_final_snapshot).
         */
        void update_checkpoints(double timestamp);

        /** Get trigger description(s) for the current reason for checkpointing.
         */
        std::vector<std::string> get_triggers();

    private:
        bool has_checkpoints_;
        std::vector<std::string> last_triggers_;
        double cpts_considered_until_;
        std::chrono::time_point<std::chrono::steady_clock> simulation_epoch_;
        bool checkpoint_at_end_;
        CombinedCheckpointTriggers wall_;
        double prevwall_;
        Optional<double> nextwall_;
        CombinedCheckpointTriggers sim_;
        Optional<double> prevsim_;
        Optional<double> nextsim_;

        bool should_save_(double simulation_time);
};

} }

#endif

