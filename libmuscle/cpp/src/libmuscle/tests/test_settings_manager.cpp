#include "libmuscle/settings_manager.hpp"

#include <string>
#include <vector>

#include <gtest/gtest.h>

#include <libmuscle/namespace.hpp>
#include <ymmsl/ymmsl.hpp>


using namespace std::string_literals;
using libmuscle::_MUSCLE_IMPL_NS::SettingsManager;
using ymmsl::Reference;
using ymmsl::Settings;


using VecS = std::vector<std::string>;


int main(int argc, char *argv[]) {
    ::testing::InitGoogleTest(&argc, argv);
    return RUN_ALL_TESTS();
}

TEST(libmuscle_settings_manager, test_create_settings_manager) {
    SettingsManager s;

    ASSERT_EQ(s.base.size(), 0u);
    ASSERT_EQ(s.overlay.size(), 0u);
}

TEST(libmuscle_settings_manager, test_list_settings_globals) {
    SettingsManager s;

    s.base["test1"] = 13;
    s.base["test2"] = 14;
    ASSERT_EQ(s.list_settings("macro"), VecS({"test1", "test2"}));
}

TEST(libmuscle_settings_manager, test_list_settings_specifics) {
    SettingsManager s;

    s.base["macro.test1"] = "test1";
    s.base["micro.test2"] = "test2";
    ASSERT_EQ(s.list_settings("macro"), VecS({"test1"}));

    s.base["micro.test1"] = "test1";
    ASSERT_EQ(s.list_settings("macro"), VecS({"test1"}));
}

TEST(libmuscle_settings_manager, test_list_settings_override) {
    SettingsManager s;

    s.base["test1"] = "test1";
    s.base["macro.test1"] = 42;
    ASSERT_EQ(s.list_settings("macro"), VecS({"test1"}));

    s.base["micro.test1"] = 43;
    ASSERT_EQ(s.list_settings("macro"), VecS({"test1"}));

    s.base["test2"] = "test2";
    ASSERT_EQ(s.list_settings("macro"), VecS({"test1", "test2"}));
}

TEST(libmuscle_settings_manager, test_list_settings_overlay) {
    SettingsManager s;

    s.base["test1"] = "test1";
    s.overlay["test1"] = "test1";
    ASSERT_EQ(s.list_settings("macro"), VecS({"test1"}));

    s.overlay["test2"] = "test2";
    ASSERT_EQ(s.list_settings("macro"), VecS({"test1", "test2"}));
}

TEST(libmuscle_settings_manager, test_list_settings_overlay_override) {
    SettingsManager s;

    s.base["test1"] = "test1";
    s.base["micro.test2"] = 1;
    s.overlay["macro.test1"] = 13;
    s.overlay["micro.test2"] = 2;

    ASSERT_EQ(s.list_settings("macro"), VecS({"test1"}));
    ASSERT_EQ(s.list_settings("micro"), VecS({"test1", "test2"}));
    ASSERT_EQ(s.list_settings("meso"), VecS({"test1"}));
}

TEST(libmuscle_settings_manager, test_get_setting) {
    SettingsManager s;

    s.base["test"] = 13;
    ASSERT_EQ(s.get_setting("instance"s, "test"s), 13);

    s.overlay["test2"] = 14;
    ASSERT_EQ(s.get_setting("instance"s, "test2"s), 14);

    s.base["test2"] = "test";
    ASSERT_EQ(s.get_setting("instance"s, "test2"s), 14);

    s.overlay = Settings();
    ASSERT_EQ(s.get_setting("instance"s, "test2"s), "test");


    s.base["test3"] = "base_test3";
    s.base["instance.test3"] = "base_instance_test3";
    ASSERT_EQ(s.get_setting("instance"s, "test3"s), "base_instance_test3");
    ASSERT_EQ(s.get_setting("instance2"s, "test3"s), "base_test3");

    s.overlay["test3"] = "overlay_test3";
    s.overlay["instance.test3"] = "overlay_instance_test3";
    ASSERT_EQ(s.get_setting("instance"s, "test3"s), "overlay_instance_test3");
    ASSERT_EQ(s.get_setting("instance2"s, "test3"s), "overlay_test3");

    s.base["instance.test4"] = "base_test4";
    s.overlay["test4"] = "overlay_test4";
    ASSERT_EQ(s.get_setting("instance"s, "test4"s), "base_test4");
    ASSERT_EQ(s.get_setting("instance[10]"s, "test4"s), "base_test4");

    s.base["instance[10].test5"] = "base_test5";
    s.overlay["test5"] = "overlay_test5";
    ASSERT_EQ(s.get_setting("instance"s, "test5"s), "overlay_test5");
    ASSERT_EQ(s.get_setting("instance[10]"s, "test5"s), "base_test5");
    ASSERT_EQ(s.get_setting("instance[11]"s, "test5"s), "overlay_test5");
}

