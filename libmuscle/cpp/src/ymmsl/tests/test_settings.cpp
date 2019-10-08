#include <cinttypes>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

#include <gtest/gtest.h>

#include <ymmsl/settings.hpp>


using std::vector;
using Vec2 = vector<vector<double>>;

using ymmsl::impl::SettingValue;
using ymmsl::impl::Settings;


TEST(ymmsl_settings, test_create_setting_value) {
    SettingValue v1("testing");
    SettingValue v2(42l);
    SettingValue v3(12.34);
    SettingValue v4(true);
    SettingValue v5({12.34, 56.78});
    SettingValue v6({{12.34, 0.0}, {56.78, 0.0}});

    ASSERT_EQ(v1.as<std::string>(), "testing");
    ASSERT_EQ(v2.as<int64_t>(), 42l);
    ASSERT_EQ(v3.as<double>(), 12.34);
    ASSERT_EQ(v4.as<bool>(), true);
    ASSERT_TRUE(v5.is_a<vector<double>>());
    ASSERT_EQ(v5.as<vector<double>>(), vector<double>({12.34, 56.78}));
    Vec2 v6_ref;
    v6_ref.push_back(vector<double>{12.34, 0.0});
    v6_ref.push_back(vector<double>{56.78, 0.0});
    ASSERT_TRUE(v6.is_a<Vec2>());
    ASSERT_EQ(v6.as<Vec2>(), v6_ref);
}

TEST(ymmsl_settings, test_copy_setting_value) {
    SettingValue v1("testing");
    SettingValue v2(v1);
    ASSERT_EQ(v2.as<std::string>(), "testing");

    SettingValue v3(42l);
    SettingValue v4(v3);
    ASSERT_EQ(v4.as<int64_t>(), 42l);

    SettingValue v5(42.13);
    SettingValue v6(v5);
    ASSERT_EQ(v6.as<double>(), 42.13);

    SettingValue v7(false);
    SettingValue v8(v7);
    ASSERT_EQ(v8.as<bool>(), false);

    SettingValue v9(vector<double>({1.2, 8.9}));
    SettingValue v10(v9);
    ASSERT_EQ(v10.as<vector<double>>(), vector<double>({1.2, 8.9}));

    SettingValue v11(Vec2({{1.2, 8.9}, {2.3, 6.7}}));
    SettingValue v12(v11);
    ASSERT_EQ(v12.as<Vec2>(), Vec2({{1.2, 8.9}, {2.3, 6.7}}));
}

TEST(ymmsl_settings, test_move_setting_value) {
    SettingValue v1("testing");
    SettingValue v2(std::move(v1));
    ASSERT_EQ(v2.as<std::string>(), "testing");
    ASSERT_FALSE(v1.is_a<std::string>());

    SettingValue v3(42l);
    SettingValue v4(std::move(v3));
    ASSERT_EQ(v4.as<int64_t>(), 42);
    ASSERT_FALSE(v3.is_a<int64_t>());

    SettingValue v5(42.13);
    SettingValue v6(std::move(v5));
    ASSERT_EQ(v6.as<double>(), 42.13);
    ASSERT_FALSE(v5.is_a<double>());

    SettingValue v7(true);
    SettingValue v8(std::move(v7));
    ASSERT_EQ(v8.as<bool>(), true);
    ASSERT_FALSE(v7.is_a<bool>());

    SettingValue v9({3.14, 2.71});
    SettingValue v10(std::move(v9));
    ASSERT_EQ(v10.as<vector<double>>()[0], 3.14);
    ASSERT_FALSE(v9.is_a<vector<double>>());

    SettingValue v11({{3.14, 2.71}});
    SettingValue v12(std::move(v11));
    ASSERT_EQ(v12.as<Vec2>()[0][1], 2.71);
    ASSERT_FALSE(v11.is_a<Vec2>());
}

