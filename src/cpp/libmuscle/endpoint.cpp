#include <libmuscle/endpoint.hpp>


using ymmsl::Identifier;
using ymmsl::Reference;


namespace libmuscle { namespace _MUSCLE_IMPL_NS {

Endpoint::Endpoint(
        Reference const & kernel,
        std::vector<int> const & index,
        Identifier const & port,
        std::vector<int> const & slot)
    : kernel(kernel)
    , index(index)
    , port(port)
    , slot(slot)
{}

Reference Endpoint::ref() const {
    Reference ret(kernel);
    if (!index.empty())
        ret += index;
    ret += port;
    if (!slot.empty())
        ret += slot;
    return ret;
}

Endpoint::operator std::string() const {
    return static_cast<std::string>(ref());
}

Reference Endpoint::instance() const {
    Reference ret(kernel);
    if (!index.empty())
        ret += index;
    return ret;
}

} }

