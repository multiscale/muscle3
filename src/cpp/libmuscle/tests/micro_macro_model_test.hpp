/* Helpers for micro_model_test.cpp and macro_model_test.cpp
 *
 * These should be in a .cpp file, but then I'd have to add that to the build system
 * explicitly, so I'm inlining them in this shared header.
 */
#include <libmuscle/libmuscle.hpp>

#include <vector>


inline void check_data(libmuscle::DataConstRef const & data, bool python_compat) {
    assert(data["bool"].as<bool>());
    assert(data["char"].as<char>() == 23);
    assert(data["short int"].as<short int>() == 4097);
    assert(data["int"].as<int>() == 1234567);
    assert(data["long int"].as<long int>() == 1234568l);
    assert(data["long long int"].as<long long int>() == 6001002003);
    if (!python_compat)
        assert(data["float"].as<float>() == 1.23456f);
    assert(data["double"].as<double>() == 1.2345678901234);
    assert(data["message"].as<std::string>() == "testing");

    auto r_list = data["list"];
    assert(r_list[0].as<int>() == 1);
    assert(r_list[1].as<std::string>() == "two");
    if (!python_compat)
        assert(r_list[2].as<float>() == 3.0f);

    auto r_test_grid = data["test_grid"];
    assert(r_test_grid.is_a_grid_of<double>());
    assert(r_test_grid.shape()[0] == 2u);
    assert(r_test_grid.shape()[1] == 3u);
    if (r_test_grid.storage_order() == libmuscle::StorageOrder::last_adjacent) {
        assert(r_test_grid.elements<double>()[3] == 4.0);
    }
    else {
        assert(r_test_grid.elements<double>()[3] == 5.0);
    }
    assert(!r_test_grid.has_indexes());
}


inline libmuscle::Data make_data() {
    std::vector<double> test_array({1.0, 2.0, 3.0, 4.0, 5.0, 6.0});
    std::vector<std::size_t> test_array_shape({2u, 3u});
    return libmuscle::Data::dict(
            "bool", true,
            "char", '\027',
            "short int", static_cast<short int>(4097),
            "int", 1234567,
            "long int", 1234568l,
            "long long int", 6001002003ll,
            "float", 1.23456f,
            "double", 1.2345678901234,
            "message", std::string("testing"),
            "list", libmuscle::Data::list(1, "two", 3.0f),
            "test_grid", libmuscle::Data::grid(test_array.data(), test_array_shape));
}

