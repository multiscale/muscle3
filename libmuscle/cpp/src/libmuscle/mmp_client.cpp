#include "libmuscle/mmp_client.hpp"

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

#include <grpc++/grpc++.h>

#include <libmuscle/port_grpc.hpp>
#include "muscle_manager_protocol/muscle_manager_protocol.grpc.pb.h"
#include "muscle_manager_protocol/muscle_manager_protocol.pb.h"
#include <ymmsl/identity.hpp>
#include <ymmsl/model.hpp>
#include "ymmsl/settings.hpp"

namespace mmp = muscle_manager_protocol;

using std::chrono::steady_clock;
using ymmsl::Conduit;
using ymmsl::Reference;


namespace {
    float connection_timeout = 300.0f;
    std::chrono::milliseconds peer_timeout(600000);        // milliseconds
    int peer_interval_min = 5000;     // milliseconds
    int peer_interval_max = 10000;    // milliseconds

    std::chrono::milliseconds random_sleep_time() {
        static std::default_random_engine engine;
        static std::uniform_int_distribution<int> dist(
                peer_interval_min, peer_interval_max);

        return std::chrono::milliseconds(dist(engine));
    }

    std::vector<double> list_from_grpc(mmp::ListOfDouble const & mmp_list) {
        std::vector<double> our_list;
        for (int i = 0; i < mmp_list.values_size(); ++i)
            our_list.push_back(mmp_list.values(i));
        return our_list;
    }

    Conduit conduit_from_grpc(mmp::Conduit const & conduit) {
        return Conduit(conduit.sender(), conduit.receiver());
    }
}

namespace libmuscle {

MMPClient::MMPClient(std::string const & location) {
    std::shared_ptr<grpc::Channel> channel = grpc::CreateChannel(
            location, grpc::InsecureChannelCredentials());
    client_ = mmp::MuscleManager::NewStub(channel);

    float total_time = 0.0f;
    while (channel->GetState(true) != GRPC_CHANNEL_READY) {
        if (total_time >= connection_timeout)
            throw std::runtime_error("Failed to connect to the MUSCLE manager");
        std::this_thread::sleep_for(std::chrono::milliseconds(100));
        total_time += 0.1f;
    }
}

void MMPClient::submit_log_message(LogMessage const & message) {
    grpc::ClientContext context;
    auto request = message.to_grpc();
    mmp::LogResult response;
    client_->SubmitLogMessage(&context, request, &response);
    // TODO: check status
}

void MMPClient::register_instance(
        Reference const & name,
        std::vector<std::string> const & locations,
        std::vector<::ymmsl::Port> const & ports)
{
    std::vector<mmp::Port> grpc_ports;
    std::transform(
            ports.cbegin(), ports.cend(),
            std::back_inserter(grpc_ports), port_to_grpc);

    mmp::RegistrationRequest request;
    request.set_instance_name(static_cast<std::string>(name));
    for (auto const & loc : locations)
        request.add_network_locations(loc);
    for (auto const & port : grpc_ports)
        *request.add_ports() = port;

    grpc::ClientContext context;
    mmp::RegistrationResult response;
    client_->RegisterInstance(&context, request, &response);
    // TODO: check status
}

ymmsl::Settings MMPClient::get_settings() {
    grpc::ClientContext context;
    mmp::SettingsResult response;
    client_->RequestSettings(&context, mmp::SettingsRequest(), &response);

    ymmsl::Settings settings;
    for (int i = 0; i < response.setting_values_size(); ++i) {
        auto const & cur = response.setting_values(i);
        switch (cur.value_type()) {
            case mmp::SETTING_VALUE_TYPE_STRING:
                settings[cur.name()] = cur.value_string();
                break;
            case mmp::SETTING_VALUE_TYPE_INT:
                settings[cur.name()] = cur.value_int();
                break;
            case mmp::SETTING_VALUE_TYPE_FLOAT:
                settings[cur.name()] = cur.value_float();
                break;
            case mmp::SETTING_VALUE_TYPE_BOOL:
                settings[cur.name()] = cur.value_bool();
                break;
            case mmp::SETTING_VALUE_TYPE_LIST_FLOAT: {
                auto mmp_list = cur.value_list_float();
                settings[cur.name()] = list_from_grpc(mmp_list);
                break;
            }
            case mmp::SETTING_VALUE_TYPE_LIST_LIST_FLOAT: {
                using Vec2 = std::vector<std::vector<double>>;
                auto mmp_list = cur.value_list_list_float();
                Vec2 our_list;
                for (int j = 0; j < mmp_list.values_size(); ++j)
                    our_list.push_back(list_from_grpc(mmp_list.values(j)));
                settings[cur.name()] = std::move(our_list);
                break;
            }
            default:
                // catch some gRPC-defined not-to-be-used values
                break;
        }
    }
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

    grpc::ClientContext context;

    mmp::PeerRequest request;
    request.set_instance_name(static_cast<std::string>(name));

    mmp::PeerResult result;
    client_->RequestPeers(&context, request, &result);

    while ((result.status() == mmp::RESULT_STATUS_PENDING) &&
           (steady_clock::now() < start_time + peer_timeout) &&
           (sleep_time < peer_interval_min)) {
        std::this_thread::sleep_for(std::chrono::milliseconds(sleep_time));
        client_->RequestPeers(&context, request, &result);
        sleep_time += sleep_time / 2;
    }

    while ((result.status() == mmp::RESULT_STATUS_PENDING) &&
           (steady_clock::now() < start_time + peer_timeout)) {
        std::this_thread::sleep_for(random_sleep_time());
        client_->RequestPeers(&context, request, &result);
    }

    if (result.status() == mmp::RESULT_STATUS_PENDING)
        throw std::runtime_error("Timeout waiting for peers to appear.");

    if (result.status() == mmp::RESULT_STATUS_ERROR) {
        std::ostringstream oss;
        oss << "Error getting peers from manager: " << result.error_message();
        throw std::runtime_error(oss.str());
    }

    std::vector<Conduit> conduits;
    std::transform(
            result.conduits().cbegin(), result.conduits().cend(),
            std::back_inserter(conduits), conduit_from_grpc);

    std::unordered_map<Reference, std::vector<int>> peer_dimensions;
    for (int i = 0; i < result.peer_dimensions_size(); ++i) {
        auto peer_dims = result.peer_dimensions(i);
        std::vector<int> dims(peer_dims.dimensions_size());
        for (int j = 0; j < peer_dims.dimensions_size(); ++j)
            dims[j] = peer_dims.dimensions(j);
        peer_dimensions[peer_dims.peer_name()] = dims;
    }

    std::unordered_map<Reference, std::vector<std::string>> peer_locations;
    for (int i = 0; i < result.peer_locations_size(); ++i) {
        auto peer_locs = result.peer_locations(i);
        std::vector<std::string> locs(peer_locs.locations_size());
        for (int j = 0; j < peer_locs.locations_size(); ++j)
            locs[j] = peer_locs.locations(j);
        peer_locations[peer_locs.instance_name()] = locs;
    }

    return std::make_tuple(
            std::move(conduits),
            std::move(peer_dimensions),
            std::move(peer_locations));
}

void MMPClient::deregister_instance(Reference const & name) {
    grpc::ClientContext context;
    mmp::DeregistrationRequest request;
    request.set_instance_name(static_cast<std::string>(name));
    mmp::DeregistrationResult response;
    client_->DeregisterInstance(&context, request, &response);
}

}

