#include <libmuscle/snapshot.hpp>

#include <cmath>

#include <msgpack.hpp>

#include <libmuscle/mcp/data_pack.hpp>
#include <libmuscle/mpp_message.hpp>


namespace libmuscle { namespace _MUSCLE_IMPL_NS {

Snapshot::Snapshot(
            std::vector<std::string> const & triggers,
            double wallclock_time,
            bool is_final_snapshot,
            Optional<Message> const & message,
            ::ymmsl::Settings const & settings_overlay,
            CommunicatorState const & communicator_state
            )
        : triggers(triggers)
        , wallclock_time(wallclock_time)
        , is_final_snapshot(is_final_snapshot)
        , message(message)
        , settings_overlay(settings_overlay)
        , communicator_state(communicator_state)
    {}

Snapshot Snapshot::from_bytes(std::vector<char> const & data) {
    // decode
    auto zone = std::make_shared<msgpack::zone>();
    DataConstRef dict = mcp::unpack_data(zone, data.data(), data.size());

    // convert lists/dicts to vectors/unordered_maps
    std::vector<std::string> triggers;
    auto data_triggers = dict["triggers"];
    for (std::size_t i=0; i<data_triggers.size(); ++i) {
        triggers.push_back(data_triggers[i].as<std::string>());
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
            dict["is_final_snapshot"].as<bool>(),
            message,
            dict["settings_overlay"].as<::ymmsl::Settings>(),
            CommunicatorState::from_data(dict["communicator_state"])
            );
}

std::vector<char> Snapshot::to_bytes() const {
    Data d_triggers = Data::nils(triggers.size());
    for (std::size_t i=0; i<triggers.size(); ++i) {
        d_triggers[i] = triggers[i];
    }

    msgpack::sbuffer sbuf;
    // Note setting dict in two branches, to avoid a memcopy of the encoded MPPMessage
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
                msg.data(),
                {});

        DataConstRef dict = DataConstRef::dict(
            "triggers", d_triggers,
            "wallclock_time", wallclock_time,
            "is_final_snapshot", is_final_snapshot,
            "message", mpp_msg.encoded_as_dcr(),
            "settings_overlay", Data(settings_overlay),
            "communicator_state", communicator_state.to_data());

        msgpack::pack(sbuf, dict);

    } else {
        DataConstRef dict = DataConstRef::dict(
            "triggers", d_triggers,
            "wallclock_time", wallclock_time,
            "is_final_snapshot", is_final_snapshot,
            "message", Data(),
            "settings_overlay", Data(settings_overlay),
            "communicator_state", communicator_state.to_data());

        msgpack::pack(sbuf, dict);
    }

    std::vector<char> bytes(sbuf.size());
    memcpy(bytes.data(), sbuf.data(), sbuf.size());
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
            snapshot.communicator_state.port_message_counts,
            snapshot.is_final_snapshot,
            snapshot_filename);
}

} }
