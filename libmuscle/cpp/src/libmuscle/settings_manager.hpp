#pragma once

#include <libmuscle/namespace.hpp>

#include <ymmsl/ymmsl.hpp>

#include <string>
#include <unordered_set>
#include <vector>


namespace libmuscle { namespace _MUSCLE_IMPL_NS {

/** Manages the current settings for a component instance.
 */
class SettingsManager {
    public:
        ymmsl::Settings base, overlay;

        /** Return the names of all the settings.
         *
         * This returns the names of all the settings, as the model would
         * pass them to request settings. It returns
         *
         * - <setting_name> as-is
         * - <instance_id>.<setting_name> as <setting_name>
         * - <other_id>.<setting_name> not at all
         * - <setting>.<setting> not at all
         *
         * Note that we don't return global settings with multipart names.
         * Those are legal, but currently indistinguishable from settings
         * intended for other components. We're not actually telling
         * anyone that they're legal, so we can probably get away with
         * that. If it becomes an issue, we'll have to get a list of
         * instance ids from the manager so we can recognise them
         * correctly.
         *
         * @param instance Our instance id.
         * @return A list of setting names.
         */
        std::vector<std::string> list_settings(
                ymmsl::Reference const & instance) const;

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

