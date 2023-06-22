#include <libmuscle/settings_manager.hpp>

#include <algorithm>
#include <iterator>
#include <stdexcept>
#include <string>
#include <unordered_set>
#include <utility>


using ymmsl::SettingValue;
using ymmsl::Reference;
using ymmsl::Settings;

namespace {

std::unordered_set<std::string> extract_names(
        Reference const & instance_id, Settings const & settings)
{
    std::unordered_set<std::string> result;
    for (auto const & nv: settings) {
        Reference const & name = nv.first;
        if (name.length() == 1)
            result.insert(std::string(name));
        else {
            std::size_t id_len = instance_id.length();
            if (name.length() > id_len) {
                // check if the name starts with our instance id
                bool for_us = true;

                auto name_it = name.cbegin();
                auto instance_it = instance_id.cbegin();
                while (instance_it != instance_id.cend()) {
                    if (*name_it != *instance_it) {
                        for_us = false;
                        break;
                    }
                    ++name_it;
                    ++instance_it;
                }

                if (for_us)
                    result.insert(
                            std::string(Reference(name_it, name.cend())));
            }
        }
    }
    return result;
}

}


namespace libmuscle { namespace _MUSCLE_IMPL_NS {

std::vector<std::string> SettingsManager::list_settings(
        Reference const & instance) const
{
    std::unordered_set<std::string> names = extract_names(instance, base);
    auto overlay_names = extract_names(instance, overlay);
    names.insert(overlay_names.cbegin(), overlay_names.cend());

    std::vector<std::string> result(names.cbegin(), names.cend());
    std::sort(result.begin(), result.end());
    return result;
}

SettingValue const & SettingsManager::get_setting(
        Reference const & instance,
        Reference const & setting_name
        ) const
{
    auto it = instance.cend();
    do {
        Reference name = (it == instance.cbegin())
            ? setting_name
            : Reference(instance.cbegin(), it) + setting_name;

        if (overlay.contains(name))
            return overlay.at(name);
        if (base.contains(name))
            return base.at(name);

        if (it == instance.cbegin())
            break;
        --it;
    }
    while (true);
    throw std::out_of_range("Value for setting "
                            + static_cast<std::string>(setting_name)
                            + " was not set");
}

template <typename T>
T const & SettingsManager::get_setting_as(
        Reference const & instance,
        Reference const & setting_name
        ) const
{
    SettingValue value(get_setting(instance, setting_name));

    if (!value.is_a<T>())
        throw std::runtime_error("Value for Setting "
                                 + static_cast<std::string>(setting_name)
                                 + " is the wrong type.");
    return value.as<T>();
}

} }

