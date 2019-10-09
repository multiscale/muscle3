#include <libmuscle/settings_manager.hpp>

#include <iterator>
#include <stdexcept>
#include <utility>


using ymmsl::SettingValue;
using ymmsl::Reference;
using ymmsl::Settings;


namespace libmuscle { namespace impl {

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

