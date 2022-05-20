#include <gtest/gtest.h>

#include <libmuscle/mcp/transport_server.hpp>
#include <libmuscle/mcp/tcp_transport_client.hpp>
#include <libmuscle/mcp/tcp_transport_server.hpp>

#include <algorithm>
#include <string>
#include <vector>

#include <iostream>
#include <ostream>


using libmuscle::impl::mcp::RequestHandler;
using libmuscle::impl::mcp::TcpTransportClient;
using libmuscle::impl::mcp::TcpTransportServer;


int main(int argc, char *argv[]) {
    ::testing::InitGoogleTest(&argc, argv);
    return RUN_ALL_TESTS();
}


class MockHandlerDirect : public RequestHandler {
public:
    virtual int handle_request(
            char const * req_buf, std::size_t req_len, std::vector<char> & res_buf
    ) override {
        std::string request(req_buf, req_len);
        if (request != "TestRequest")
            throw std::runtime_error("Unexpected request " + request);

        std::string response("TestResponse");
        res_buf.resize(response.size());
        std::copy(response.cbegin(), response.cend(), res_buf.begin());
        return -1;
    };

    virtual void get_response(int fd, std::vector<char> & res_buf) override {
        // Should not be called if we return -1 above
        ASSERT_TRUE(false);
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
            char const * req_buf, std::size_t req_len, std::vector<char> & res_buf
    ) override {
        std::cout << "handle_request" << std::endl;
        std::string request(req_buf, req_len);
        if (request != "TestRequest")
            throw std::runtime_error("Unexpected request " + request);

        return pipe_fds[0];
    };

    virtual void get_response(int fd, std::vector<char> & res_buf) override {
        std::cout << "get_response" << std::endl;
        if (fd != pipe_fds[0])
            throw std::runtime_error("Unexpected fd in get_response");

        std::string response("TestResponse");
        res_buf.resize(response.size());
        std::copy(response.cbegin(), response.cend(), res_buf.begin());
    };

    void send_response() {
        if (write(pipe_fds[1], "\0", 1) != 1)
            throw std::runtime_error("Error writing to signal pipe");
        std::cout << "Wrote" << std::endl;
    };

    int pipe_fds[2];
};


TEST(test_tcp_communication, send_receive_direct) {
    MockHandlerDirect handler;
    TcpTransportServer server(handler);
    std::string location = server.get_location();
    ASSERT_TRUE(TcpTransportClient::can_connect_to(location));
    TcpTransportClient client(location);

    std::vector<char> result;
    client.call("TestRequest", strlen("TestRequest"), result);

    std::string response(result.size(), ' ');
    std::copy(result.cbegin(), result.cend(), response.begin());

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

    std::vector<char> result;
    client.call("TestRequest", strlen("TestRequest"), result);
    std::cout << "call done" << std::endl;

    std::string response(result.size(), ' ');
    std::copy(result.cbegin(), result.cend(), response.begin());

    ASSERT_EQ(response, "TestResponse");

    std::cout << "closing client" << std::endl;
    client.close();
    std::cout << "closing server" << std::endl;
    server.close();
    std::cout << "done" << std::endl;
}

