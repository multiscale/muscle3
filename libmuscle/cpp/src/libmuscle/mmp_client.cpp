#include "libmuscle/mmp_client.hpp"

#include "libmuscle/data.hpp"
#include "libmuscle/mcp/data_pack.hpp"
#include "libmuscle/mcp/protocol.hpp"

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


using libmuscle::impl::Data;
using libmuscle::impl::DataConstRef;
using libmuscle::impl::mcp::unpack_data;
using std::chrono::steady_clock;
using ymmsl::Conduit;
using ymmsl::Reference;
using ymmsl::SettingValue;


namespace {
    const float connection_timeout = 300.0f;
    const std::chrono::milliseconds peer_timeout(600000);   // milliseconds
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

}

namespace libmuscle { namespace impl {

MMPClient::MMPClient(std::string const & location)
    : transport_client_(location)
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

void MMPClient::register_instance(
        Reference const & name,
        std::vector<std::string> const & locations,
        std::vector<::ymmsl::Port> const & ports)
{
    auto encoded_locs = Data::nils(locations.size());
    for (std::size_t i = 0u; i < locations.size(); ++i)
        encoded_locs[i] = locations[i];

    auto encoded_ports = Data::nils(ports.size());
    for (std::size_t i = 0u; i < ports.size(); ++i)
        encoded_ports[i] = encode_port(ports[i]);

    auto request = Data::list(
            static_cast<int>(RequestType::register_instance),
            std::string(name), encoded_locs, encoded_ports);

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

auto MMPClient::request_peers(Reference const & name) ->
        std::tuple<
            std::vector<::ymmsl::Conduit>,
            std::unordered_map<::ymmsl::Reference, std::vector<int>>,
            std::unordered_map<::ymmsl::Reference, std::vector<std::string>>
        >
{
    int sleep_time = 100;   // milliseconds
    auto start_time = steady_clock::now();

    auto request = Data::list(static_cast<int>(RequestType::get_peers), std::string(name));
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

void MMPClient::deregister_instance(Reference const & name) {
    auto request = Data::list(
            static_cast<int>(RequestType::deregister_instance), std::string(name));
    auto response = call_manager_(request);
    if (response[0].as<int>() == static_cast<int>(ResponseType::error)) {
        std::ostringstream oss;
        oss << "Failed to deregister: " << response[1].as<std::string>();
        throw std::runtime_error(oss.str());
    }
}

DataConstRef MMPClient::call_manager_(DataConstRef const & request) {
    msgpack::sbuffer sbuf;
    msgpack::pack(sbuf, request);

    auto result = transport_client_.call(sbuf.data(), sbuf.size());

    auto zone = std::make_shared<msgpack::zone>();
    return unpack_data(zone, result.as_byte_array(), result.size());
}


} }

