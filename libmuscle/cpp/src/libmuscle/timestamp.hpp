#pragma once

#include <muscle_manager_protocol/muscle_manager_protocol.pb.h>

namespace libmuscle {


/** A timestamp, as the number of seconds since the UNIX epoch.
 */
class Timestamp {
    public:
        /** Create a Timestamp.
         *
         * @param seconds The number of seconds since the UNIX epoch.
         */
        Timestamp(double seconds);

        /** Create a Timestamp from a gRPC Timestamp message.
         *
         * @param timestamp A gRPC Timestamp from a gRPC call.
         * @return The same timestamp as a Timestamp object.
         */
        static Timestamp from_grpc(
                ::google::protobuf::Timestamp const & timestamp);

        /** Convert a Timestamp to the gRPC type.
         *
         * @return This timestamp as a gRPC object.
         */
        std::unique_ptr<google::protobuf::Timestamp> to_grpc() const;

    private:
        double seconds_;
};

}

