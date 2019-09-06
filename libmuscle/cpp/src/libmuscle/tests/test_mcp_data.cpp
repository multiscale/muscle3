#include "libmuscle/mcp/data.hpp"
#include "libmuscle/mcp/data_pack.hpp"

#include "ymmsl/settings.hpp"

#include <cstdint>
#include <string>

#include <gtest/gtest.h>
#include <msgpack.hpp>


using libmuscle::mcp::Data;
using libmuscle::mcp::DataConstRef;
using ymmsl::ParameterValue;
using ymmsl::Settings;


int main(int argc, char *argv[]) {
    ::testing::InitGoogleTest(&argc, argv);
    return RUN_ALL_TESTS();
}

TEST(libmuscle_mcp_data, nil_value) {
    Data d;
    ASSERT_TRUE(d.is_nil());
    ASSERT_FALSE(d.is_a_list());

    msgpack::sbuffer buf;
    msgpack::pack(buf, d);

    auto zone = std::make_shared<msgpack::zone>();
    Data d2(libmuscle::mcp::unpack_data(zone, buf.data(), buf.size()));
    ASSERT_TRUE(d.is_nil());
    ASSERT_FALSE(d.is_a<int>());
}

template <typename T, typename U>
void test2(U const & test_value) {
    Data d(test_value);
    ASSERT_TRUE(d.is_a<T>());

    msgpack::sbuffer buf;
    msgpack::pack(buf, d);

    auto zone = std::make_shared<msgpack::zone>();
    Data d2(libmuscle::mcp::unpack_data(zone, buf.data(), buf.size()));
    ASSERT_TRUE(d2.is_a<T>());
    T x = d2.as<T>();
    ASSERT_EQ(x, test_value);
}

template <typename T>
void test(T const & test_value) {
    test2<T, T>(test_value);
}

TEST(libmuscle_mcp_data, bool_value) {
    test<bool>(false);
    test<bool>(true);
}

TEST(libmuscle_mcp_data, char_value) {
    test<char>(-13);
    test<char>(0);
    test<char>(42);
}

TEST(libmuscle_mcp_data, short_int_value) {
    test<short int>(-13);
    test<short int>(0);
    test<short int>(4242);
}

TEST(libmuscle_mcp_data, int_value) {
    test<int>(-13);
    test<int>(0);
    test<int>(42424242);
}

TEST(libmuscle_mcp_data, long_int_value) {
    test<long int>(-13);
    test<long int>(0);
    test<long int>(42424242l);
}

TEST(libmuscle_mcp_data, long_long_int_value) {
    test<long long int>(-13);
    test<long long int>(0);
    test<long long int>(4242424242424242ll);
}

TEST(libmuscle_mcp_data, unsigned_char_value) {
    test<unsigned char>(0);
    test<unsigned char>(42);
}

TEST(libmuscle_mcp_data, unsigned_short_int_value) {
    test<unsigned short int>(0);
    test<unsigned short int>(4242);
}

TEST(libmuscle_mcp_data, unsigned_int_value) {
    test<unsigned int>(0);
    test<unsigned int>(42424242);
}

TEST(libmuscle_mcp_data, unsigned_long_int_value) {
    test<unsigned long int>(0);
    test<unsigned long int>(42424242l);
}

TEST(libmuscle_mcp_data, unsigned_long_long_int_value) {
    test<unsigned long long int>(0);
    test<unsigned long long int>(4242424242424242ll);
}

TEST(libmuscle_mcp_data, float_value) {
    test<float>(0.0f);
    test<float>(424242.42f);
}

TEST(libmuscle_mcp_data, double_value) {
    test<double>(0.0);
    test<double>(424242.42);
}

TEST(libmuscle_mcp_data, string_value) {
    test2<std::string, char const *>("");
    test2<std::string, char const *>("Testing");

    test<std::string>(std::string(""));
    test<std::string>(std::string("Testing"));
}

