#pragma once

#include <libmuscle/namespace.hpp>
#include <ymmsl/ymmsl.hpp>

#include <libmuscle/tests/mocks/mock_support.hpp>

#include <string>
#include <vector>


namespace libmuscle { namespace _MUSCLE_IMPL_NS {

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

        MockFun<
            Val<::ymmsl::SettingValue const &>,
            Val<::ymmsl::Reference const &>, Val<::ymmsl::Reference const &>
            > get_setting;
};

using SettingsManager = MockSettingsManager;

} }

