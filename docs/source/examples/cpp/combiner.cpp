#include <algorithm>
#include <iostream>
#include <stdexcept>
#include <string>
#include <vector>

#include <libmuscle/libmuscle.hpp>
#include <ymmsl/ymmsl.hpp>

using libmuscle::Data;
using libmuscle::Instance;
using libmuscle::Message;
using ymmsl::Operator;


int main(int argc, char * argv[]) {
    // 1. Request dynamic port configuration by not providing a ports description
    Instance instance(argc, argv);
    // Optionally provide instance flags with: Instance(argc, argv, instance_flags)

    // 2. Request which ports are available:
    auto ports = instance.list_ports();

    // check that we don't have any O_I or S ports defined
    if (!ports[Operator::O_I].empty() || !ports[Operator::S].empty()) {
        std::string msg = "The combiner component does not support O_I or S ports.";
        instance.error_shutdown(msg);
        throw std::runtime_error(msg);
    }

    // Find connected F_INIT ports
    std::vector<std::string> f_init_ports;
    for (auto && port_name : ports[Operator::F_INIT]) {
        if (instance.is_connected(port_name)) {
            f_init_ports.push_back(port_name);
        }
    }
    // sort them by name,
    std::sort(f_init_ports.begin(), f_init_ports.end());
    // and check that we have at least one input
    if (f_init_ports.empty()) {
        std::string msg = "The combiner actor requires at least one connected F_INIT port.";
        instance.error_shutdown(msg);
        throw std::runtime_error(msg);
    }

    while (instance.reuse_instance()) {
        // 3. Receive on all connected F_INIT ports
        std::vector<libmuscle::Message> input_messages;
        for (auto const & port : f_init_ports) {
            input_messages.push_back(instance.receive(port));
        }

        // 4. Combine the input and send on connected O_F ports
        auto timestamp = input_messages[0].timestamp();
        auto next_timestamp = input_messages[0].next_timestamp();
        Data data = Data::nils(input_messages.size());
        for (std::size_t i = 0; i < input_messages.size(); ++i) {
            Data copy;
            copy.reseat(input_messages[i].data());
            data[i] = copy;
        }
        Message output(timestamp, next_timestamp, data);

        for (auto const & port : ports[Operator::O_F]) {
            instance.send(port, output);
        }
    }

    return 0;
}
