#include "mocks/mock_mmp_client.hpp"

#include <ymmsl/identity.hpp>
#include <ymmsl/model.hpp>
#include "ymmsl/settings.hpp"


using ymmsl::Conduit;
using ymmsl::Reference;


namespace libmuscle {

MockMMPClient::MockMMPClient(std::string const & location) {
    ++num_constructed;
    last_location = location;
}

void MockMMPClient::submit_log_message(LogMessage const & message) {}

void MockMMPClient::register_instance(
        Reference const & name,
        std::vector<std::string> const & locations,
        std::vector<::ymmsl::Port> const & ports)
{}

ymmsl::Settings MockMMPClient::get_settings() {
    ymmsl::Settings settings;
    return settings;
}

auto MockMMPClient::request_peers(Reference const & name) ->
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

void MockMMPClient::deregister_instance(Reference const & name) {}

void MockMMPClient::reset() {
    num_constructed = 0;
    last_location = "";
}

int MockMMPClient::num_constructed = 0;

std::string MockMMPClient::last_location("");

}

