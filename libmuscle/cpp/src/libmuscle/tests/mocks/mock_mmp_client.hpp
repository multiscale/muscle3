#pragma once

#include <string>
#include <tuple>
#include <unordered_map>
#include <vector>

#include <libmuscle/logging.hpp>
#include <libmuscle/timestamp.hpp>

#include <ymmsl/ymmsl.hpp>


namespace libmuscle { namespace impl {

class MockMMPClient {
    public:
        MockMMPClient(std::string const & location);

        void submit_log_message(LogMessage const & message);

        ymmsl::Settings get_settings();

        void register_instance(
                ::ymmsl::Reference const & name,
                std::vector<std::string> const & locations,
                std::vector<::ymmsl::Port> const & ports);

        auto request_peers(::ymmsl::Reference const & name) ->
            std::tuple<
                std::vector<::ymmsl::Conduit>,
                std::unordered_map<::ymmsl::Reference, std::vector<int>>,
                std::unordered_map<::ymmsl::Reference, std::vector<std::string>>
            >;

        void deregister_instance(::ymmsl::Reference const & name);

        static void reset();

        static int num_constructed;
        static std::string last_location;
        static ::ymmsl::Reference last_registered_name;
        static std::vector<std::string> last_registered_locations;
        static std::vector<::ymmsl::Port> last_registered_ports;
        static LogMessage last_submitted_log_message;
};

using MMPClient = MockMMPClient;

} }

