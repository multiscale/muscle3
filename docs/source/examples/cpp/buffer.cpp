#include "libmuscle/libmuscle.hpp"
#include "ymmsl/ymmsl.hpp"

#include "unistd.h"


using libmuscle::Data;
using libmuscle::Instance;
using libmuscle::Message;
using ymmsl::Operator;


int main(int argc, char * argv[]) {
    Instance instance(argc, argv, {
            {Operator::F_INIT, {"in"}},
            {Operator::O_F, {"out"}}});

    while (instance.reuse_instance()) {
        // F_INIT
        Message msg = instance.receive("in", Message(0.0, Data("Testing")));

        // S
        usleep(250000);

        // O_F
        instance.send("out", msg);
    }

    return 0;
}

