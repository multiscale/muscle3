#include "mocks/mock_mmp_client.hpp"

#include <ymmsl/ymmsl.hpp>


using ymmsl::Conduit;
using ymmsl::Reference;


namespace libmuscle { namespace impl {

MockMMPClient::MockMMPClient(
        Reference const & instance_id, std::string const & location)
{
    ++num_constructed;
    last_instance_id = instance_id;
    last_location = location;
}

void MockMMPClient::close() {}

void MockMMPClient::submit_log_message(LogMessage const & message) {
    last_submitted_log_message = message;
}

void MockMMPClient::register_instance(
        std::vector<std::string> const & locations,
        std::vector<::ymmsl::Port> const & ports)
{
    last_registered_locations = locations;
    last_registered_ports = ports;
}

ymmsl::Settings MockMMPClient::get_settings() {
    ymmsl::Settings settings;
    settings["test_int"] = 10;
    settings["test_string"] = "testing";
    return settings;
}

auto MockMMPClient::request_peers() ->
        std::tuple<
            std::vector<::ymmsl::Conduit>,
            std::unordered_map<::ymmsl::Reference, std::vector<int>>,
            std::unordered_map<::ymmsl::Reference, std::vector<std::string>>
        >
{
    std::vector<Conduit> conduits;

    std::unordered_map<Reference, std::vector<int>> peer_dimensions;

    std::unordered_map<Reference, std::vector<std::string>> peer_locations;

    return std::make_tuple(
            std::move(conduits),
            std::move(peer_dimensions),
            std::move(peer_locations));
}

void MockMMPClient::deregister_instance() {}

void MockMMPClient::reset() {
    num_constructed = 0;
    last_instance_id = Reference("NONE");
    last_location = "";
    last_registered_locations.clear();
    last_registered_ports.clear();
    last_submitted_log_message.instance_id = "";
    last_submitted_log_message.timestamp = Timestamp(-1.0);
    last_submitted_log_message.level = LogLevel::DEBUG;
    last_submitted_log_message.text = "";
}

::ymmsl::Reference MockMMPClient::last_instance_id("NONE");

int MockMMPClient::num_constructed = 0;

std::string MockMMPClient::last_location("");

std::vector<std::string> MockMMPClient::last_registered_locations({});

std::vector<::ymmsl::Port> MockMMPClient::last_registered_ports({});

LogMessage MockMMPClient::last_submitted_log_message(
        "", Timestamp(-1.0), LogLevel::DEBUG, "");

} }

