#pragma once

#include <memory>
#include <string>

#include "libmuscle/logging.hpp"
#include "muscle_manager_protocol/muscle_manager_protocol.grpc.pb.h"
#include "ymmsl/settings.hpp"


namespace libmuscle {

/** The client for the MUSCLE Manager Protocol.
 *
 * This class connects to the Manager and communicates with it on behalf of the
 * rest of libmuscle.
 *
 * It manages the connection, and converts between our native types and the
 * gRPC generated types.
 */
class MMPClient {
    public:
        /** Create an MMPClient.
         *
         * @param location A connection string of the form hostname:port.
         */
        MMPClient(std::string const & location);

        /** Send a log message to the manager.
         *
         * @param message The message to send.
         */
        void submit_log_message(LogMessage const & message);

        /** Get the global settings from the manager.
         *
         * @return A Settings object with the global settings.
         */
        ymmsl::Settings get_settings();

    private:
        std::unique_ptr<muscle_manager_protocol::MuscleManager::Stub> client_;
};

}

