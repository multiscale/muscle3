// Template implementation. Do not include directly!

namespace libmuscle {

template <typename ValueType>
ValueType Instance::get_parameter_value_as(std::string const & name) const {
    return settings_manager_.get_parameter(instance_name_, name).as<ValueType>();
}

}

