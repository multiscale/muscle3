#include <libmuscle/api_guard.hpp>

#include <sstream>

namespace libmuscle { namespace _MUSCLE_IMPL_NS {

APIGuard::APIGuard(bool uses_checkpointing, bool is_root)
        : phase_(APIPhase::BEFORE_FIRST_REUSE_INSTANCE),
          uses_checkpointing_(uses_checkpointing),
          is_root_(is_root)
{}

void APIGuard::verify_reuse_instance() {
    if (phase_ != APIPhase::BEFORE_REUSE_INSTANCE
            && phase_ != APIPhase::BEFORE_FIRST_REUSE_INSTANCE) {
        throw std::runtime_error(
                "We reached the end of the reuse loop without checking"
                " if a snapshot should be saved. Please add at least"
                " a should_save_final_snapshot and save_final_snapshot.");
    }
}

void APIGuard::reuse_instance_done(bool reusing) {
    if (!reusing) {
        phase_ = APIPhase::AFTER_REUSE_LOOP;
    } else {
        if (uses_checkpointing_) {
            phase_ = APIPhase::BEFORE_RESUMING;
        } else {
            phase_ = APIPhase::BEFORE_REUSE_INSTANCE;
        }
    }
}

void APIGuard::verify_resuming() {
    if (!uses_checkpointing_) {
        throw std::runtime_error(
                "Please add the flag"
                " InstanceFlag::USES_CHECKPOINT_API to your"
                " instance to use the MUSCLE3 checkpointing API.");
    }
    if (phase_ != APIPhase::BEFORE_RESUMING) {
        throw std::runtime_error(
                "Please call resuming() only as the first thing in the"
                " reuse loop.");
    }
}

void APIGuard::resuming_done(bool resuming) {
    if (resuming && is_root_) {
        phase_ = APIPhase::BEFORE_LOAD_SNAPSHOT;
    } else {
        phase_ = APIPhase::BEFORE_SHOULD_INIT;
    }
}

void APIGuard::verify_load_snapshot() {
    if (!is_root_)
        throw std::runtime_error(
                "load_snapshot may only be called from the root process");
    if (phase_ != APIPhase::BEFORE_LOAD_SNAPSHOT) {
        throw std::runtime_error(
            "Please check that we are resuming by calling resuming()"
            " before calling load_snapshot()");
    }
}

void APIGuard::load_snapshot_done() {
    phase_ = APIPhase::BEFORE_SHOULD_INIT;
}

void APIGuard::verify_should_init() {
    if (phase_ != APIPhase::BEFORE_SHOULD_INIT) {
        throw std::runtime_error(
                "Please check whether to run f_init using should_init()"
                " after resuming, and before trying to save a snapshot.");
    }
}

void APIGuard::should_init_done() {
    phase_ = APIPhase::BEFORE_SHOULD_SAVE_SNAPSHOT;
}

void APIGuard::verify_should_save_snapshot() {
    if (phase_ != APIPhase::BEFORE_SHOULD_SAVE_SNAPSHOT) {
        generic_error_messages_("should_save_snapshot");
        throw std::runtime_error("Should be unreachable.");
    }
}

void APIGuard::should_save_snapshot_done(bool should_save) {
    if (should_save && is_root_) {
        phase_ = APIPhase::BEFORE_SAVE_SNAPSHOT;
    }
}

void APIGuard::verify_save_snapshot() {
    if (!is_root_)
        throw std::runtime_error(
                "save_snapshot may only be called from the root process");
    if (phase_ != APIPhase::BEFORE_SAVE_SNAPSHOT) {
        generic_error_messages_("save_snapshot");
        throw std::runtime_error("Should be unreachable.");
    }
}

void APIGuard::save_snapshot_done() {
    phase_ = APIPhase::BEFORE_SHOULD_SAVE_SNAPSHOT;
}

void APIGuard::verify_should_save_final_snapshot() {
    if (phase_ != APIPhase::BEFORE_SHOULD_SAVE_SNAPSHOT) {
        generic_error_messages_("should_save_final_snapshot");
        throw std::runtime_error("Should be unreachable.");
    }
}

void APIGuard::should_save_final_snapshot_done(bool should_save) {
    if (should_save && is_root_) {
        phase_ = APIPhase::BEFORE_SAVE_FINAL_SNAPSHOT;
    } else {
        phase_ = APIPhase::BEFORE_REUSE_INSTANCE;
    }
}

void APIGuard::verify_save_final_snapshot() {
    if (!is_root_)
        throw std::runtime_error(
                "save_final_snapshot may only be called from the root process");
    if (phase_ != APIPhase::BEFORE_SAVE_FINAL_SNAPSHOT) {
        generic_error_messages_("save_final_snapshot");
        throw std::runtime_error("Should be unreachable.");
    }
}

void APIGuard::save_final_snapshot_done() {
    phase_ = APIPhase::BEFORE_REUSE_INSTANCE;
}

void APIGuard::generic_error_messages_(std::string const & verify_phase) {
    std::ostringstream oss;
    switch (phase_) {
        case APIPhase::BEFORE_FIRST_REUSE_INSTANCE:
        case APIPhase::AFTER_REUSE_LOOP:
            oss << "Please only call " << verify_phase << " inside the reuse loop.";
            break;
        case APIPhase::BEFORE_REUSE_INSTANCE:
            oss << "Please do not call " << verify_phase << " after";
            oss << " should_save_final_snapshot. should_save_final_snapshot";
            oss << " should be at the end of the reuse loop.";
            break;
        case APIPhase::BEFORE_RESUMING:
            oss << "Inside the reuse loop you must call resuming first.";
            break;
        case APIPhase::BEFORE_LOAD_SNAPSHOT:
            oss << "If resuming returns True, then you must call load_snapshot first.";
            break;
        case APIPhase::BEFORE_SHOULD_INIT:
            oss << "After calling resuming, you must call should_init first.";
            break;
        case APIPhase::BEFORE_SHOULD_SAVE_SNAPSHOT:
            oss << "You must call save_snapshot or save_final_snapshot first.";
            break;
        case APIPhase::BEFORE_SAVE_SNAPSHOT:
            oss << "If should_save_snapshot returns True, then you must";
            oss << " call save_snapshot first.";
            break;
        case APIPhase::BEFORE_SAVE_FINAL_SNAPSHOT:
            oss << "If should_save_final_snapshot returns True, then you";
            oss << " must call save_final_snapshot first.";
            break;
        default:
            return;
    }
    throw std::runtime_error(oss.str());
}

} }
