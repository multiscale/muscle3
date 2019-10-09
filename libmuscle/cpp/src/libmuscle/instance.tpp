// Template implementation. Do not include directly!

namespace libmuscle { namespace impl {

template <typename ValueType>
ValueType Instance::get_setting_as(std::string const & name) const {
    return settings_manager_.get_setting(instance_name_, name).as<ValueType>();
}

} }

