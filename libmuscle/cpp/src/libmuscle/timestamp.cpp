#include <cinttypes>
#include <cmath>
#include <memory>

#include "libmuscle/timestamp.hpp"
#include "muscle_manager_protocol/muscle_manager_protocol.pb.h"


namespace libmuscle {

Timestamp::Timestamp(double seconds)
    : seconds_(seconds)
{}

Timestamp Timestamp::from_grpc(
        ::google::protobuf::Timestamp const & timestamp
) {
    return Timestamp(timestamp.seconds() + timestamp.nanos() * 1e-9);
}

std::unique_ptr<::google::protobuf::Timestamp> Timestamp::to_grpc() const {
    auto result = std::make_unique<::google::protobuf::Timestamp>();

    result->set_seconds(static_cast<::google::protobuf::int64>(seconds_));
    result->set_nanos(static_cast<::google::protobuf::int32>(
            fmod(seconds_, 1.0) * 1e-9));
    return result;
}

}

