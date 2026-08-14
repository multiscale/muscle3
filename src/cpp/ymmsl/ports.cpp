#include <ymmsl/ports.hpp>


::std::size_t (::std::hash<::ymmsl::impl::Timeline>::operator())(
        argument_type const & timeline) const noexcept
{
    return hash<std::string>()(static_cast<std::string>(timeline));
}

namespace ymmsl { namespace impl {

Timeline::Timeline(std::string const & timeline)
    : timeline_(timeline)
{}

Timeline::operator std::string() const {
    return timeline_;
}

bool Timeline::operator==(Timeline const & rhs) const {
    return timeline_ == rhs.timeline_;
}

Port::Port(Identifier const & name, Operator oper, Timeline const & timeline)
    : name(name)
    , oper(oper)
    , timeline(timeline)
{}

} }
