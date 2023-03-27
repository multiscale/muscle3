#pragma once

#include <libmuscle/namespace.hpp>

#include <ymmsl/ymmsl.hpp>


namespace libmuscle { namespace _MUSCLE_IMPL_NS {

/** Manages the current settings for a component instance.
 */
class SettingsManager {
    public:
        ymmsl::Settings base, overlay;

        /** Get a setting's value.
         *
         * @param instance The name of the instance to get the setting for.
         * @param setting_name The name of the setting to get.
         *
         * @return The value of the setting.
         * @throws std::out_of_range if the setting was not found.
         */
        ymmsl::SettingValue const & get_setting(
                ymmsl::Reference const & instance,
                ymmsl::Reference const & setting_name) const;

        /** Get a setting's value, checking the type.
         *
         * @param T The expected type, one of std::string, int64_t, double,
         *          bool, std::vector<double>, std::vector<std::vector<double>>.
         * @param instance The name of the instance to get the setting for.
         * @param setting_name The name of the setting to get.
         *
         * @return The value of the setting.
         * @throws std::out_of_range if the setting was not found.
         */
        template <typename T>
        T const & get_setting_as(
                ymmsl::Reference const & instance,
                ymmsl::Reference const & setting_name) const;
};

} }

