// Inject mocks
#define LIBMUSCLE_MOCK_MCP_TCP_TRANSPORT_SERVER <mocks/mcp/mock_tcp_transport_server.hpp>
#define LIBMUSCLE_MOCK_POST_OFFICE <mocks/mock_post_office.hpp>

// into the real implementation under test.
#include <libmuscle/mcp/data_pack.cpp>
#include <libmuscle/mpp_server.cpp>
#include <libmuscle/mcp/transport_server.cpp>
#include <ymmsl/ymmsl.hpp>

// Test code dependencies
#include <gtest/gtest.h>
#include <libmuscle/namespace.hpp>
#include <mocks/mcp/mock_tcp_transport_server.hpp>
#include <mocks/mock_post_office.hpp>


int main(int argc, char *argv[]) {
    ::testing::InitGoogleTest(&argc, argv);
    return RUN_ALL_TESTS();
}


using libmuscle::_MUSCLE_IMPL_NS::mcp::MockTcpTransportServer;
using libmuscle::_MUSCLE_IMPL_NS::MockPostOffice;
using libmuscle::_MUSCLE_IMPL_NS::MPPServer;

using ymmsl::Conduit;
using ymmsl::Reference;


/* Fixture */
struct libmuscle_mpp_server : ::testing::Test {
    RESET_MOCKS(MockPostOffice, MockTcpTransportServer);

    MPPServer mpp_server_;

    libmuscle_mpp_server() {
        dynamic_cast<MockTcpTransportServer&>(*mpp_server_.servers_.back()
                ).get_location_mock.return_value = "tcp:testing:9001";
    }
};


/* Tests */
TEST_F(libmuscle_mpp_server, get_locations) {
    ASSERT_EQ(mpp_server_.get_locations().size(), 1);
    ASSERT_EQ(mpp_server_.get_locations()[0], "tcp:testing:9001");
}

