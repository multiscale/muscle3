/* This is a part of the integration test suite, and is run from a Python
 * test in /integration_test. It is not a unit test.
 */
#include <libmuscle/libmuscle.hpp>
#include <ymmsl/ymmsl.hpp>

#include <cassert>
#include <sstream>


using libmuscle::Data;
using libmuscle::Instance;
using libmuscle::Message;
using libmuscle::StorageOrder;
using ymmsl::Operator;


int main(int argc, char *argv[]) {
    Instance instance(argc, argv, {
            {Operator::F_INIT, {"in"}},
            {Operator::O_F, {"out"}}});

    int i = 0;
    while (instance.reuse_instance()) {
        // F_INIT
        assert(instance.get_setting_as<int64_t>("test1") == 13);
        assert(instance.get_setting_as<bool>("test4") == true);

        auto msg = instance.receive("in");
        assert(msg.data()["message"].as<std::string>() == "testing");
        auto r_test_grid = msg.data()["test_grid"];
        assert(r_test_grid.is_a_grid_of<double>());
        assert(r_test_grid.grid_shape()[0] == 2u);
        assert(r_test_grid.grid_shape()[1] == 3u);
        assert(r_test_grid.grid_storage_order() == StorageOrder::last_adjacent);
        assert(r_test_grid.grid_data<double>()[3] == 4.0);
        assert(!r_test_grid.grid_has_indexes());

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