TEST(ymmsl_settings, test_copy_assign_setting_value) {
    SettingValue v1("testing");
    SettingValue v2;
    v2 = v1;
    ASSERT_TRUE(v1.is_a<std::string>());
    ASSERT_TRUE(v2.is_a<std::string>());
    ASSERT_EQ(v1.as<std::string>(), "testing");
    ASSERT_EQ(v2.as<std::string>(), "testing");

    SettingValue v3(13l);
    v2 = v3;
    ASSERT_TRUE(v3.is_a<int64_t>());
    ASSERT_TRUE(v2.is_a<int64_t>());
    ASSERT_EQ(v3.as<int64_t>(), 13l);
    ASSERT_EQ(v2.as<int64_t>(), 13l);

    SettingValue v4(13.1);
    v2 = v4;
    ASSERT_TRUE(v4.is_a<double>());
    ASSERT_TRUE(v2.is_a<double>());
    ASSERT_EQ(v4.as<double>(), 13.1);
    ASSERT_EQ(v2.as<double>(), 13.1);

    SettingValue v5(false);
    v2 = v5;
    ASSERT_TRUE(v5.is_a<bool>());
    ASSERT_TRUE(v2.is_a<bool>());
    ASSERT_EQ(v5.as<bool>(), false);
    ASSERT_EQ(v2.as<bool>(), false);

    SettingValue v6({1.2});
    v2 = v6;
    ASSERT_TRUE(v6.is_a<vector<double>>());
    ASSERT_TRUE(v2.is_a<vector<double>>());
    ASSERT_EQ(v6.as<vector<double>>().size(), 1u);
    ASSERT_EQ(v2.as<vector<double>>()[0], 1.2);

    SettingValue v7({{1.2, 1}, {4, 3}});
    v2 = v7;
    ASSERT_TRUE(v7.is_a<Vec2>());
    ASSERT_TRUE(v2.is_a<Vec2>());
    ASSERT_EQ(v7.as<Vec2>().size(), 2u);
    ASSERT_EQ(v2.as<Vec2>()[0][0], 1.2);
    ASSERT_EQ(v2.as<Vec2>()[1][1], 3.0);
}

TEST(ymmsl_settings, test_move_assign_setting_value) {
    SettingValue v1("testing");
    SettingValue v2;
    v2 = std::move(v1);
    ASSERT_FALSE(v1.is_a<std::string>());
    ASSERT_TRUE(v2.is_a<std::string>());
    ASSERT_EQ(v2.as<std::string>(), "testing");

    SettingValue v3(13l);
    v2 = std::move(v3);
    ASSERT_FALSE(v3.is_a<int64_t>());
    ASSERT_TRUE(v2.is_a<int64_t>());
    ASSERT_EQ(v2.as<int64_t>(), 13l);

    SettingValue v4(13.4);
    v2 = std::move(v4);
    ASSERT_FALSE(v4.is_a<double>());
    ASSERT_TRUE(v2.is_a<double>());
    ASSERT_EQ(v2.as<double>(), 13.4);

    SettingValue v5(true);
    v2 = std::move(v5);
    ASSERT_FALSE(v5.is_a<bool>());
    ASSERT_TRUE(v2.is_a<bool>());
    ASSERT_EQ(v2.as<bool>(), true);

    SettingValue v6(vector<double>({7.6, 5.4, 3.2}));
    v2 = std::move(v6);
    ASSERT_FALSE(v6.is_a<vector<double>>());
    ASSERT_TRUE(v2.is_a<vector<double>>());
    ASSERT_EQ(v2.as<vector<double>>()[2], 3.2);

    SettingValue v7(Vec2({{7.6}, {5.4, 3.2}}));
    v2 = std::move(v7);
    ASSERT_FALSE(v7.is_a<Vec2>());
    ASSERT_TRUE(v2.is_a<Vec2>());
    ASSERT_EQ(v2.as<Vec2>()[1][0], 5.4);
}

