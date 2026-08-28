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
using libmuscle::InstanceFlags;
using libmuscle::Message;
using ymmsl::Operator;

static std::vector<std::vector<int>> expected_counts{
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

// See corresponding Python actor in integration_test/test_filters
void pico(int argc, char * argv[]) {
    std::string filters = std::string(argv[2]);
    std::cout << "Running with conduit filter: '" << filters << "'" << std::endl;
    assert(filters == "pad pad" || filters == "repeat pad" || filters == "repeat repeat");

    Instance instance(argc, argv, {{Operator::F_INIT, {"macro", "meso", "micro"}}});

    int reused = 0;
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

// See corresponding Python actor in integration_test/test_filters
void repeat_s(int argc, char * argv[]) {
    std::string filters = std::string(argv[2]);
    std::cout << "Running with conduit filter: '" << filters << "'" << std::endl;

    
    Instance instance(argc, argv, {
        {Operator::F_INIT, {"meso"}},
        {Operator::S, {"macro", "repeated_meso", "micro"}}
    });

    int micro_received = 0;
    while (instance.reuse_instance()) {
        auto meso = instance.receive("meso");

        for (int i = 0; i < 2; ++i) {
            auto macro = instance.receive("macro");
            auto repeated_meso = instance.receive("repeated_meso");
            auto micro = instance.receive("micro");

            std::vector<int> message_counts{
                micro.data()[1].as<int>(),
                micro.data()[3].as<int>(),
                micro.data()[5].as<int>()};
            assert(message_counts == expected_counts[micro_received]);

            if (filters == "pad pad" && (message_counts[1] || message_counts[2])) {
                assert(macro.data().is_nil());
            } else if (filters == "repeat pad" && message_counts[2]) {
                assert(macro.data().is_nil());
            } else {
                assert(macro.data()[0].as<std::string>() == micro.data()[0].as<std::string>());
                assert(macro.data()[1].as<int>() == micro.data()[1].as<int>());
            }

            ++micro_received;
        }
    }
    assert(micro_received == expected_counts.size());
}

// See corresponding Python actor in integration_test/test_filters
void checkpointing_A(int argc, char * argv[]) {
    Instance instance(argc, argv, 
        {{Operator::O_F, {"out"}}},
        InstanceFlags::KEEPS_NO_STATE_FOR_NEXT_USE);

    while (instance.reuse_instance())
        instance.send("out", Message(4, "xyz"));
}

// See corresponding Python actor in integration_test/test_filters
void checkpointing_B(int argc, char * argv[]) {
    Instance instance(argc, argv, 
        {{Operator::S, {"in"}}},
        InstanceFlags::USES_CHECKPOINT_API);

    while (instance.reuse_instance()) {
        double t_cur;
        if (instance.resuming())
            t_cur = instance.load_snapshot().timestamp();
        if (instance.should_init())
            t_cur = 0.0;
        
        while (t_cur < 5) {
            auto msg = instance.receive("in");
            assert(msg.data().as<std::string>() == "xyz");
            assert(msg.timestamp() == 5);
            std::cout << "Message is alright!";

            t_cur += 1.0;
            if (instance.should_save_snapshot(t_cur))
                instance.save_snapshot(Message(t_cur));
        }

        if (instance.should_save_final_snapshot())
            instance.save_final_snapshot(Message(t_cur));
    }
}


int main(int argc, char * argv[]) {
    if (argc < 3) throw std::runtime_error("Missing filters argument");
    if (argv[1] == std::string("pico"))
        pico(argc, argv);
    else if (argv[1] == std::string("repeat_s"))
        repeat_s(argc, argv);
    else if (argv[1] == std::string("checkpointing_A"))
        checkpointing_A(argc, argv);
    else if (argv[1] == std::string("checkpointing_B"))
        checkpointing_B(argc, argv);
    else
        throw std::runtime_error("Unknown program: " + std::string(argv[1]));
    return EXIT_SUCCESS;
}

