#include <cinttypes>
#include <string>
#include <utility>
#include <vector>

#include <gtest/gtest.h>

#include "ymmsl/settings.hpp"


using std::vector;
using Vec2 = vector<vector<double>>;

using ymmsl::ParameterValue;


TEST(ymmsl_settings, test_create_parameter_value) {
    ParameterValue v1("testing");
    ParameterValue v2(42l);
    ParameterValue v3(12.34);
    ParameterValue v4(true);
    ParameterValue v5({12.34, 56.78});
    ParameterValue v6({{12.34, 0.0}, {56.78, 0.0}});

    ASSERT_EQ(v1.get<std::string>(), "testing");
    ASSERT_EQ(v2.get<int64_t>(), 42l);
    ASSERT_EQ(v3.get<double>(), 12.34);
    ASSERT_EQ(v4.get<bool>(), true);
    ASSERT_TRUE(v5.is<vector<double>>());
    ASSERT_EQ(v5.get<vector<double>>(), vector<double>({12.34, 56.78}));
    Vec2 v6_ref;
    v6_ref.push_back(vector<double>{12.34, 0.0});
    v6_ref.push_back(vector<double>{56.78, 0.0});
    ASSERT_TRUE(v6.is<Vec2>());
    ASSERT_EQ(v6.get<Vec2>(), v6_ref);
}

TEST(ymmsl_settings, test_copy_parameter_value) {
    ParameterValue v1("testing");
    ParameterValue v2(v1);
    ASSERT_EQ(v2.get<std::string>(), "testing");

    ParameterValue v3(42l);
    ParameterValue v4(v3);
    ASSERT_EQ(v4.get<int64_t>(), 42l);

    ParameterValue v5(42.13);
    ParameterValue v6(v5);
    ASSERT_EQ(v6.get<double>(), 42.13);

    ParameterValue v7(false);
    ParameterValue v8(v7);
    ASSERT_EQ(v8.get<bool>(), false);

    ParameterValue v9(vector<double>({1.2, 8.9}));
    ParameterValue v10(v9);
    ASSERT_EQ(v10.get<vector<double>>(), vector<double>({1.2, 8.9}));

    ParameterValue v11(Vec2({{1.2, 8.9}, {2.3, 6.7}}));
    ParameterValue v12(v11);
    ASSERT_EQ(v12.get<Vec2>(), Vec2({{1.2, 8.9}, {2.3, 6.7}}));
}

TEST(ymmsl_settings, test_move_parameter_value) {
    ParameterValue v1("testing");
    ParameterValue v2(std::move(v1));
    ASSERT_EQ(v2.get<std::string>(), "testing");
    ASSERT_FALSE(v1.is<std::string>());

    ParameterValue v3(42l);
    ParameterValue v4(std::move(v3));
    ASSERT_EQ(v4.get<int64_t>(), 42);
    ASSERT_FALSE(v3.is<int64_t>());

    ParameterValue v5(42.13);
    ParameterValue v6(std::move(v5));
    ASSERT_EQ(v6.get<double>(), 42.13);
    ASSERT_FALSE(v5.is<double>());

    ParameterValue v7(true);
    ParameterValue v8(std::move(v7));
    ASSERT_EQ(v8.get<bool>(), true);
    ASSERT_FALSE(v7.is<bool>());

    ParameterValue v9({3.14, 2.71});
    ParameterValue v10(std::move(v9));
    ASSERT_EQ(v10.get<vector<double>>()[0], 3.14);
    ASSERT_FALSE(v9.is<vector<double>>());

    ParameterValue v11({{3.14, 2.71}});
    ParameterValue v12(std::move(v11));
    ASSERT_EQ(v12.get<Vec2>()[0][1], 2.71);
    ASSERT_FALSE(v11.is<Vec2>());
}

TEST(ymmsl_settings, test_copy_assign_parameter_value) {
    ParameterValue v1("testing");
    ParameterValue v2;
    v2 = v1;
    ASSERT_TRUE(v1.is<std::string>());
    ASSERT_TRUE(v2.is<std::string>());
    ASSERT_EQ(v1.get<std::string>(), "testing");
    ASSERT_EQ(v2.get<std::string>(), "testing");

    ParameterValue v3(13l);
    v2 = v3;
    ASSERT_TRUE(v3.is<int64_t>());
    ASSERT_TRUE(v2.is<int64_t>());
    ASSERT_EQ(v3.get<int64_t>(), 13l);
    ASSERT_EQ(v2.get<int64_t>(), 13l);

    ParameterValue v4(13.1);
    v2 = v4;
    ASSERT_TRUE(v4.is<double>());
    ASSERT_TRUE(v2.is<double>());
    ASSERT_EQ(v4.get<double>(), 13.1);
    ASSERT_EQ(v2.get<double>(), 13.1);

    ParameterValue v5(false);
    v2 = v5;
    ASSERT_TRUE(v5.is<bool>());
    ASSERT_TRUE(v2.is<bool>());
    ASSERT_EQ(v5.get<bool>(), false);
    ASSERT_EQ(v2.get<bool>(), false);

    ParameterValue v6({1.2});
    v2 = v6;
    ASSERT_TRUE(v6.is<vector<double>>());
    ASSERT_TRUE(v2.is<vector<double>>());
    ASSERT_EQ(v6.get<vector<double>>().size(), 1u);
    ASSERT_EQ(v2.get<vector<double>>()[0], 1.2);

    ParameterValue v7({{1.2, 1}, {4, 3}});
    v2 = v7;
    ASSERT_TRUE(v7.is<Vec2>());
    ASSERT_TRUE(v2.is<Vec2>());
    ASSERT_EQ(v7.get<Vec2>().size(), 2u);
    ASSERT_EQ(v2.get<Vec2>()[0][0], 1.2);
    ASSERT_EQ(v2.get<Vec2>()[1][1], 3.0);
}

TEST(ymmsl_settings, test_move_assign_parameter_value) {
    ParameterValue v1("testing");
    ParameterValue v2;
    v2 = std::move(v1);
    ASSERT_FALSE(v1.is<std::string>());
    ASSERT_TRUE(v2.is<std::string>());
    ASSERT_EQ(v2.get<std::string>(), "testing");

    ParameterValue v3(13l);
    v2 = std::move(v3);
    ASSERT_FALSE(v3.is<int64_t>());
    ASSERT_TRUE(v2.is<int64_t>());
    ASSERT_EQ(v2.get<int64_t>(), 13l);

    ParameterValue v4(13.4);
    v2 = std::move(v4);
    ASSERT_FALSE(v4.is<double>());
    ASSERT_TRUE(v2.is<double>());
    ASSERT_EQ(v2.get<double>(), 13.4);

    ParameterValue v5(true);
    v2 = std::move(v5);
    ASSERT_FALSE(v5.is<bool>());
    ASSERT_TRUE(v2.is<bool>());
    ASSERT_EQ(v2.get<bool>(), true);

    ParameterValue v6(vector<double>({7.6, 5.4, 3.2}));
    v2 = std::move(v6);
    ASSERT_FALSE(v6.is<vector<double>>());
    ASSERT_TRUE(v2.is<vector<double>>());
    ASSERT_EQ(v2.get<vector<double>>()[2], 3.2);

    ParameterValue v7(Vec2({{7.6}, {5.4, 3.2}}));
    v2 = std::move(v7);
    ASSERT_FALSE(v7.is<Vec2>());
    ASSERT_TRUE(v2.is<Vec2>());
    ASSERT_EQ(v2.get<Vec2>()[1][0], 5.4);
}

