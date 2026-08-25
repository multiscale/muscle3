/* This is a part of the integration test suite, and is run from a Python
 * test in /integration_test. It is not a unit test.
 */
#include <cassert>
#include <iostream>

#include <libmuscle/libmuscle.hpp>
#include <ymmsl/ymmsl.hpp>


using libmuscle::Data;
using libmuscle::DataConstRef;
using libmuscle::Instance;
using libmuscle::Message;
using ymmsl::Operator;

// See corresponding Python actor in integration_test/test_filters
void pico(int argc, char * argv[]) {
    if (argc < 2) throw std::runtime_error("Missing filters argument");
    std::string filters = std::string(argv[1]);
    std::cout << "Running with conduit filter: '" << filters << "'" << std::endl;
    assert(filters == "pad pad" || filters == "repeat pad" || filters == "repeat repeat");

    Instance instance(argc, argv, {{Operator::F_INIT, {"macro", "meso", "micro"}}});

    int reused = 0;
    std::vector<std::vector<int>> expected_counts{
        {1, 0, 0},
        {1, 0, 1},
        {2, 0, 0},
        {2, 0, 1},
        {2, 1, 0},
        {2, 1, 1},
        {3, 0, 0},
        {3, 0, 1},
        {3, 1, 0},
        {3, 1, 1},
        {3, 2, 0},
        {3, 2, 1}
    };
    while (instance.reuse_instance()) {
        auto macro = instance.receive("macro");
        auto meso = instance.receive("meso");
        auto micro = instance.receive("micro");

        std::vector<int> message_counts{
            micro.data()[1].as<int>(),
            micro.data()[3].as<int>(),
            micro.data()[5].as<int>()};
        assert(message_counts == expected_counts[reused]);

        if (filters == "pad pad" && (message_counts[1] || message_counts[2])) {
            assert(macro.data().is_nil());
        } else if (filters == "repeat pad" && message_counts[2]) {
            assert(macro.data().is_nil());
        } else {
            assert(macro.data()[0].as<std::string>() == micro.data()[0].as<std::string>());
            assert(macro.data()[1].as<int>() == micro.data()[1].as<int>());
        }

        ++reused;
    }
    assert(reused == expected_counts.size());
}

int main(int argc, char * argv[]) {
    pico(argc, argv);
    return EXIT_SUCCESS;
}

