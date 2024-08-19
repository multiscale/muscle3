#include "libmuscle/mmp_client.hpp"

#include "libmuscle/data.hpp"
#include "libmuscle/mcp/data_pack.hpp"
#include "libmuscle/mcp/protocol.hpp"
#include "libmuscle/version.h"

#include <chrono>
#include <iterator>
#include <memory>
#include <random>
#include <sstream>
#include <string>
#include <thread>
#include <tuple>
#include <utility>
#include <vector>

#include <msgpack.hpp>
#include "ymmsl/ymmsl.hpp"


using libmuscle::_MUSCLE_IMPL_NS::Data;
using libmuscle::_MUSCLE_IMPL_NS::DataConstRef;
using libmuscle::_MUSCLE_IMPL_NS::mcp::unpack_data;
using libmuscle::_MUSCLE_IMPL_NS::Optional;
using libmuscle::_MUSCLE_IMPL_NS::ProfileEvent;
using libmuscle::_MUSCLE_IMPL_NS::SnapshotMetadata;
using std::chrono::steady_clock;
using ymmsl::Conduit;
using ymmsl::Reference;
using ymmsl::SettingValue;


namespace {
    const std::chrono::milliseconds peer_timeout(600000);
    const int peer_interval_min = 5000;     // milliseconds
    const int peer_interval_max = 10000;    // milliseconds

    std::chrono::milliseconds random_sleep_time() {
        static std::default_random_engine engine;
        static std::uniform_int_distribution<int> dist(
                peer_interval_min, peer_interval_max);

        return std::chrono::milliseconds(dist(engine));
    }

    Data encode_operator(ymmsl::Operator op) {
        switch (op) {
            case ymmsl::Operator::NONE:
                return Data("NONE");
            case ymmsl::Operator::F_INIT:
                return Data("F_INIT");
            case ymmsl::Operator::O_I:
                return Data("O_I");
            case ymmsl::Operator::S:
                return Data("S");
            case ymmsl::Operator::O_F:
                return Data("O_F");
        }
        // can't happen, but silence compiler warning
        throw std::runtime_error("Invalid operator");
    }

    Data encode_port(ymmsl::Port const & port) {
        return Data::list(std::string(port.name), encode_operator(port.oper));
    }

    template <class T>
    Data encode_optional(Optional<T> const & value) {
        Data encoded;
        if (value.is_set())
            encoded = value.get();
        return encoded;
    }

    template <typename T>
    Data encode_vector(std::vector<T> const & value) {
        auto retval = Data::nils(value.size());
        for (std::size_t i = 0u; i < value.size(); ++i)
            retval[i] = value[i];
        return retval;
    }

    Data encode_profile_event(ProfileEvent const & event) {
        if (!event.start_time.is_set() || !event.stop_time.is_set()) {
            throw std::runtime_error(
                    "Incomplete ProfileEvent sent. This is a bug, please"
                    " report it.");
        }

        Data encoded_port;
        if (event.port.is_set())
            encoded_port = encode_port(event.port.get());

        return Data::list(
                static_cast<int>(event.event_type),
                event.start_time.get().nanoseconds,
                event.stop_time.get().nanoseconds,
                encoded_port, encode_optional(event.port_length),
                encode_optional(event.slot), encode_optional(event.message_number),
                encode_optional(event.message_size),
                encode_optional(event.message_timestamp));
    }

    Data encode_snapshot_metadata(SnapshotMetadata const & snapshot_metadata) {
        auto port_message_counts = Data::dict();
        for(auto const & kv : snapshot_metadata.port_message_counts)
            port_message_counts[kv.first] = encode_vector(kv.second);

        auto metadata = Data::dict(
                "triggers", encode_vector(snapshot_metadata.triggers),
                "wallclock_time", snapshot_metadata.wallclock_time,
                "timestamp", snapshot_metadata.timestamp,
                "next_timestamp", encode_optional(snapshot_metadata.next_timestamp),
                "port_message_counts", port_message_counts,
                "is_final_snapshot", snapshot_metadata.is_final_snapshot,
                "snapshot_filename", snapshot_metadata.snapshot_filename
        );

        return metadata;
    }

