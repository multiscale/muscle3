#pragma once

#include <libmuscle/namespace.hpp>
#include <libmuscle/util.hpp>
#include <ymmsl/ymmsl.hpp>

#include <libmuscle/tests/mocks/mock_support.hpp>

#include <string>
#include <vector>


namespace libmuscle { namespace _MUSCLE_IMPL_NS {

// Wrapper for get_setting to support default argument
struct MockGetSetting : public MockFun<
    Val<::ymmsl::SettingValue const &>,
    Val<::ymmsl::Reference const &>,
    Val<::ymmsl::Reference const &>,
    Val<Optional<::ymmsl::SettingValue> const &>
> {
    using BaseMockFun = MockFun<
        Val<::ymmsl::SettingValue const &>,
        Val<::ymmsl::Reference const &>,
        Val<::ymmsl::Reference const &>,
        Val<Optional<::ymmsl::SettingValue> const &>
    >;

    // Overload to support calling with 2 arguments (default third argument = {})
    ::ymmsl::SettingValue const & operator()(
            ::ymmsl::Reference const & instance,
            ::ymmsl::Reference const & setting_name,
            Optional<::ymmsl::SettingValue> const & default_value = {}) const {
        return BaseMockFun::operator()(instance, setting_name, default_value);
    }
};

class MockSettingsManager : public MockClass<MockSettingsManager> {
    public:
        MockSettingsManager(ReturnValue) {
            NAME_MOCK_MEM_FUN(MockSettingsManager, constructor);
            NAME_MOCK_MEM_FUN(MockSettingsManager, list_settings);
            NAME_MOCK_MEM_FUN(MockSettingsManager, get_setting);
        }

        MockSettingsManager() {
            init_from_return_value();
            constructor();
        }

        MockFun<Void> constructor;

        ::ymmsl::Settings base, overlay;

        MockFun<
            Val<std::vector<std::string>>, Val<::ymmsl::Reference const &>
            > list_settings;

        MockGetSetting get_setting;
};

using SettingsManager = MockSettingsManager;

} }

