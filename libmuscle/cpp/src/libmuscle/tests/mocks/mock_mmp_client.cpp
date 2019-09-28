#include "libmuscle/mmp_client.hpp"

#include <chrono>
#include <iterator>
#include <memory>
#include <random>
#include <sstream>
#include <string>
#include <thread>
#include <tuple>
#include <utility>
#include <vector>

#include <ymmsl/identity.hpp>
#include <ymmsl/model.hpp>
#include "ymmsl/settings.hpp"


using ymmsl::Conduit;
using ymmsl::Reference;


namespace libmuscle {

MMPClient::MMPClient(std::string const & location) {}

void MMPClient::submit_log_message(LogMessage const & message) {}

void MMPClient::register_instance(
        Reference const & name,
        std::vector<std::string> const & locations,
        std::vector<::ymmsl::Port> const & ports)
{}

ymmsl::Settings MMPClient::get_settings() {
    ymmsl::Settings settings;
    return settings;
}

auto MMPClient::request_peers(Reference const & name) ->
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

void MMPClient::deregister_instance(Reference const & name) {}

}

