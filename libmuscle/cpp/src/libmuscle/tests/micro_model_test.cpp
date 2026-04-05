/* This is a part of the integration test suite, and is run from a Python
 * test in /integration_test. It is not a unit test.
 */
#include <libmuscle/libmuscle.hpp>
#include <ymmsl/ymmsl.hpp>

#include <algorithm>
#include <cassert>
#include <cstdint>
#include <sstream>

#include "micro_macro_model_test.hpp"

using libmuscle::Data;
using libmuscle::DataConstRef;
using libmuscle::Instance;
using libmuscle::Message;
using libmuscle::StorageOrder;
using ymmsl::Operator;


void check_settings(Instance const & instance) {
    auto settings = instance.list_settings();

    assert(settings.size() == 8);   // test1-6, test_with_a_longer_name, python_compat
    std::vector<bool> setting_seen(8, false);
    for (std::string const & setting : settings) {
        if (setting == "test1") setting_seen[0] = true;
        else if (setting == "test2") setting_seen[1] = true;
        else if (setting == "test3") setting_seen[2] = true;
        else if (setting == "test4") setting_seen[3] = true;
        else if (setting == "test5") setting_seen[4] = true;
        else if (setting == "test6") setting_seen[5] = true;
        else if (setting == "test_with_a_longer_name") setting_seen[6] = true;
        else if (setting == "python_compat") setting_seen[7] = true;
        else throw std::runtime_error("Unexpected setting name " + setting);
    }
    assert(std::all_of(
                setting_seen.begin(), setting_seen.end(), [](bool b){return b;}));

    assert(instance.get_setting("test1").is_a<int64_t>());
    assert(!instance.get_setting("test1").is_a<bool>());
    try {
        instance.get_setting("does_not_exist");
    }
    catch (std::out_of_range const & e) {}

    assert(instance.get_setting_as<int64_t>("test1") == 13);
    assert(instance.get_setting_as<bool>("test4"));

    // Test get_setting_as with default (scalar types only)
    assert(instance.get_setting_as<int64_t>("test1", 99) == 13);
    assert(instance.get_setting_as<int64_t>("does_not_exist", 99) == 99);

    assert(instance.get_setting_as<bool>("test4", false));
    assert(!instance.get_setting_as<bool>("does_not_exist", false));

    assert(instance.get_setting_as<double>("test2", 99.0) == 13.3);
    assert(instance.get_setting_as<double>("does_not_exist", 99.0) == 99.0);

    assert(instance.get_setting_as<std::string>("test3", "default") == "testing");
    assert(
            instance.get_setting_as<std::string>("does_not_exist", "default") ==
            "default");
}


int main(int argc, char *argv[]) {
    Instance instance(argc, argv, {
            {Operator::F_INIT, {"in"}},
            {Operator::O_F, {"out"}}});

    int i = 0;
    while (instance.reuse_instance()) {
        // F_INIT
        check_settings(instance);
        bool python_compat = instance.get_setting_as<bool>("python_compat");

        auto msg = instance.receive("in");
        check_data(msg.data(), python_compat);

        // O_F
        auto reply = make_data();
        instance.send("out", Message(msg.timestamp(), reply));
        ++i;
    }

    return 0;
}