TEST(libmuscle_mcp_data, dict) {
    Data d(Data::dict(
            "test_double", 13.3,
            "test_int", 42
            ));
    ASSERT_TRUE(d.is_a_dict());
    ASSERT_EQ(d.size(), 2);

    msgpack::sbuffer buf;
    msgpack::pack(buf, d);

    auto zone = std::make_shared<msgpack::zone>();
    Data d2(libmuscle::mcp::unpack_data(zone, buf.data(), buf.size()));
    ASSERT_TRUE(d2.is_a_dict());
    ASSERT_EQ(d2.size(), 2);

    double x = d2["test_double"].as<double>();
    ASSERT_EQ(x, 13.3);
    int i = d2["test_int"].as<int>();
    ASSERT_EQ(i, 42);

    ASSERT_TRUE(d2.key(0u).as<std::string>() == "test_double" ||
                d2.key(1u).as<std::string>() == "test_double");

    ASSERT_TRUE(d2.key(0u).as<std::string>() == "test_int" ||
                d2.key(1u).as<std::string>() == "test_int");

    ASSERT_TRUE(d2.value(0u).is_a<double>() || d2.value(1u).is_a<double>());
    ASSERT_TRUE(d2.value(0u).is_a<int>() || d2.value(1u).is_a<int>());

    ASSERT_TRUE((d2.key(0u).as<std::string>() == "test_double" && d2.value(0u).is_a<double>()) ||
                (d2.key(1u).as<std::string>() == "test_double" && d2.value(1u).is_a<double>()));
}

TEST(libmuscle_mcp_data, dict_errors) {
    DataConstRef dcr(10);
    ASSERT_THROW(dcr["test_not_a_map"], std::runtime_error);

    DataConstRef dcr_dict(Data::dict("test_int", 10.3));
    ASSERT_THROW(dcr_dict["test_nonexistent"], std::out_of_range);

    Data d(10);
    ASSERT_THROW(d["test_not_a_map"], std::runtime_error);
}


TEST(libmuscle_mcp_data, dict_dict) {
    Data d(Data::dict(
            "test3", Data::dict("test1", true, "test2", 87),
            "test4", 12.34
            ));
    ASSERT_TRUE(d.is_a_dict());
    ASSERT_TRUE(d["test3"].is_a_dict());
    ASSERT_TRUE(d["test3"]["test2"].is_a<int>());
    ASSERT_EQ(d["test3"]["test2"].as<int>(), 87);
    ASSERT_TRUE(d["test4"].is_a<double>());
    ASSERT_EQ(d["test4"].as<double>(), 12.34);

    msgpack::sbuffer buf;
    msgpack::pack(buf, d);

    ASSERT_TRUE(d.is_a_dict());
    ASSERT_TRUE(d["test3"].is_a_dict());
    ASSERT_TRUE(d["test3"]["test2"].is_a<int>());
    ASSERT_EQ(d["test3"]["test2"].as<int>(), 87);
    ASSERT_TRUE(d["test4"].is_a<double>());
    ASSERT_EQ(d["test4"].as<double>(), 12.34);

    auto zone = std::make_shared<msgpack::zone>();
    Data d2(libmuscle::mcp::unpack_data(zone, buf.data(), buf.size()));

    ASSERT_TRUE(d2.is_a_dict());
    ASSERT_TRUE(d2["test3"].is_a_dict());
    ASSERT_TRUE(d2["test3"]["test2"].is_a<int>());
    ASSERT_EQ(d2["test3"]["test2"].as<int>(), 87);
    ASSERT_TRUE(d2["test4"].is_a<double>());
    ASSERT_EQ(d2["test4"].as<double>(), 12.34);
}


