#include <chrono>
#include <memory>
#include <thread>

#include <grpc++/grpc++.h>

#include "libmuscle/mmp_client.hpp"
#include "muscle_manager_protocol/muscle_manager_protocol.grpc.pb.h"
#include "muscle_manager_protocol/muscle_manager_protocol.pb.h"

namespace mmp = muscle_manager_protocol;


namespace {
    float connection_timeout = 300.0f;
}

namespace libmuscle {

MMPClient::MMPClient(std::string const & location)
        : context_(std::make_unique<grpc::ClientContext>())
{
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
    auto request = message.to_grpc();
    mmp::LogResult response;
    client_->SubmitLogMessage(context_.get(), request, &response);
}

}