    template <typename T>
    Optional<T> decode_optional(DataConstRef const & data) {
        if (data.is_nil())
            return {};
        return data.as<T>();
    }
}

namespace libmuscle { namespace _MUSCLE_IMPL_NS {

MMPClient::MMPClient(
        Reference const & instance_id, std::string const & location)
    : instance_id_(instance_id)
    , transport_client_(location)
{}

void MMPClient::close() {
    transport_client_.close();
}

void MMPClient::submit_log_message(LogMessage const & message) {
    auto request = Data::list(
            static_cast<int>(RequestType::submit_log_message),
            message.instance_id,
            message.timestamp.seconds,
            static_cast<int>(message.level),
            message.text);

    call_manager_(request);
}

void MMPClient::submit_profile_events(
        std::vector<ProfileEvent> const & events)
{
    auto event_list = Data::nils(events.size());
    for (std::size_t i = 0u; i < events.size(); ++i)
        event_list[i] = encode_profile_event(events[i]);

    auto request = Data::list(
            static_cast<int>(RequestType::submit_profile_events),
            static_cast<std::string>(instance_id_),
            event_list);

    auto response = call_manager_(request);
}

void MMPClient::submit_snapshot_metadata(
        SnapshotMetadata const & snapshot_metadata) {
    auto request = Data::list(
            static_cast<int>(RequestType::submit_snapshot),
            static_cast<std::string>(instance_id_),
            encode_snapshot_metadata(snapshot_metadata));

    auto response = call_manager_(request);
}

void MMPClient::register_instance(
        std::vector<std::string> const & locations,
        std::vector<::ymmsl::Port> const & ports)
{
    auto encoded_locs = encode_vector(locations);
    auto encoded_ports = Data::nils(ports.size());
    for (std::size_t i = 0u; i < ports.size(); ++i)
        encoded_ports[i] = encode_port(ports[i]);

    auto request = Data::list(
            static_cast<int>(RequestType::register_instance),
            static_cast<std::string>(instance_id_), encoded_locs,
            encoded_ports, MUSCLE3_VERSION);

    auto response = call_manager_(request);

    if (response[0].as<int>() == static_cast<int>(ResponseType::error))
        throw std::runtime_error(
                "Error registering instance: " + response[1].as<std::string>());
}

ymmsl::Settings MMPClient::get_settings() {
    auto request = Data::list(static_cast<int>(RequestType::get_settings));
    auto response = call_manager_(request);
    // always returns success, so no need to check

    auto dict = response[1];

    ymmsl::Settings settings;
    for (std::size_t i = 0u; i < dict.size(); ++i)
        settings[dict.key(i)] = dict.value(i).as<SettingValue>();

    return settings;
}

auto MMPClient::get_checkpoint_info() ->
        std::tuple<
            double,
            DataConstRef,
            Optional<std::string>,
            Optional<std::string>
        >
{
    auto request = Data::list(
            static_cast<int>(RequestType::get_checkpoint_info),
            static_cast<std::string>(instance_id_));
    auto response = call_manager_(request);

    if (response[0].as<int>() != static_cast<int>(ResponseType::success)) {
        throw std::runtime_error("Error getting checkpoint info from manager.");
    }

    return std::make_tuple(
            response[1].as<double>(),
            response[2],
            decode_optional<std::string>(response[3]),
            decode_optional<std::string>(response[4]));
}

auto MMPClient::request_peers() ->
        std::tuple<
            std::vector<::ymmsl::Conduit>,
            std::unordered_map<::ymmsl::Reference, std::vector<int>>,
            std::unordered_map<::ymmsl::Reference, std::vector<std::string>>
        >
{
    int sleep_time = 100;   // milliseconds
    auto start_time = steady_clock::now();

    auto request = Data::list(
            static_cast<int>(RequestType::get_peers),
            static_cast<std::string>(instance_id_));
    auto response = call_manager_(request);

    const int status_pending = static_cast<int>(ResponseType::pending);

    while ((response[0].as<int>() == status_pending) &&
           (steady_clock::now() < start_time + peer_timeout) &&
           (sleep_time < peer_interval_min)) {
        std::this_thread::sleep_for(std::chrono::milliseconds(sleep_time));
        response.reseat(call_manager_(request));
        sleep_time += sleep_time / 2;
    }

    while ((response[0].as<int>() == status_pending) &&
           (steady_clock::now() < start_time + peer_timeout)) {
        std::this_thread::sleep_for(random_sleep_time());
        response.reseat(call_manager_(request));
    }

    if (response[0].as<int>() == status_pending)
        throw std::runtime_error("Timeout waiting for peers to appear.");

    if (response[0].as<int>() == static_cast<int>(ResponseType::error)) {
        std::ostringstream oss;
        oss << "Error getting peers from manager: " << response[1].as<std::string>();
        throw std::runtime_error(oss.str());
    }

    auto const & recv_conduits = response[1];
    std::vector<Conduit> conduits;
    for (std::size_t i = 0u; i < recv_conduits.size(); ++i)
        conduits.emplace_back(
                recv_conduits[i][0].as<std::string>(), recv_conduits[i][1].as<std::string>());


    auto const & recv_dims = response[2];
    std::unordered_map<Reference, std::vector<int>> peer_dimensions;
    for (std::size_t i = 0u; i < recv_dims.size(); ++i) {
        auto dim_list = recv_dims.value(i);
        std::vector<int> dims(dim_list.size());
        for (std::size_t j = 0u; j < dim_list.size(); ++j)
            dims[j] = dim_list[j].as<int>();

        peer_dimensions[recv_dims.key(i)] = dims;
    }

    auto const & recv_locs = response[3];
    std::unordered_map<Reference, std::vector<std::string>> peer_locations;
    for (std::size_t i = 0u; i < recv_locs.size(); ++i) {
        auto peer_locs = recv_locs.value(i);
        std::vector<std::string> locs(peer_locs.size());
        for (std::size_t j = 0u; j < peer_locs.size(); ++j)
            locs[j] = peer_locs[j].as<std::string>();

        peer_locations[recv_locs.key(i)] = locs;
    }

    return std::make_tuple(
            std::move(conduits),
            std::move(peer_dimensions),
            std::move(peer_locations));
}

void MMPClient::deregister_instance() {
    auto request = Data::list(
            static_cast<int>(RequestType::deregister_instance),
            static_cast<std::string>(instance_id_));
    auto response = call_manager_(request);
    if (response[0].as<int>() == static_cast<int>(ResponseType::error)) {
        std::ostringstream oss;
        oss << "Failed to deregister: " << response[1].as<std::string>();
        throw std::runtime_error(oss.str());
    }
}

void MMPClient::waiting_for_receive(
        std::string const & peer_instance_id, std::string const & port_name,
        Optional<int> slot)
{
    auto request = Data::list(
            static_cast<int>(RequestType::waiting_for_receive),
            static_cast<std::string>(instance_id_),
            peer_instance_id, port_name, encode_optional(slot));

    auto response = call_manager_(request);
}

void MMPClient::waiting_for_receive_done(
        std::string const & peer_instance_id, std::string const & port_name,
        Optional<int> slot)
{
    auto request = Data::list(
            static_cast<int>(RequestType::waiting_for_receive_done),
            static_cast<std::string>(instance_id_),
            peer_instance_id, port_name, encode_optional(slot));

    auto response = call_manager_(request);
}

bool MMPClient::is_deadlocked() {
    auto request = Data::list(
            static_cast<int>(RequestType::is_deadlocked),
            static_cast<std::string>(instance_id_));
    
    auto response = call_manager_(request);
    return response[1].as<bool>();
}

DataConstRef MMPClient::call_manager_(DataConstRef const & request) {
    std::lock_guard<std::mutex> lock(mutex_);

    msgpack::sbuffer sbuf;
    msgpack::pack(sbuf, request);

    auto res = transport_client_.call(sbuf.data(), sbuf.size());
    auto const & result = std::get<0>(res);

    auto zone = std::make_shared<msgpack::zone>();
    return unpack_data(zone, result.data(), result.size());
}


} }

