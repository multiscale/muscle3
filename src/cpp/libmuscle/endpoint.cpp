#include <libmuscle/endpoint.hpp>


using ymmsl::Identifier;
using ymmsl::Reference;


namespace libmuscle { namespace _MUSCLE_IMPL_NS {

Endpoint::Endpoint(
        Reference const & kernel,
        std::vector<int> const & index,
        Identifier const & port,
        Optional<int> const & slot)
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
    if (slot.is_set())
        ret += slot.get();
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