TEST(libmuscle_mcp_data, dict_build) {
    Data dict = Data::dict("test1", true, "test2", 54);
    ASSERT_TRUE(dict["test1"].is_a<bool>());
    ASSERT_EQ(dict["test1"].as<bool>(), true);

    dict["test1"] = 123.0;
    ASSERT_TRUE(dict["test1"].is_a<double>());
    ASSERT_EQ(dict["test1"].as<double>(), 123.0);

    ASSERT_TRUE(dict["test3"].is_nil());
    dict["test4"] = static_cast<short int>(23);
    ASSERT_TRUE(dict["test4"].is_a<short int>());
    ASSERT_EQ(dict["test4"].as<short int>(), 23);

    msgpack::sbuffer buf;
    msgpack::pack(buf, dict);

    auto zone = std::make_shared<msgpack::zone>();
    Data data(libmuscle::mcp::unpack_data(zone, buf.data(), buf.size()));
    ASSERT_TRUE(data.is_a_dict());
    ASSERT_EQ(data.size(), 4);
    ASSERT_TRUE(data["test1"].is_a<double>());
    ASSERT_EQ(data["test1"].as<double>(), 123.0);
    ASSERT_TRUE(data["test2"].is_a<int>());
    ASSERT_EQ(data["test2"].as<int>(), 54);
    ASSERT_TRUE(data["test4"].is_a<int>());
    ASSERT_EQ(data["test4"].as<int>(), 23);
}


TEST(libmuscle_mcp_data, dict_dataconstref) {
    // regression test
    Data dict = Data::dict("test", DataConstRef());
    dict = Data::dict("test", Data());
}


TEST(libmuscle_mcp_data, list) {
    Data d(Data::list("test_string", 12, 1.0));

    msgpack::sbuffer buf;
    msgpack::pack(buf, d);
    auto zone = std::make_shared<msgpack::zone>();
    Data data(libmuscle::mcp::unpack_data(zone, buf.data(), buf.size()));

    ASSERT_TRUE(data.is_a_list());
    ASSERT_EQ(data.size(), 3);
    ASSERT_TRUE(data[0].is_a<std::string>());
    std::string s = data[0].as<std::string>();
    ASSERT_EQ(s, "test_string");

    ASSERT_TRUE(data[1].is_a<int>());
    int i = data[1].as<int>();
    ASSERT_EQ(i, 12);

    ASSERT_TRUE(data[2].is_a<double>());
    double d2 = data[2].as<double>();
    ASSERT_EQ(d2, 1.0);

    ASSERT_THROW(data[3], std::out_of_range);
}

TEST(libmuscle_mcp_data, list_errors) {
    DataConstRef dcr(10);
    ASSERT_THROW(dcr[0], std::runtime_error);

    DataConstRef dcr_list(Data::list("test_string", 10.3));
    ASSERT_THROW(dcr_list[2], std::out_of_range);

    Data d(10);
    ASSERT_THROW(d[0], std::runtime_error);

    Data list(Data::list("test_string", 10.3));
    ASSERT_THROW(list[2], std::out_of_range);
}

TEST(libmuscle_mcp_data, list_build) {
    Data l0 = Data::nils(1u);
    ASSERT_TRUE(l0.is_a_list());
    ASSERT_EQ(l0.size(), 1u);
    ASSERT_TRUE(l0[0].is_nil());

    Data l1 = Data::nils(1);
    ASSERT_TRUE(l1.is_a_list());
    ASSERT_EQ(l1.size(), 1);
    ASSERT_TRUE(l1[0].is_nil());

    Data list = Data::nils(3u);

    list[0] = 12;
    list[1] = "test_string";
    list[2] = 1.0;

    msgpack::sbuffer buf;
    msgpack::pack(buf, list);
    auto zone = std::make_shared<msgpack::zone>();
    Data data(libmuscle::mcp::unpack_data(zone, buf.data(), buf.size()));

    ASSERT_TRUE(data.is_a_list());
    ASSERT_EQ(data.size(), 3);

    ASSERT_TRUE(data[0].is_a<int>());
    int i = data[0].as<int>();
    ASSERT_EQ(i, 12);

    ASSERT_TRUE(data[1].is_a<std::string>());
    std::string s = data[1].as<std::string>();
    ASSERT_EQ(s, "test_string");

    ASSERT_TRUE(data[2].is_a<double>());
    double d = data[2].as<double>();
    ASSERT_EQ(d, 1.0);
}

