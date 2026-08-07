/* This is a part of the integration test suite, and is run from a Python
 * test in /integration_test. It is not a unit test.
 */
#include <libmuscle/libmuscle.hpp>
#include <ymmsl/ymmsl.hpp>

#include <algorithm>
#include <cassert>
#include <cstdint>
#include <iostream>

#include "micro_macro_model_test.hpp"

using libmuscle::Data;
using libmuscle::DataConstRef;
using libmuscle::Instance;
using libmuscle::Message;
using libmuscle::StorageOrder;
using ymmsl::Operator;


int main(int argc, char *argv[]) {
    Instance instance(argc, argv, {
            {Operator::O_I, {"out"}},
            {Operator::S, {"in"}}});

    while (instance.reuse_instance()) {
        bool python_compat = instance.get_setting_as<bool>("python_compat");

        for (int i = 0; i < 2; ++i) {
            // O_I
            std::cout << "O_I " << i << std::endl;
            auto data = make_data();
            std::cout << "Sending... " << i << std::endl;
            instance.send("out", Message(i * 10.0, (i + 1) * 10.0, data));
            std::cout << "Sent " << i << std::endl;

            // S
            std::cout << "Receiving... " << i << std::endl;
            auto msg = instance.receive("in");
            std::cout << "Received " << i << std::endl;
            check_data(msg.data(), python_compat);
        }
    }

    return 0;
}

