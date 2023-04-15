#include <libmuscle/checkpoint_triggers.hpp>

#include <algorithm>
#include <cmath>

namespace libmuscle { namespace _MUSCLE_IMPL_NS {

AtCheckpointTrigger::AtCheckpointTrigger(
        std::vector<double> & at) : at_(at) {
    std::sort(at_.begin(), at_.end());
}

Optional<double> AtCheckpointTrigger::next_checkpoint(double cur_time) {
    if (cur_time >= at_.back())
        return {};  // no future checkpoint left
    auto iter = std::upper_bound(at_.begin(), at_.end(), cur_time);
    return *iter;
}

Optional<double> AtCheckpointTrigger::previous_checkpoint(double cur_time) {
    if (cur_time < at_.front())
        return {};  // no future checkpoint left
    auto iter = std::upper_bound(at_.begin(), at_.end(), cur_time);
    return *std::prev(iter);
}

namespace {

Optional<double> parse_optional_double(
        DataConstRef const & map, std::string const & key) {
    auto value = map[key];
    if (value.is_nil())
        return {};
    return value.as<double>();
}

}

RangeCheckpointTrigger::RangeCheckpointTrigger(
        DataConstRef const & encoded_range_rule) {
    start_ = parse_optional_double(encoded_range_rule, "start");
    stop_ = parse_optional_double(encoded_range_rule, "stop");
    auto every = parse_optional_double(encoded_range_rule, "every");
    if (!every.is_set())
        throw std::runtime_error("Received a nil value for every.");
    every_ = every.get();

    if (stop_.is_set()) {
        double start = start_.is_set() ? start_.get() : 0;
        double diff = stop_.get() - start;
        last_ = start + std::floor(diff / every_) * every_;
    } else {
        last_ = {};
    }
}

Optional<double> RangeCheckpointTrigger::next_checkpoint(double cur_time) {
    if (start_.is_set() && cur_time < start_.get()) {
        return start_;
    }
    if (last_.is_set() && cur_time >= last_.get()) {
        return {};
    }
    double start = start_.is_set() ? start_.get() : 0;
    double diff = cur_time - start;
    return start + std::floor(diff / every_ + 1) * every_;
}

Optional<double> RangeCheckpointTrigger::previous_checkpoint(double cur_time) {
    if (start_.is_set() && cur_time < start_.get()) {
        return {};
    }
    if (last_.is_set() && cur_time >= last_.get()) {
        return last_;
    }
    double start = start_.is_set() ? start_.get() : 0;
    double diff = cur_time - start;
    return start + std::floor(diff / every_) * every_;
}

CombinedCheckpointTriggers::CombinedCheckpointTriggers(
        DataConstRef const & encoded_checkpoint_rules)
        : triggers_() {
    std::vector<double> at;
    for (std::size_t i=0; i<encoded_checkpoint_rules.size(); ++i) {
        auto const & rule = encoded_checkpoint_rules[i];
        if (rule.size() == 1 && rule.key(0) == "at") {
            auto const & at_list = rule["at"];
            for (std::size_t j=0; j<at_list.size(); ++j) {
                auto value = at_list[j];
                if (value.is_a<double>())
                    at.push_back(value.as<double>());
                else
                    at.push_back(value.as<int64_t>());
            }
        } else {
            triggers_.push_back(
                    std::make_unique<RangeCheckpointTrigger>(rule));
        }
    }
    if (!at.empty()) {
        triggers_.push_back(std::make_unique<AtCheckpointTrigger>(at));
    }
}

Optional<double> CombinedCheckpointTriggers::next_checkpoint(double cur_time) {
    Optional<double> retval;
    for (auto & trigger : triggers_) {
        auto checkpoint = trigger->next_checkpoint(cur_time);
        if (checkpoint.is_set()) {
            if (!retval.is_set() || retval.get() > checkpoint.get()) {
                retval = checkpoint;
            }
        }
    }
    return retval;
}

Optional<double> CombinedCheckpointTriggers::previous_checkpoint(double cur_time) {
    Optional<double> retval;
    for (auto & trigger : triggers_) {
        auto checkpoint = trigger->previous_checkpoint(cur_time);
        if (checkpoint.is_set()) {
            if (!retval.is_set() || retval.get() < checkpoint.get()) {
                retval = checkpoint;
            }
        }
    }
    return retval;
}

bool CombinedCheckpointTriggers::has_rules() const {
    return !triggers_.empty();
}

TriggerManager::TriggerManager()
        : has_checkpoints_(false)
        , last_triggers_()
        , cpts_considered_until_(-std::numeric_limits<double>::infinity())
        , simulation_epoch_()
        , checkpoint_at_end_(false)
        , wall_(Data::list())
        , prevwall_(0)
        , nextwall_(0)
        , sim_(Data::list())
        , prevsim_()
        , nextsim_()
{}

void TriggerManager::set_checkpoint_info(
        double elapsed, DataConstRef const & encoded_checkpoints) {
    auto elapsed_as_duration =
        std::chrono::duration_cast<std::chrono::steady_clock::duration>(
            std::chrono::duration<double>(elapsed));
    simulation_epoch_ = std::chrono::steady_clock::now() - elapsed_as_duration;

    checkpoint_at_end_ = encoded_checkpoints["at_end"].as<bool>();

    wall_ = CombinedCheckpointTriggers(
            encoded_checkpoints["wallclock_time"]);
    prevwall_ = 0.0;
    nextwall_ = wall_.next_checkpoint(0.0);

    sim_ = CombinedCheckpointTriggers(
            encoded_checkpoints["simulation_time"]);
    prevsim_ = {};
    nextsim_ = {};

    has_checkpoints_ = checkpoint_at_end_ || wall_.has_rules() || sim_.has_rules();
}

double TriggerManager::elapsed_walltime() {
    auto duration = std::chrono::steady_clock::now() - simulation_epoch_;
    return std::chrono::duration<double>(duration).count();
}

double TriggerManager::checkpoints_considered_until() {
    return cpts_considered_until_;
}

void TriggerManager::harmonise_wall_time(double at_least) {
    double cur = elapsed_walltime();
    if (cur < at_least) {
        auto duration = std::chrono::duration_cast<std::chrono::steady_clock::duration>(
            std::chrono::duration<double>(at_least - cur));
        simulation_epoch_ -= duration;
    }
}

bool TriggerManager::should_save_snapshot(double timestamp) {
    if (!has_checkpoints_) return false;

    return should_save_(timestamp);
}

bool TriggerManager::should_save_final_snapshot(
        bool do_reuse, Optional<double> f_init_max_timestamp) {
    if (!has_checkpoints_) return false;

    bool value = false;
    if (!do_reuse) {
        if (checkpoint_at_end_) {
            value = true;
            last_triggers_.push_back("at_end");
        }
    } else if (!f_init_max_timestamp.is_set()) {
        //  No F_INIT messages received: reuse triggered on muscle_settings_in
        // message.
        // _logger.debug('Reuse triggered by muscle_settings_in.'
        //               ' Not creating a snapshot.')
    } else {
        value = should_save_(f_init_max_timestamp.get());
    }

    return value;
}

void TriggerManager::update_checkpoints(double timestamp) {
    prevwall_ = elapsed_walltime();
    nextwall_ = wall_.next_checkpoint(prevwall_);

    prevsim_ = timestamp;
    nextsim_ = sim_.next_checkpoint(timestamp);
}

std::vector<std::string> TriggerManager::get_triggers() {
    auto triggers = last_triggers_;
    last_triggers_ = std::vector<std::string>();
    return triggers;
}

bool TriggerManager::should_save_(double simulation_time) {
    if (!nextsim_.is_set() && !prevsim_.is_set()) {
        // we cannot make assumptions about the start time of a simulation,
        // a t=-1000 could make sense if t represents years since CE
        // and we should not disallow checkpointing for negative t
        auto previous = sim_.previous_checkpoint(simulation_time);
        if (previous.is_set()) {
            // there is a checkpoint rule before the current moment, assume
            // we should have taken a snapshot back then
            nextsim_ = previous;
        } else {
            nextsim_ = sim_.next_checkpoint(simulation_time);
        }
    }

    double walltime = elapsed_walltime();
    cpts_considered_until_ = walltime;

    last_triggers_.clear();
    if (nextwall_.is_set() && walltime >= nextwall_.get()) {
        last_triggers_.push_back(std::string("wallclock_time >= ") +
                                 std::to_string(nextwall_.get()));
    }
    if (nextsim_.is_set() && simulation_time >= nextsim_.get()) {
        last_triggers_.push_back(std::string("simulation_time >= ") +
                                 std::to_string(nextsim_.get()));
    }
    return !last_triggers_.empty();
}

} }
