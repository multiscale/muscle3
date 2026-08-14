/* This is a part of the integration test suite, and is run from a Python
 * test in /integration_test. It is not a unit test.
 *
 * This is a collection of actors used in test_snapshot_macro_micro.py
 */
#include <cassert>
#include <iostream>
#include <string>

#include <libmuscle/libmuscle.hpp>
#include <ymmsl/ymmsl.hpp>

using namespace std::string_literals;

using libmuscle::Data;
using libmuscle::DataConstRef;
using libmuscle::Instance;
using libmuscle::InstanceFlags;
using libmuscle::Message;
using ymmsl::Operator;


/** A simple snapshotting macro component used in
 * integration_tests/test_snapshot_macro_micro.py
 */
void macro(int argc, char * argv[]) {
    Instance instance(
            argc, argv, {
                {Operator::O_I, {"o_i"}},
                {Operator::S, {"s"}}},
            InstanceFlags::USES_CHECKPOINT_API);

    while (instance.reuse_instance()) {
        double dt = instance.get_setting_as<double>("dt");
        double t_max = instance.get_setting_as<double>("t_max");
        double t_cur;
        int i;

        if (instance.resuming()) {
            auto msg = instance.load_snapshot();
            // load state from message
            t_cur = msg.timestamp();
            i = msg.data().as<int>();
            assert(i >= 1);
        }

        if (instance.should_init()) {
            t_cur = instance.get_setting_as<double>("t0");
            i = 0;
        }

        while (t_cur + dt <= t_max) {
            Message msg(t_cur, i);
            double t_next = t_cur + dt;
            if (t_next + dt <= t_max)
                msg.set_next_timestamp(t_next);
            instance.send("o_i", msg);

            msg = instance.receive("s");
            assert(msg.data().as<int>() == i);

            i ++;
            t_cur += dt;

            if (instance.should_save_snapshot(t_cur))
                instance.save_snapshot(Message(t_cur, i));
        }

        if (instance.should_save_final_snapshot())
            instance.save_final_snapshot(Message(t_cur, i));
    }
}


void macro_vector(int argc, char * argv[]) {
    Instance instance(
            argc, argv, {
                {Operator::O_I, {"o_i[]"}},
                {Operator::S, {"s[]"}}},
            InstanceFlags::USES_CHECKPOINT_API);

    while (instance.reuse_instance()) {
        double dt = instance.get_setting_as<double>("dt");
        double t_max = instance.get_setting_as<double>("t_max");
        double t_cur;
        int i;

        if (instance.resuming()) {
            auto msg = instance.load_snapshot();
            // load state from message
            t_cur = msg.timestamp();
            i = msg.data().as<int>();
            assert(i >= 1);
        }

        if (instance.should_init()) {
            t_cur = instance.get_setting_as<double>("t0");
            i = 0;
        }

        while (t_cur + dt <= t_max) {
            Message msg(t_cur, i);
            double t_next = t_cur + dt;
            if (t_next + dt <= t_max)
                msg.set_next_timestamp(t_next);
            for (int slot = 0; slot < instance.get_port_length("o_i"); ++slot)
                instance.send("o_i", msg, slot);

            for (int slot = 0; slot < instance.get_port_length("s"); ++slot) {
                msg = instance.receive("s", slot);
                assert(msg.data().as<int>() == i);
            }

            i ++;
            t_cur += dt;

            if (instance.should_save_snapshot(t_cur))
                instance.save_snapshot(Message(t_cur, i));
        }

        if (instance.should_save_final_snapshot())
            instance.save_final_snapshot(Message(t_cur, i));
    }
}


void micro(int argc, char * argv[]) {
    Instance instance(
            argc, argv, {
                {Operator::F_INIT, {"f_i"}},
                {Operator::O_F, {"o_f"}}},
            InstanceFlags::USES_CHECKPOINT_API);

    while (instance.reuse_instance()) {
        double dt = instance.get_setting_as<double>("dt");
        double t_max = instance.get_setting_as<double>("t_max");
        double t_cur, t_stop;
        int i;

        if (instance.resuming()) {
            auto msg = instance.load_snapshot();
            // load state from message
            t_cur = msg.timestamp();
            i = msg.data()[0].as<int>();
            t_stop = msg.data()[1].as<double>();
        }

        if (instance.should_init()) {
            auto msg = instance.receive("f_i");
            t_cur = msg.timestamp();
            i = msg.data().as<int>();
            t_stop = t_cur + t_max;
        }

        while (t_cur <= t_stop) {
            // faux time-integration for testing snapshots
            t_cur += dt;

            if (instance.should_save_snapshot(t_cur))
                instance.save_snapshot(Message(t_cur, Data::list(i, t_stop)));
        }

        instance.send("o_f", Message(t_cur, i));

        if (instance.should_save_final_snapshot())
            instance.save_final_snapshot(Message(t_cur, Data::list(i, t_stop)));
    }
}


void stateless_micro(int argc, char * argv[]) {
    Instance instance(
            argc, argv, {
                {Operator::F_INIT, {"f_i"}},
                {Operator::O_F, {"o_f"}}},
            InstanceFlags::KEEPS_NO_STATE_FOR_NEXT_USE);

    while (instance.reuse_instance()) {
        double dt = instance.get_setting_as<double>("dt");
        double t_max = instance.get_setting_as<double>("t_max");

        auto msg = instance.receive("f_i");
        auto t_cur = msg.timestamp();
        auto i = msg.data().as<int>();
        auto t_stop = t_cur + t_max;

        while (t_cur <= t_stop) {
            // faux time-integration for testing snapshots
            t_cur += dt;
        }

        instance.send("o_f", Message(t_cur, i));
    }
}


int main(int argc, char * argv[]) {
    if (argc > 1) {
        if (argv[1] == "macro"s) {
            macro(argc, argv);
            return EXIT_SUCCESS;
        } else if (argv[1] == "macro_vector"s) {
            macro_vector(argc, argv);
            return EXIT_SUCCESS;
        } else if (argv[1] == "micro"s) {
            micro(argc, argv);
            return EXIT_SUCCESS;
        } else if (argv[1] == "stateless_micro"s) {
            stateless_micro(argc, argv);
            return EXIT_SUCCESS;
        }
        std::cerr << "Unknown component name: " << argv[1] << std::endl;
    } else {
        std::cerr << "No component name provided." << std::endl;
    }
    std::cerr << "Valid component names are: macro, macro_vector, micro";
    std::cerr << " and stateless_micro" << std::endl;
    return EXIT_FAILURE;
}

