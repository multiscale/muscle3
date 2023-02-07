#pragma once

#include <unordered_map>
#include <string>
#include <vector>

#include <libmuscle/data.hpp>
#include <libmuscle/message.hpp>
#include <libmuscle/util.hpp>

#include <ymmsl/ymmsl.hpp>

namespace libmuscle { namespace impl {

/** Snapshot data structure.
 */
class Snapshot {
    public:
        enum class VersionByte : char {
            MESSAGEPACK = '1'
        };

        Snapshot(
                std::vector<std::string> triggers,
                double wallclock_time,
                std::unordered_map<std::string, std::vector<int>> port_message_counts,
                bool is_final_snapshot,
                Optional<Message> message,
                ::ymmsl::Settings settings_overlay);

        /** Create a snapshot object from binary data.
         *
         * @param data binary data representing the snapshot. Note that this must
         *      exclude the versioning byte.
         */
        static Snapshot from_bytes(DataConstRef const & data);

        /** Convert the snapshot object to binary data.
         *
         * @return DataConstRef Binary data representing the snapshot. Note that this
         *      excludes the versioning byte.
         */
        DataConstRef to_bytes() const;

        std::vector<std::string> triggers_;
        double wallclock_time_;
        std::unordered_map<std::string, std::vector<int>> port_message_counts_;
        bool is_final_snapshot_;
        Optional<Message> message_;
        ::ymmsl::Settings settings_overlay_;
};

/** Metadata of a snapshot for sending to the muscle_manager.
 */
class SnapshotMetadata {
    public:
        SnapshotMetadata(
                std::vector<std::string> const & triggers,
                double wallclock_time,
                double timestamp,
                Optional<double> next_timestamp,
                std::unordered_map<std::string, std::vector<int>> const & port_message_counts,
                bool is_final_snapshot,
                std::string const & snapshot_filename);

        /** Create snapshot metadata from the given snapshot and filename
         */
        static SnapshotMetadata from_snapshot(
                Snapshot const & snapshot, std::string const & snapshot_filename);

        std::vector<std::string> triggers_;
        double wallclock_time_;
        double timestamp_;
        Optional<double> next_timestamp_;
        std::unordered_map<std::string, std::vector<int>> port_message_counts_;
        bool is_final_snapshot_;
        std::string snapshot_filename_;
};

} }
