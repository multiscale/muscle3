/* This is a part of the integration test suite, and is run from a Python
 * test in /integration_test. It is not a unit test.
 */
#include <cassert>
#include <cmath>
#include <cstddef>
#include <random>

#include <iostream>     // TODO: remove

#include <sys/socket.h>


void inject_fault(int socket_fd);

#define INJECT_BEFORE_TCP_RECEIVE ::inject_fault(socket_fd);
#define INJECT_BEFORE_TCP_SEND ::inject_fault(socket_fd);


#include <libmuscle/libmuscle.hpp>
#include <ymmsl/ymmsl.hpp>

#include <libmuscle/data.cpp>

#include <libmuscle/api_guard.cpp>
#include <libmuscle/checkpoint_triggers.cpp>
#include <libmuscle/close_port.cpp>
#include <libmuscle/communicator.cpp>
#include <libmuscle/endpoint.cpp>
#include <libmuscle/instance.cpp>
#include <libmuscle/logger.cpp>
#include <libmuscle/logging.cpp>
#include <libmuscle/mark.cpp>
#include <libmuscle/mcp/data_pack.cpp>
#include <libmuscle/mmp_client.cpp>
#include <libmuscle/mpp_client.cpp>
#include <libmuscle/mpp_message.cpp>
#include <libmuscle/mpp_server.cpp>
#include <libmuscle/mcp/session_state.cpp>
#include <libmuscle/mcp/tcp_util.cpp>
#include <libmuscle/mcp/transport_client.cpp>
#include <libmuscle/mcp/transport_server.cpp>
#include <libmuscle/mcp/tcp_transport_client.cpp>
#include <libmuscle/mcp/tcp_transport_server.cpp>
#include <libmuscle/message.cpp>
#include <libmuscle/mmsf_validator.cpp>
#include <libmuscle/outbox.cpp>
#include <libmuscle/peer_info.cpp>
#include <libmuscle/port.cpp>
#include <libmuscle/port_manager.cpp>
#include <libmuscle/post_office.cpp>
#include <libmuscle/profiling.cpp>
#include <libmuscle/profiler.cpp>
#include <libmuscle/settings_manager.cpp>
#include <libmuscle/snapshot.cpp>
#include <libmuscle/snapshot_manager.cpp>
#include <libmuscle/receive_timeout_handler.cpp>
#include <libmuscle/timestamp.cpp>
#include <libmuscle/util.cpp>


using libmuscle::Data;
using libmuscle::DataConstRef;
using libmuscle::Instance;
using libmuscle::Message;
using ymmsl::Operator;


double rand01() {
    static std::default_random_engine re(424242u);
    static std::uniform_real_distribution<> dist;
    return dist(re);
}


int random_mode() {
    static std::default_random_engine re(242424u);
    static std::uniform_int_distribution<> dist(0, 2);

    int options[] = {SHUT_RD, SHUT_RDWR, SHUT_WR};
    return options[dist(re)];
}


const double fault_prob_max = 0.1;
double start_time = 0.0;
double repeat_period = 0.0;


// Randomly closes the socket to simulate a dropped connection.
void inject_fault(int socket_fd) {
    double t = fmod((time_monotonic() - start_time), repeat_period);
    double fault_prob = 0.0;
    if (0.5 < t && t < 1.5)
        fault_prob = (t - 0.5) * fault_prob_max;
    else if (1.5 < t && t < 3.0)
        fault_prob = fault_prob_max;
    else if (3.0 < t && t < 4.0)
        fault_prob = (4.0 - t) * fault_prob_max;

    if (rand01() < fault_prob)
        shutdown(socket_fd, random_mode());
}


bool data_matches(DataConstRef const & data, int i) {
    if (!data.is_a_list()) return false;
    if (data.size() != (static_cast<std::size_t>(i) * 1000u)) return false;
    for (std::size_t k = 0u; k < data.size(); ++k)
        if (data[k].as<int>() != i) return false;
    return true;
}


/** A dummy component for TCP reconnect testing
 *
 * Compatible with the one in integration_test/conftest.py
 */
void component(int argc, char * argv[]) {
    Instance instance(argc, argv, {
            {Operator::F_INIT, {"init"}},       // int
            {Operator::O_I, {"out"}},           // int
            {Operator::S, {"in"}},              // int
            {Operator::O_F, {"result"}}});      // int

    int j = 0;
    while (instance.reuse_instance()) {
        auto init_msg = instance.receive("init", Message(0.0, Data()));
        assert(init_msg.data().is_nil() || data_matches(init_msg.data(), j));

        if (instance.is_connected("out")) {
            for (int i = 0; i < 200; ++i) {
                auto data = Data::nils(i * 1000);
                for (std::size_t k = 0u; k < data.size(); ++k)
                    data[k] = i;

                Message out_msg(static_cast<double>(i), data);
                instance.send("out", out_msg);

                auto in_msg = instance.receive("in", out_msg);
                assert(data_matches(in_msg.data(), i));
            }
        }

        // O_F
        instance.send("result", init_msg);
        ++j;
    }
}


int main(int argc, char * argv[]) {
    start_time = time_monotonic();
    repeat_period = 4.0 + rand01() * 2.0;

    component(argc, argv);
    return EXIT_SUCCESS;
}

