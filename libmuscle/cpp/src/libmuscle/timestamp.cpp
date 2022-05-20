#include <chrono>
#include <cinttypes>
#include <cmath>
#include <memory>

#include <libmuscle/timestamp.hpp>
#include <muscle_manager_protocol/muscle_manager_protocol.pb.h>

using wallclock = std::chrono::high_resolution_clock;


namespace libmuscle { namespace impl {

Timestamp::Timestamp(double seconds)
    : seconds(seconds)
{}

Timestamp Timestamp::now() {
    auto since_epoch = wallclock::now().time_since_epoch();
    double cycles = since_epoch.count();
    double seconds = cycles * wallclock::period::num / wallclock::period::den;
    return Timestamp(seconds);
}

Timestamp Timestamp::from_grpc(
        ::google::protobuf::Timestamp const & timestamp
) {
    return Timestamp(timestamp.seconds() + timestamp.nanos() * 1e-9);
}

std::unique_ptr<::google::protobuf::Timestamp> Timestamp::to_grpc() const {
    auto result = std::make_unique<::google::protobuf::Timestamp>();

    result->set_seconds(static_cast<::google::protobuf::int64>(seconds));
    result->set_nanos(static_cast<::google::protobuf::int32>(
            fmod(seconds, 1.0) * 1e9));
    return result;
}

} }

