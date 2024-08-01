#pragma once

#include <unordered_map>
#include <string>
#include <vector>

#include <libmuscle/message.hpp>
#include <libmuscle/namespace.hpp>
#include <libmuscle/util.hpp>

#include <ymmsl/ymmsl.hpp>

namespace libmuscle { namespace _MUSCLE_IMPL_NS {

/** Snapshot data structure.
 */
class Snapshot {
    public:
        enum class VersionByte : char {
            MESSAGEPACK = '1'
        };

        Snapshot(
                std::vector<std::string> const & triggers,
                double wallclock_time,
                std::unordered_map<std::string, std::vector<int>> const & port_message_counts,
                bool is_final_snapshot,
                Optional<Message> const & message,
                ::ymmsl::Settings const & settings_overlay);

        /** Create a snapshot object from binary data.
         *
         * @param data binary data representing the snapshot. Note that this must
         *      exclude the versioning byte.
         */
        static Snapshot from_bytes(std::vector<char> const & data);

        /** Convert the snapshot object to binary data.
         *
         * @return Binary data representing the snapshot. Note that this excludes
         *      the versioning byte.
         */
        std::vector<char> to_bytes() const;

        std::vector<std::string> triggers;
        double wallclock_time;
        std::unordered_map<std::string, std::vector<int>> port_message_counts;
        bool is_final_snapshot;
        Optional<Message> message;
        ::ymmsl::Settings settings_overlay;
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

        std::vector<std::string> triggers;
        double wallclock_time;
        double timestamp;
        Optional<double> next_timestamp;
        std::unordered_map<std::string, std::vector<int>> port_message_counts;
        bool is_final_snapshot;
        std::string snapshot_filename;
};

} }
