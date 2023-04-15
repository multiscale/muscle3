#pragma once

#include <libmuscle/namespace.hpp>

#include <stdexcept>
#include <string>

namespace libmuscle { namespace _MUSCLE_IMPL_NS {

/** Different phases that the user code traverses.
 *
 * These values describe different regions that the model code can be
 * in for the case where checkpointing is implemented. By tracking
 * the phase that the model should be in, we can detect incorrect API
 * usage.
 *
 * This does not match the yMMSL operators, as it is more
 * fine-grained and concerns checkpointing, which is not represented
 * in the SEL.
 */
enum class APIPhase {
    /** Before the first time calling reuse_instance
     */
    BEFORE_FIRST_REUSE_INSTANCE,

    /** Before calling reuse_instance
     */
    BEFORE_REUSE_INSTANCE,

    /** Between reuse_instance and resuming
     */
    BEFORE_RESUMING,

    /** Between resuming and load_snapshot
     */
    BEFORE_LOAD_SNAPSHOT,

    /** After resuming, before should_init
     */
    BEFORE_SHOULD_INIT,

    /** Between should_init and should_save*
     */
    BEFORE_SHOULD_SAVE_SNAPSHOT,

    /** Between should_save_snapshot and save_snapshot
     */
    BEFORE_SAVE_SNAPSHOT,

    /** Between should_save_final_snapshot and save_final_snapshot
     */
    BEFORE_SAVE_FINAL_SNAPSHOT,

    /** After the final call to reuse_instance()
     */
    AFTER_REUSE_LOOP
};

/** Keeps track of and checks in which phase the model is.
 *
 * The verify_* functions are called when the corresponding function
 * on Instance is called, to check that we're in the right phase. They
 * raise a RuntimeError if there's a problem. The *_done functions are
 * called to signal that the corresponding function finished
 * successfully, and that we are moving on to the next phase.
 */
class APIGuard {
    public:
        /** Create an APIGuard
         *
         * This starts the tracker in the phase BEFORE_FIRST_REUSE_INSTANCE.
         *
         * @param uses_checkpointing Whether this instance wants to use checkpointing.
         * @param is_root Whether this is the root process (relevant for MPI).
         */
        explicit APIGuard(bool uses_checkpointing, bool is_root);

        /** Check reuse_instance()
         */
        void verify_reuse_instance();

        /** Update phase on successful reuse_instance().
         *
         * @param reusing Whether we are reusing or not.
         */
        void reuse_instance_done(bool reusing);

        /** Check resuming()
         */
        void verify_resuming();

        /** Update phase on successful resuming().
         *
         * @param resuming Whether we're resuming or not.
         */
        void resuming_done(bool resuming);

        /** Check load_snapshot()
         */
        void verify_load_snapshot();

        /** Update phase on successful load_snapshot()
         */
        void load_snapshot_done();

        /** Check should_init()
         */
        void verify_should_init();

        /** Update phase on successful should_init()
         */
        void should_init_done();

        /** Check should_save_snapshot()
         */
        void verify_should_save_snapshot();

        /** Update phase on successful should_save_snapshot().
         *
         * @param should_save Whether we should save or not.
         */
        void should_save_snapshot_done(bool should_save);

        /** Check save_snapshot()
         */
        void verify_save_snapshot();

        /** Update phase on successful save_snapshot()
         */
        void save_snapshot_done();

        /** Check should_save_final_snapshot().
         */
        void verify_should_save_final_snapshot();

        /** Update phase on successful should_save_snapshot().
         *
         * @param should_save Whether we should save or not.
         */
        void should_save_final_snapshot_done(bool should_save);

        /** Check should_save_final_snapshot()
         */
        void verify_save_final_snapshot();

        /** Updates state on successful save_final_snapshot()
         */
        void save_final_snapshot_done();

    private:
        APIPhase phase_;
        bool uses_checkpointing_;
        bool is_root_;

        void generic_error_messages_(std::string const & verify_phase);
};

} }
