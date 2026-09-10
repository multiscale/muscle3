#include <ymmsl/ports.hpp>

#include <algorithm>


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

std::size_t Timeline::size() const {
    if (timeline_.empty() || timeline_ == ":") return 0;
    std::size_t num_colons = std::count(timeline_.begin(), timeline_.end(), ':');
    if (timeline_[0] != ':')
        return num_colons + 1;
    return num_colons;
}

Port::Port(Identifier const & name, Operator oper, Timeline const & timeline)
    : name(name)
    , oper(oper)
    , timeline(timeline)
{}

} }
