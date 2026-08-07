/* This is a part of the integration test suite, and is run from a Python
 * test in /integration_test. It is not a unit test.
 */
#include <cassert>

#include <libmuscle/libmuscle.hpp>
#include <ymmsl/ymmsl.hpp>


using libmuscle::Data;
using libmuscle::DataConstRef;
using libmuscle::Instance;
using libmuscle::Message;
using ymmsl::Operator;


/** A simple dummy component for testing.
 */
void component(int argc, char * argv[]) {
    Instance instance(argc, argv, {
            {Operator::F_INIT, {"init"}},       // int
            {Operator::O_I, {"out"}},           // int
            {Operator::S, {"in"}},              // int
            {Operator::O_F, {"result"}}});      // int

    while (instance.reuse_instance()) {
        // F_INIT
        Message default_init_msg(0.0, Data(0));
        auto init_msg = instance.receive("init", default_init_msg);

        for (int i = 0; i < 10; ++i) {
            // O_I
            Message out_msg(static_cast<double>(i), Data(i));
            instance.send("out", out_msg);

            // S
            auto in_msg = instance.receive("in", out_msg);
            assert(in_msg.data().as<int>() == i);
        }

        // O_F
        instance.send("result", init_msg);
    }
}


int main(int argc, char * argv[]) {
    component(argc, argv);
    return EXIT_SUCCESS;
}

