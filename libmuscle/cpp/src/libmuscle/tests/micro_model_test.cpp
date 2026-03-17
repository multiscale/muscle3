/* This is a part of the integration test suite, and is run from a Python
 * test in /integration_test. It is not a unit test.
 */
#include <libmuscle/libmuscle.hpp>
#include <ymmsl/ymmsl.hpp>

#include <algorithm>
#include <cassert>
#include <cstdint>
#include <sstream>


using libmuscle::Data;
using libmuscle::Instance;
using libmuscle::Message;
using libmuscle::StorageOrder;
using ymmsl::Operator;


void check_settings(Instance const & instance) {
    auto settings = instance.list_settings();

    assert(settings.size() == 7);   // test1-6, test_with_a_longer_name
    std::vector<bool> setting_seen(7, false);
    for (std::string const & setting : settings) {
        if (setting == "test1") setting_seen[0] = true;
        else if (setting == "test2") setting_seen[1] = true;
        else if (setting == "test3") setting_seen[2] = true;
        else if (setting == "test4") setting_seen[3] = true;
        else if (setting == "test5") setting_seen[4] = true;
        else if (setting == "test6") setting_seen[5] = true;
        else if (setting == "test_with_a_longer_name") setting_seen[6] = true;
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

        auto msg = instance.receive("in");
        assert(msg.data()["message"].as<std::string>() == "testing");
        auto r_test_grid = msg.data()["test_grid"];
        assert(r_test_grid.is_a_grid_of<double>());
        assert(r_test_grid.shape()[0] == 2u);
        assert(r_test_grid.shape()[1] == 3u);
        assert(r_test_grid.storage_order() == StorageOrder::last_adjacent);
        assert(r_test_grid.elements<double>()[3] == 4.0);
        assert(!r_test_grid.has_indexes());

        // O_F
        std::ostringstream reply;
        reply << "testing back " << i;

        std::vector<std::int64_t> s_test_grid_data({1, 2, 3, 4, 5, 6});
        Data s_test_grid = Data::grid<std::int64_t>(
                s_test_grid_data.data(), {2, 3}, {"x", "y"});

        Data reply_dict = Data::dict(
                "reply", reply.str(),
                "test_grid", s_test_grid);
        instance.send("out", Message(msg.timestamp(), reply_dict));
        ++i;
    }

    return 0;
}

