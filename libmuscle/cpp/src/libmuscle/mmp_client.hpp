#pragma once

#include <memory>
#include <string>

#include "libmuscle/logging.hpp"
#include "muscle_manager_protocol/muscle_manager_protocol.grpc.pb.h"
#include <ymmsl/compute_element.hpp>
#include <ymmsl/identity.hpp>
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

        /** Register a compute element instance with the manager.
         *
         * @param name Name of the instance in the simulation.
         * @param locations List of places where the instance can be reached.
         * @param ports List of ports of this instance.
         */
        void register_instance(
                ::ymmsl::Reference const & name,
                std::vector<std::string> const & locations,
                std::vector<::ymmsl::Port> const & ports);

    private:
        std::unique_ptr<muscle_manager_protocol::MuscleManager::Stub> client_;
};

}