TEST(libmuscle_mcp_data, list_dict) {
    auto dict = Data::dict("test1", "test", "test2", 87);

    msgpack::sbuffer buf;
    msgpack::pack(buf, Data::list(1, 2.0, dict));
    auto zone = std::make_shared<msgpack::zone>();
    auto data = libmuscle::mcp::unpack_data(zone, buf.data(), buf.size());

    ASSERT_TRUE(data.is_a_list());
    ASSERT_EQ(data.size(), 3);
    ASSERT_TRUE(data[0].is_a<int>());
    ASSERT_EQ(data[0].as<int>(), 1);
    ASSERT_TRUE(data[1].is_a<double>());
    ASSERT_EQ(data[1].as<double>(), 2.0);
    ASSERT_TRUE(data[2].is_a_dict());
    ASSERT_EQ(data[2].size(), 2);
    ASSERT_TRUE(data[2]["test1"].is_a<std::string>());
    ASSERT_EQ(data[2]["test1"].as<std::string>(), "test");
    ASSERT_TRUE(data[2]["test2"].is_a<int>());
    ASSERT_EQ(data[2]["test2"].as<int>(), 87);
}

TEST(libmuscle_mcp_data, list_dataconstref) {
    // regression test
    Data dict = Data::list(DataConstRef());
    dict = Data::list(Data());
}


template <typename T>
void test_parameter_value(ParameterValue const & test_value) {
    Data d(test_value);
    ASSERT_TRUE(d.is_a<T>());

    msgpack::sbuffer buf;
    msgpack::pack(buf, d);

    auto zone = std::make_shared<msgpack::zone>();
    Data d2(libmuscle::mcp::unpack_data(zone, buf.data(), buf.size()));
    ASSERT_TRUE(d2.is_a<T>());
    T x = d2.as<T>();
    ASSERT_EQ(x, test_value.get<T>());
}

TEST(libmuscle_mcp_data, parameter_value) {
    test_parameter_value<int64_t>(ymmsl::ParameterValue(13));
    test_parameter_value<std::string>(ymmsl::ParameterValue("test"));

    test<ymmsl::ParameterValue>(ymmsl::ParameterValue(13));
}

TEST(libmuscle_mcp_data, parameter_value_list) {
    ParameterValue pv(std::vector<double>{1.0, 2.2, 3.1415});
    Data d(pv);
    ASSERT_TRUE(d.is_a_list());
    ASSERT_EQ(d.size(), 3u);
    ASSERT_EQ(d[0].as<double>(), 1.0);
    ASSERT_EQ(d[1].as<double>(), 2.2);
    ASSERT_EQ(d[2].as<double>(), 3.1415);

    msgpack::sbuffer buf;
    msgpack::pack(buf, d);

    auto zone = std::make_shared<msgpack::zone>();
    Data d2(libmuscle::mcp::unpack_data(zone, buf.data(), buf.size()));
    ASSERT_TRUE(d.is_a_list());
    ASSERT_EQ(d2.size(), 3u);
    ASSERT_EQ(d2[0].as<double>(), 1.0);
    ASSERT_EQ(d2[1].as<double>(), 2.2);
    ASSERT_EQ(d2[2].as<double>(), 3.1415);
}

