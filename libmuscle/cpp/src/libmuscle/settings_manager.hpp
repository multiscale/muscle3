#pragma once

#include <ymmsl/settings.hpp>


namespace libmuscle {

/** Manages the current settings for a compute element instance.
 */
class SettingsManager {
    public:
        ymmsl::Settings base, overlay;

        /** Get a parameter's value.
         *
         * @param instance The name of the instance to get the setting for.
         * @param parameter_name The name of the setting to get.
         *
         * @return The value of the setting.
         * @throws std::out_of_range if the setting was not found.
         */
        ymmsl::ParameterValue const & get_parameter(
                ymmsl::Reference const & instance,
                ymmsl::Reference const & parameter_name) const;

        /** Get a parameter's value, checking the type.
         *
         * @param T The expected type, one of std::string, int64_t, double,
         *          bool, std::vector<double>, std::vector<std::vector<double>>.
         * @param instance The name of the instance to get the setting for.
         * @param parameter_name The name of the setting to get.
         *
         * @return The value of the setting.
         * @throws std::out_of_range if the setting was not found.
         */
        template <typename T>
        T const & get_parameter_as(
                ymmsl::Reference const & instance,
                ymmsl::Reference const & parameter_name) const;
};

}