TEST(ymmsl_settings, test_compare_setting_value) {
    SettingValue v1(13);
    SettingValue v2(13.0);
    SettingValue v3("13");
    SettingValue v4("13");
    SettingValue v5({13.2, 14.3});
    SettingValue v6(std::vector<double>({13.2, 14.3}));
    SettingValue v7(Vec2({{7.6}, {5.4, 3.2}}));
    SettingValue v8({{7.6}, {5.4, 3.2}});

    ASSERT_NE(v1, v2);
    ASSERT_NE(v1, v3);
    ASSERT_EQ(v3, v4);
    ASSERT_EQ(v5, v6);
    ASSERT_NE(v1, v5);
    ASSERT_NE(v2, v6);
    ASSERT_NE(v2, v7);
    ASSERT_NE(v6, v7);
    ASSERT_EQ(v7, v8);
}

TEST(ymmsl_settings, test_create_settings) {
    Settings s1;
}

TEST(ymmsl_settings, test_compare_settings) {
    Settings s1;
    Settings s2;

    ASSERT_TRUE(s1 == s2);
    ASSERT_TRUE(s2 == s1);
    ASSERT_FALSE(s1 != s2);
    ASSERT_FALSE(s2 != s1);

    s1["test"] = true;
    s2["test"] = true;
    ASSERT_EQ(s1, s2);
    ASSERT_EQ(s2, s1);

    s1["test2"] = 10;
    ASSERT_NE(s1, s2);
    ASSERT_NE(s2, s1);
    s2["test2"] = 10;
    ASSERT_EQ(s1, s2);
    ASSERT_EQ(s2, s1);

    s1["test2"] = "10";
    ASSERT_NE(s1, s2);
    ASSERT_NE(s2, s1);
}

TEST(ymmsl_settings, test_settings_size) {
    Settings s1;

    ASSERT_EQ(s1.size(), 0u);
    ASSERT_TRUE(s1.empty());
}

TEST(ymmsl_settings, test_set_get_settings_value) {
    Settings s1;

    s1["test"] = "testing";
    ASSERT_EQ(s1.at("test"), "testing");

    s1["test2"] = 123.4;
    ASSERT_TRUE(s1["test2"].is_a<double>());
    ASSERT_EQ(s1.at("test2"), 123.4);

    s1["test_list"] = {123.4, 567.8};
    ASSERT_TRUE(s1.at("test_list").is_a<std::vector<double>>());
    ASSERT_EQ(s1.at("test_list").as<std::vector<double>>()[1], 567.8);

    ASSERT_THROW(s1.at("invalid^ref"), std::invalid_argument);
    ASSERT_THROW(s1.at("0invalid"), std::invalid_argument);
    ASSERT_THROW(s1.at("no_such_key"), std::out_of_range);
}

TEST(ymmsl_settings, test_erase) {
    Settings s1;

    ASSERT_FALSE(s1.contains("test"));
    s1["test"] = true;
    ASSERT_TRUE(s1.contains("test"));

    s1.erase("test");
    ASSERT_FALSE(s1.contains("test"));
    ASSERT_THROW(s1.at("test"), std::out_of_range);
}

TEST(ymmsl_settings, test_clear) {
    Settings s1;

    s1["test"] = true;
    s1["test2"] = 1;

    ASSERT_TRUE(s1.contains("test"));
    ASSERT_TRUE(s1.contains("test2"));

    s1.clear();

    ASSERT_FALSE(s1.contains("test"));
    ASSERT_FALSE(s1.contains("test2"));
}


TEST(ymmsl_settings, test_iterate) {
    Settings s1;
    s1["test"] = true;
    s1["test2"] = 123;

    for (auto const & p : s1) {
        if (p.first == "test")
            ASSERT_EQ(p.second, true);
        else
            ASSERT_EQ(p.second, 123);
    }
}

