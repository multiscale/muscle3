#include <libmuscle/snapshot_manager.hpp>

#include <libmuscle/data.hpp>

#include <algorithm>
#include <cmath>
#include <fstream>
#include <sstream>

// Note: using POSIX for filesystem calls
// Could be upgraded to std::filesystem when targeting C++17 or later
#include <errno.h>
#include <fcntl.h>
#include <limits.h>
#include <string.h>
#include <unistd.h>

#define MAX_FILE_EXISTS_CHECK 10000

using namespace std::string_literals;

namespace libmuscle { namespace _MUSCLE_IMPL_NS {

SnapshotManager::SnapshotManager(
            ymmsl::Reference const & instance_id,
            MMPClient & manager,
            PortManager & port_manager,
            Logger & logger)
        : instance_id_(instance_id)
        , manager_(manager)
        , port_manager_(port_manager)
        , logger_(logger)
        , resume_from_snapshot_()
        , resume_overlay_()
        , next_snapshot_num_(1)
        , snapshot_directory_()
{
    // replace identifier[i] by identifier-i to use in snapshot file name
    // using a dash (-) because that is not allowed in Identifiers
    safe_id_ = static_cast<std::string>(instance_id_);
    std::replace(safe_id_.begin(), safe_id_.end(), '[', '-');
    safe_id_.erase(
            std::remove(safe_id_.begin(), safe_id_.end(), ']'),
            safe_id_.end());
}

namespace {

std::string string_error(int err_num) {
    char err_buf[1024];
#ifdef _GNU_SOURCE
    // g++ defines this by default, which uses the gnu extension for strerror_r
    return strerror_r(err_num, err_buf, 1024);
#else  // _GNU_SOURCE
    // POSIX complient strerror_r
    if (strerror_r(err_num, err_buf, 1024) == 0)
        return err_buf;
    return std::to_string(err_num);
#endif  // _GNU_SOURCE
}

// Adapted from https://stackoverflow.com/a/2203853
std::string get_working_path()
{
    char temp [ PATH_MAX ];

    if ( getcwd(temp, PATH_MAX) != 0)
        return std::string ( temp );

    throw std::runtime_error(
            "Error retrieving current working directory: " + string_error(errno));
}

}

Optional<double> SnapshotManager::prepare_resume(
        Optional<std::string> const & resume_snapshot,
        Optional<std::string> const & snapshot_directory) {
    Optional<double> result;

    if (snapshot_directory.is_set()) {
        snapshot_directory_ = snapshot_directory.get();
    } else {
        // store snapshots in current working directory
        snapshot_directory_ = get_working_path();
    }

    if (resume_snapshot.is_set()) {
        auto snapshot = load_snapshot_from_file(resume_snapshot.get());

        if (snapshot.message.is_set()) {
            // snapshot.message is not set for implicit snapshots
            resume_from_snapshot_ = snapshot;
            result = snapshot.message.get().timestamp();
        }
        resume_overlay_ = snapshot.settings_overlay;

        port_manager_.restore_message_counts(snapshot.port_message_counts);
        // Store a copy of the snapshot in the current run directory
        auto path = store_snapshot_(snapshot);
        auto metadata = SnapshotMetadata::from_snapshot(snapshot, path);
        manager_.submit_snapshot_metadata(metadata);
    }

    return result;
}

bool SnapshotManager::resuming_from_intermediate() {
    return (resume_from_snapshot_.is_set() &&
            !resume_from_snapshot_.get().is_final_snapshot);
}

bool SnapshotManager::resuming_from_final() {
    return (resume_from_snapshot_.is_set() &&
            resume_from_snapshot_.get().is_final_snapshot);
}

Message SnapshotManager::load_snapshot() {
    if (!resume_from_snapshot_.is_set())
        throw std::runtime_error("Error: no snapshot to load.");
    return resume_from_snapshot_.get().message.get();
}

double SnapshotManager::save_snapshot(
        Optional<Message> message, bool is_final,
        std::vector<std::string> const & triggers, double wallclock_time,
        Optional<double> f_init_max_timestamp,
        ::ymmsl::Settings settings_overlay) {
    auto port_message_counts = port_manager_.get_message_counts();

    if (is_final) {
        // Decrease F_INIT port counts by one: F_INIT messages are already
        // pre-received, but not yet processed by the user code. Therefore,
        // the snapshot state should treat these as not-received.
        auto all_ports = port_manager_.list_ports();
        auto ports = all_ports.find(::ymmsl::Operator::F_INIT);
        if (ports != all_ports.end()) {
            for (auto const & port_name : ports->second) {
                for (auto & count : port_message_counts[port_name]) {
                    --count;
                }
            }
        }
        if (port_manager_.settings_in_connected()) {
            for (auto & count : port_message_counts["muscle_settings_in"]) {
                --count;
            }
        }
    }

    Snapshot snapshot(
            triggers, wallclock_time, port_message_counts, is_final, message,
            settings_overlay);

    auto path = store_snapshot_(snapshot);
    auto metadata = SnapshotMetadata::from_snapshot(snapshot, path);
    manager_.submit_snapshot_metadata(metadata);

    double timestamp = message.is_set() ? message.get().timestamp() : -INFINITY;
    if (is_final && f_init_max_timestamp.is_set()) {
        // For final snapshots f_init_max_snapshot is the reference time (see
        // should_save_final_snapshot).
        timestamp = f_init_max_timestamp.get();
    }
    return timestamp;
}

Snapshot SnapshotManager::load_snapshot_from_file(
        std::string const & snapshot_location) {
    logger_.debug("Loading snapshot from " + snapshot_location);

    std::ifstream snapshot_file(snapshot_location, std::ios::binary);
    if (!snapshot_file.good()) {
        throw std::runtime_error(
                "Unable to load snapshot: " + snapshot_location +
                " cannot be opened. Please ensure this path exists and can be read.");
    }

    // get the size of the file
    snapshot_file.seekg(0, std::ios::end);
    std::size_t fsize = snapshot_file.tellg();
    snapshot_file.seekg(0, std::ios::beg);

    if (fsize < 1) {
        throw std::runtime_error(
                "Unable to load snapshot: " + snapshot_location + " is an empty file.");
    }

    char version;
    std::vector<char> data(fsize - 1);
    snapshot_file.read(&version, 1);
    snapshot_file.read(data.data(), fsize - 1);
    if (!snapshot_file.good()) {
        throw std::runtime_error(
                "Unable to load snapshot file " + snapshot_location +
                ". I/O error while reading file.");
    }

    switch (static_cast<Snapshot::VersionByte>(version)) {
        case Snapshot::VersionByte::MESSAGEPACK:
            return Snapshot::from_bytes(data);
        default:
            throw std::runtime_error(
                    "Unable to load snapshot file " + snapshot_location +
                    ": unknown version of snapshot file. Was the file saved with a"
                    " different version of libmuscle or edited?");
    }
}

std::string SnapshotManager::store_snapshot_(Snapshot const & snapshot) {
    logger_.debug("Saving snapshot to " + snapshot_directory_);
    std::ofstream snapshot_file;
    std::string fpath;
    for (int i=0; i<MAX_FILE_EXISTS_CHECK; ++i) {
        // Expectation is that muscle_snapshot_directory is empty initially
        // and we succeed in the first loop. Still wrapping in a for-loop
        // such that an existing filename doesn't immediately raise an error
        std::ostringstream fname;
        fname << snapshot_directory_ << "/";
        fname << safe_id_ << "_" << next_snapshot_num_ << ".pack";
        fpath = fname.str();
        ++next_snapshot_num_;

        // TODO: use std::ios::noreplace (from C++23) in fstream.open instead of this
        int fd = ::open(fpath.c_str(), O_WRONLY | O_CREAT | O_EXCL, 0777);
        if (fd < 0) {
            if (errno == EEXIST)
                continue;  // file already exists: retry next available
            throw std::runtime_error(string_error(errno));
        }
        ::close(fd);

        snapshot_file.open(fpath, std::ios::binary);
        if (snapshot_file.good()) {
            break;
        } else {
            snapshot_file.close();
        }
    }
    if (!snapshot_file.good()) {
        throw std::runtime_error(
                "Could not find an available filename for storing the next"
                " snapshot: " + fpath + " cannot be opened for writing.");
    }
    snapshot_file << static_cast<char>(Snapshot::VersionByte::MESSAGEPACK);
    auto data = snapshot.to_bytes();
    snapshot_file.write(data.data(), data.size());
    snapshot_file.close();
    if (!snapshot_file.good()) {
        throw std::runtime_error("I/O error while writing snapshot to file " + fpath);
    }
    return fpath;
}

} }
