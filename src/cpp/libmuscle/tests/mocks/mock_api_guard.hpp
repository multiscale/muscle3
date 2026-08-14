#pragma once

namespace libmuscle { namespace _MUSCLE_IMPL_NS {

class MockAPIGuard {
    public:
        explicit MockAPIGuard(bool uses_checkpointing, bool is_root) {}

        void verify_reuse_instance() {}

        void reuse_instance_done(bool reusing) {}

        void verify_resuming() {}

        void resuming_done(bool resuming) {}

        void verify_load_snapshot() {}

        void load_snapshot_done() {}

        void verify_should_init() {}

        void should_init_done() {}

        void verify_should_save_snapshot() {}

        void should_save_snapshot_done(bool should_save) {}

        void verify_save_snapshot() {}

        void save_snapshot_done() {}

        void verify_should_save_final_snapshot() {}

        void should_save_final_snapshot_done(bool should_save) {}

        void verify_save_final_snapshot() {}

        void save_final_snapshot_done() {}
};

using APIGuard = MockAPIGuard;

} }

