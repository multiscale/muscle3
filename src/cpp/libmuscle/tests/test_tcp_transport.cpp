#include <gtest/gtest.h>

#include <libmuscle/data.hpp>
#include <libmuscle/mcp/transport_server.hpp>
#include <libmuscle/mcp/tcp_transport_client.hpp>
#include <libmuscle/mcp/tcp_transport_server.hpp>
#include <libmuscle/namespace.hpp>

#include <msgpack.hpp>

#include <algorithm>
#include <string>
#include <tuple>
#include <unistd.h>
#include <vector>


using libmuscle::_MUSCLE_IMPL_NS::Data;
using libmuscle::_MUSCLE_IMPL_NS::DataConstRef;
using libmuscle::_MUSCLE_IMPL_NS::mcp::RequestHandler;
using libmuscle::_MUSCLE_IMPL_NS::mcp::TcpTransportClient;
using libmuscle::_MUSCLE_IMPL_NS::mcp::TcpTransportServer;


int main(int argc, char *argv[]) {
    ::testing::InitGoogleTest(&argc, argv);
    return RUN_ALL_TESTS();
}


class MockHandlerDirect : public RequestHandler {
public:
    virtual int handle_request(
            char const * req_buf, std::size_t req_len,
            std::vector<char> & res_buf
    ) override {
        std::string request(req_buf, req_len);
        if (request != "TestRequest")
            throw std::runtime_error("Unexpected request " + request);

        std::string response("TestResponse");
        std::vector<char> response_data(response.size());
        memcpy(response_data.data(), response.c_str(), response.size());
        res_buf = std::move(response_data);
        return -1;
    };

    virtual std::vector<char> get_response(int fd) override {
        // Should not be called if we return -1 above
        throw std::runtime_error("Should not be called");
    };

};


class MockHandlerDelayed : public RequestHandler {
public:
    MockHandlerDelayed() {
        pipe(pipe_fds);
    }

    ~MockHandlerDelayed() {
        close(pipe_fds[0]);
        close(pipe_fds[1]);
    }

    virtual int handle_request(
            char const * req_buf, std::size_t req_len,
            std::vector<char> & res_buf
    ) override {
        std::string request(req_buf, req_len);
        if (request != "TestRequest")
            throw std::runtime_error("Unexpected request " + request);

        return pipe_fds[0];
    };

    virtual std::vector<char> get_response(int fd) override {
        if (fd != pipe_fds[0])
            throw std::runtime_error("Unexpected fd in get_response");

        std::string response("TestResponse");
        std::vector<char> response_data(response.size());
        memcpy(response_data.data(), response.c_str(), response.size());
        return response_data;
    };

    void send_response() {
        if (write(pipe_fds[1], "\0", 1) != 1)
            throw std::runtime_error("Error writing to signal pipe");
    };

    int pipe_fds[2];
};


TEST(test_tcp_communication, send_receive_direct) {
    MockHandlerDirect handler;
    TcpTransportServer server(handler);
    std::string location = server.get_location();
    ASSERT_TRUE(TcpTransportClient::can_connect_to(location));
    TcpTransportClient client(location);

    auto res = client.call("TestRequest", strlen("TestRequest"));
    auto result = std::get<0>(res);

    std::string response(result.begin(), result.end());
    ASSERT_EQ(response, "TestResponse");

    client.close();
    server.close();
}


TEST(test_tcp_communication, send_receive_delayed) {
    MockHandlerDelayed handler;
    TcpTransportServer server(handler);
    std::string location = server.get_location();
    ASSERT_TRUE(TcpTransportClient::can_connect_to(location));
    TcpTransportClient client(location);

    handler.send_response();

    auto res = client.call("TestRequest", strlen("TestRequest"));
    auto result = std::get<0>(res);

    std::string response(result.begin(), result.end());
    ASSERT_EQ(response, "TestResponse");

    client.close();
    server.close();
}

