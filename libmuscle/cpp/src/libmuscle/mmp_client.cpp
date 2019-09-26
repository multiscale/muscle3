#include <chrono>
#include <memory>
#include <string>
#include <thread>
#include <utility>
#include <vector>

#include <grpc++/grpc++.h>

#include "libmuscle/mmp_client.hpp"
#include <libmuscle/port_grpc.hpp>
#include "muscle_manager_protocol/muscle_manager_protocol.grpc.pb.h"
#include "muscle_manager_protocol/muscle_manager_protocol.pb.h"
#include <ymmsl/identity.hpp>
#include "ymmsl/settings.hpp"

namespace mmp = muscle_manager_protocol;

using ymmsl::Reference;


namespace {
    float connection_timeout = 300.0f;

    std::vector<double> list_from_grpc(mmp::ListOfDouble const & mmp_list) {
        std::vector<double> our_list;
        for (int i = 0; i < mmp_list.values_size(); ++i)
            our_list.push_back(mmp_list.values(i));
        return our_list;
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
    for (int i = 0; i < response.parameter_values_size(); ++i) {
        auto const & cur = response.parameter_values(i);
        switch (cur.value_type()) {
            case mmp::PARAMETER_VALUE_TYPE_STRING:
                settings[cur.parameter()] = cur.value_string();
                break;
            case mmp::PARAMETER_VALUE_TYPE_INT:
                settings[cur.parameter()] = cur.value_int();
                break;
            case mmp::PARAMETER_VALUE_TYPE_FLOAT:
                settings[cur.parameter()] = cur.value_float();
                break;
            case mmp::PARAMETER_VALUE_TYPE_BOOL:
                settings[cur.parameter()] = cur.value_bool();
                break;
            case mmp::PARAMETER_VALUE_TYPE_LIST_FLOAT: {
                auto mmp_list = cur.value_list_float();
                settings[cur.parameter()] = list_from_grpc(mmp_list);
                break;
            }
            case mmp::PARAMETER_VALUE_TYPE_LIST_LIST_FLOAT: {
                using Vec2 = std::vector<std::vector<double>>;
                auto mmp_list = cur.value_list_list_float();
                Vec2 our_list;
                for (int j = 0; j < mmp_list.values_size(); ++j)
                    our_list.push_back(list_from_grpc(mmp_list.values(j)));
                settings[cur.parameter()] = std::move(our_list);
                break;
            }
            default:
                // catch some gRPC-defined not-to-be-used values
                break;
        }
    }
    return settings;
}

}

