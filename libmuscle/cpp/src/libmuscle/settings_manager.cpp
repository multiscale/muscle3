#include <libmuscle/settings_manager.hpp>

#include <iterator>
#include <stdexcept>
#include <utility>


using ymmsl::ParameterValue;
using ymmsl::Reference;
using ymmsl::Settings;


namespace libmuscle {

ParameterValue const & SettingsManager::get_parameter(
        Reference const & instance,
        Reference const & parameter_name
        ) const
{
    auto it = instance.cend();
    do {
        Reference name = (it == instance.cbegin())
            ? parameter_name
            : Reference(instance.cbegin(), it) + parameter_name;

        if (overlay.contains(name))
            return overlay.at(name);
        if (base.contains(name))
            return base.at(name);

        if (it == instance.cbegin())
            break;
        --it;
    }
    while (true);
    throw std::out_of_range("Parameter value for parameter "
                            + static_cast<std::string>(parameter_name)
                            + " was not set");
}

template <typename T>
T const & SettingsManager::get_parameter_as(
        Reference const & instance,
        Reference const & parameter_name
        ) const
{
    ParameterValue value(get_parameter(instance, parameter_name));

    if (!value.is<T>())
        throw std::runtime_error("Value for parameter "
                                 + static_cast<std::string>(parameter_name)
                                 + " is the wrong type.");
    return value.get<T>();
}

}