TEST(libmuscle_mcp_data, parameter_value_list_list) {
    ParameterValue pv(std::vector<std::vector<double>>{
            {1.0, 2.2, 3.1415}, {4.5}});
    Data d(pv);
    ASSERT_TRUE(d.is_a_list());
    ASSERT_EQ(d.size(), 2u);

    ASSERT_TRUE(d[0].is_a_list());
    ASSERT_EQ(d[0].size(), 3u);
    ASSERT_TRUE(d[1].is_a_list());
    ASSERT_EQ(d[1].size(), 1u);

    ASSERT_EQ(d[0][0].as<double>(), 1.0);
    ASSERT_EQ(d[0][1].as<double>(), 2.2);
    ASSERT_EQ(d[0][2].as<double>(), 3.1415);
    ASSERT_EQ(d[1][0].as<double>(), 4.5);

    msgpack::sbuffer buf;
    msgpack::pack(buf, d);

    auto zone = std::make_shared<msgpack::zone>();
    Data d2(libmuscle::mcp::unpack_data(zone, buf.data(), buf.size()));
    ASSERT_TRUE(d2.is_a_list());
    ASSERT_EQ(d2.size(), 2u);

    ASSERT_TRUE(d2[0].is_a_list());
    ASSERT_EQ(d2[0].size(), 3u);
    ASSERT_TRUE(d2[1].is_a_list());
    ASSERT_EQ(d2[1].size(), 1u);

    ASSERT_EQ(d2[0][0].as<double>(), 1.0);
    ASSERT_EQ(d2[0][1].as<double>(), 2.2);
    ASSERT_EQ(d2[0][2].as<double>(), 3.1415);
    ASSERT_EQ(d2[1][0].as<double>(), 4.5);
}

TEST(libmuscle_mcp_data, parameter_value_list_pv) {
    ParameterValue pv(std::vector<double>{1.0, 2.2, 3.1415});
    Data d(pv);

    ASSERT_TRUE(d.is_a<ParameterValue>());
    ParameterValue pv2 = d.as<ParameterValue>();

    auto vec = pv2.get<std::vector<double>>();
    ASSERT_EQ(vec.size(), 3);
    ASSERT_EQ(vec[0], 1.0);
    ASSERT_EQ(vec[1], 2.2);
    ASSERT_EQ(vec[2], 3.1415);
}

TEST(libmuscle_mcp_data, parameter_value_list_list_pv) {
    ParameterValue pv(std::vector<std::vector<double>>{{1.0, 2.2, 3.1415}, {4.5}});
    Data d(pv);

    ASSERT_TRUE(d.is_a<ParameterValue>());
    ParameterValue pv2 = d.as<ParameterValue>();

    auto vec = pv2.get<std::vector<std::vector<double>>>();
    ASSERT_EQ(vec.size(), 2);
    ASSERT_EQ(vec[0].size(), 3);
    ASSERT_EQ(vec[0][0], 1.0);
    ASSERT_EQ(vec[0][1], 2.2);
    ASSERT_EQ(vec[0][2], 3.1415);
    ASSERT_EQ(vec[1].size(), 1);
    ASSERT_EQ(vec[1][0], 4.5);
}

TEST(libmuscle_mcp_data, settings) {
    Settings settings;
    settings["setting1"] = 1;
    settings["setting2"] = true;
    settings["setting3"] = "testing";

    Data d(settings);
    ASSERT_TRUE(d.is_a<Settings>());

    msgpack::sbuffer buf;
    msgpack::pack(buf, d);

    auto zone = std::make_shared<msgpack::zone>();
    Data d2(libmuscle::mcp::unpack_data(zone, buf.data(), buf.size()));
    ASSERT_TRUE(d2.is_a<Settings>());
    Settings x = d2.as<Settings>();
    ASSERT_EQ(x["setting1"], 1);
    ASSERT_EQ(x["setting2"], true);
    ASSERT_EQ(x["setting3"], "testing");
}


TEST(libmuscle_mcp_data, byte_array) {
    std::string test_data("Test data");

    auto bytes = Data::byte_array(test_data.data(), test_data.size());

    msgpack::sbuffer buf;
    msgpack::pack(buf, bytes);
    auto zone = std::make_shared<msgpack::zone>();
    auto data = libmuscle::mcp::unpack_data(zone, buf.data(), buf.size());

    ASSERT_TRUE(data.is_a_byte_array());
    ASSERT_EQ(data.size(), test_data.size());
    for (std::size_t i = 0u; i < data.size(); ++i)
        ASSERT_EQ(data.as_byte_array()[i], test_data[i]);
}


TEST(libmuscle_mcp_data, as_wrong_type) {
    Data d(42);

    ASSERT_THROW(d.as<float>(), std::runtime_error);
}

