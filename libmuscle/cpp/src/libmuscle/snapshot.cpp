#include <libmuscle/snapshot.hpp>

#include <cmath>

#include <msgpack.hpp>

#include <libmuscle/mcp/data_pack.hpp>
#include <libmuscle/mpp_message.hpp>


namespace libmuscle { namespace impl {

Snapshot::Snapshot(
            std::vector<std::string> const & triggers,
            double wallclock_time,
            std::unordered_map<std::string, std::vector<int>> const & port_message_counts,
            bool is_final_snapshot,
            Optional<Message> const & message,
            ::ymmsl::Settings const & settings_overlay
            )
        : triggers(triggers)
        , wallclock_time(wallclock_time)
        , port_message_counts(port_message_counts)
        , is_final_snapshot(is_final_snapshot)
        , message(message)
        , settings_overlay(settings_overlay)
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
    Data d_triggers = Data::nils(triggers.size());
    for (std::size_t i=0; i<triggers.size(); ++i) {
        d_triggers[i] = triggers[i];
    }

    Data pmc = Data::dict();
    for (const auto & kv : port_message_counts) {
        Data counts = Data::nils(kv.second.size());
        for (std::size_t i=0; i<kv.second.size(); ++i) {
            counts[i] = kv.second[i];
        }
        pmc[kv.first] = counts;
    }

    Data dict;
    // Note setting dict in two branches, to avoid a memcopy of the encoded MMPMessage
    if (message.is_set()) {
        auto msg = message.get();
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
        // Initializing a Data::dict with a DataConstRef is allowed, but assignment
        // after creation is not
        dict = Data::dict(
            "triggers", d_triggers,
            "wallclock_time", wallclock_time,
            "port_message_counts", pmc,
            "is_final_snapshot", is_final_snapshot,
            "message", mpp_msg.encoded(),
            "settings_overlay", Data(settings_overlay));
    } else {
        dict = Data::dict(
            "triggers", d_triggers,
            "wallclock_time", wallclock_time,
            "port_message_counts", pmc,
            "is_final_snapshot", is_final_snapshot,
            "message", Data(),
            "settings_overlay", Data(settings_overlay));
    }

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
        : triggers(triggers)
        , wallclock_time(wallclock_time)
        , timestamp(timestamp)
        , next_timestamp(next_timestamp)
        , port_message_counts(port_message_counts)
        , is_final_snapshot(is_final_snapshot)
        , snapshot_filename(snapshot_filename)
    {}

SnapshotMetadata SnapshotMetadata::from_snapshot(
        Snapshot const & snapshot, std::string const & snapshot_filename) {
    double timestamp = std::numeric_limits<double>::quiet_NaN();
    Optional<double> next_timestamp;
    if (snapshot.message.is_set()) {
        timestamp = snapshot.message.get().timestamp();
        if (snapshot.message.get().has_next_timestamp()) {
            next_timestamp = snapshot.message.get().next_timestamp();
        }
    }
    return SnapshotMetadata(
            snapshot.triggers,
            snapshot.wallclock_time,
            timestamp,
            next_timestamp,
            snapshot.port_message_counts,
            snapshot.is_final_snapshot,
            snapshot_filename);
}

} }
