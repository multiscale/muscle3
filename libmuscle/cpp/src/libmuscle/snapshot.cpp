#include <libmuscle/snapshot.hpp>

#include <cmath>

#include <msgpack.hpp>

#include <libmuscle/mcp/data_pack.hpp>
#include <libmuscle/mpp_message.hpp>


namespace libmuscle { namespace impl {

Snapshot::Snapshot(
            std::vector<std::string> triggers,
            double wallclock_time,
            std::unordered_map<std::string, std::vector<int>> port_message_counts,
            bool is_final_snapshot,
            Optional<Message> message,
            ::ymmsl::Settings settings_overlay
            )
        : triggers_(triggers)
        , wallclock_time_(wallclock_time)
        , port_message_counts_(port_message_counts)
        , is_final_snapshot_(is_final_snapshot)
        , message_(message)
        , settings_overlay_(settings_overlay)
    {}

Snapshot Snapshot::from_bytes(DataConstRef const & data) {
    // decode
    auto zone = std::make_shared<msgpack::zone>();
    DataConstRef dict = mcp::unpack_data(zone, data.as_byte_array(), data.size());

    // convert lists/dicts to vectors/unordered_maps
    std::vector<std::string> triggers;
    auto data_triggers = dict["triggers"];
    for (std::size_t i=0; i<data_triggers.size(); ++i) {
        triggers.push_back(data_triggers[i].as<std::string>());
    }

    std::unordered_map<std::string, std::vector<int>> port_message_counts;
    auto data_pmc = dict["port_message_counts"];
    for (std::size_t i=0; i<data_pmc.size(); ++i) {
        std::vector<int> counts;
        for (std::size_t j=0; j<data_pmc.value(i).size(); ++j) {
            counts.push_back(data_pmc.value(i)[j].as<int>());
        }
        port_message_counts[data_pmc.key(i)] = counts;
    }

    Optional<Message> message;
    if (!dict["message"].is_nil()) {
        auto mpp_message = MPPMessage::from_bytes(dict["message"]);
        message = Message(mpp_message.timestamp, mpp_message.data);
        if (mpp_message.next_timestamp.is_set()) {
            message.get().set_next_timestamp(mpp_message.next_timestamp.get());
        }
        if (!mpp_message.settings_overlay.is_nil()) {
            message.get().set_settings(
                    mpp_message.settings_overlay.as<::ymmsl::Settings>());
        }
    }

    return Snapshot(
            triggers,
            dict["wallclock_time"].as<double>(),
            port_message_counts,
            dict["is_final_snapshot"].as<bool>(),
            message,
            dict["settings_overlay"].as<::ymmsl::Settings>()
            );
}

DataConstRef Snapshot::to_bytes() const {
    Data triggers = Data::nils(triggers_.size());
    for (std::size_t i=0; i<triggers_.size(); ++i) {
        triggers[i] = triggers_[i];
    }

    Data port_message_counts = Data::dict();
    for (const auto & kv : port_message_counts_) {
        Data counts = Data::nils(kv.second.size());
        for (std::size_t i=0; i<kv.second.size(); ++i) {
            counts[i] = kv.second[i];
        }
        port_message_counts[kv.first] = counts;
    }

    Data message;
    if (message_.is_set()) {
        auto msg = message_.get();
        MPPMessage mpp_msg(
                "_",
                "_",
                {},
                msg.timestamp(),
                msg.has_next_timestamp() ? msg.next_timestamp() : Optional<double>(),
                msg.has_settings() ? msg.settings() : Data(),
                0,
                -1.0,
                msg.data());
        auto encoded = mpp_msg.encoded();
        // unfortunately need to create a copy of the byte array here...
        message = Data::byte_array(encoded.size());
        memcpy(message.as_byte_array(), encoded.as_byte_array(), encoded.size());
    }

    Data dict = Data::dict(
            "triggers", triggers,
            "wallclock_time", wallclock_time_,
            "port_message_counts", port_message_counts,
            "is_final_snapshot", is_final_snapshot_,
            "message", message,
            "settings_overlay", Data(settings_overlay_)
            );

    msgpack::sbuffer sbuf;
    msgpack::pack(sbuf, dict);

    auto bytes = Data::byte_array(sbuf.size());
    memcpy(bytes.as_byte_array(), sbuf.data(), sbuf.size());

    return bytes;
}

SnapshotMetadata::SnapshotMetadata(
            std::vector<std::string> const & triggers,
            double wallclock_time,
            double timestamp,
            Optional<double> next_timestamp,
            std::unordered_map<std::string, std::vector<int>> const & port_message_counts,
            bool is_final_snapshot,
            std::string const & snapshot_filename)
        : triggers_(triggers)
        , wallclock_time_(wallclock_time)
        , timestamp_(timestamp)
        , next_timestamp_(next_timestamp)
        , port_message_counts_(port_message_counts)
        , is_final_snapshot_(is_final_snapshot)
        , snapshot_filename_(snapshot_filename)
    {}

SnapshotMetadata SnapshotMetadata::from_snapshot(
        Snapshot const & snapshot, std::string const & snapshot_filename) {
    double timestamp = NAN;
    Optional<double> next_timestamp;
    if (snapshot.message_.is_set()) {
        timestamp = snapshot.message_.get().timestamp();
        if (snapshot.message_.get().has_next_timestamp()) {
            next_timestamp = snapshot.message_.get().next_timestamp();
        }
    }
    return SnapshotMetadata(
            snapshot.triggers_,
            snapshot.wallclock_time_,
            timestamp,
            next_timestamp,
            snapshot.port_message_counts_,
            snapshot.is_final_snapshot_,
            snapshot_filename);
}

} }
