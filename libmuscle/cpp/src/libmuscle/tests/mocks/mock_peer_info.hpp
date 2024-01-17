#pragma once

#include <ymmsl/ymmsl.hpp>

#include <libmuscle/endpoint.hpp>
#include <libmuscle/namespace.hpp>
#include <mocks/mock_support.hpp>

#include <string>
#include <unordered_map>
#include <vector>


namespace libmuscle { namespace _MUSCLE_IMPL_NS {

using PeerDims = std::unordered_map<ymmsl::Reference, std::vector<int>>;
using PeerLocations = std::unordered_map<
        ymmsl::Reference, std::vector<std::string>>;

class MockPeerInfo : public MockClass<MockPeerInfo> {
    public:
        MockPeerInfo(ReturnValue) {
            NAME_MOCK_MEM_FUN(MockPeerInfo, constructor);
            NAME_MOCK_MEM_FUN(MockPeerInfo, is_connected);
            NAME_MOCK_MEM_FUN(MockPeerInfo, get_peer_ports);
            NAME_MOCK_MEM_FUN(MockPeerInfo, get_peer_dims);
            NAME_MOCK_MEM_FUN(MockPeerInfo, get_peer_locations);
            NAME_MOCK_MEM_FUN(MockPeerInfo, get_peer_endpoints);
        }

        MockPeerInfo(
                ymmsl::Reference const & kernel,
                std::vector<int> const & index,
                std::vector<ymmsl::Conduit> const & conduits,
                PeerDims const & peer_dims,
                PeerLocations const & peer_locations)
        {
            init_from_return_value();
            constructor(kernel, index, conduits, peer_dims, peer_locations);
        }

        MockFun<Void,
            Val<ymmsl::Reference const &>,
            Val<std::vector<int> const &>,
            Val<std::vector<ymmsl::Conduit> const &>,
            Val<PeerDims const &>,
            Val<PeerLocations const &>
        > constructor;

        MockFun<Val<bool>, Val<ymmsl::Identifier const &>> is_connected;

        MockFun<
            Val<std::vector<ymmsl::Reference>>,
            Val<ymmsl::Identifier const &>
        > get_peer_ports;

        MockFun<Val<std::vector<int>>, Val<ymmsl::Reference const &>> get_peer_dims;

        MockFun<
            Val<std::vector<std::string>>,
            Val<ymmsl::Reference const &>
        > get_peer_locations;

        MockFun<
            Val<std::vector<Endpoint>>,
            Val<ymmsl::Identifier const &>,
            Val<std::vector<int> const &>
        > get_peer_endpoints;
};

using PeerInfo = MockPeerInfo;

} }

