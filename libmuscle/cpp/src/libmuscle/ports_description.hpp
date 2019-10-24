#include <string>
#include <unordered_map>
#include <vector>

#include <ymmsl/ymmsl.hpp>


namespace libmuscle { namespace impl {

/** A description of which ports a compute element has.
 *
 * You can create one like this:
 *
 * \code{.cpp}
 * PortsDescription ports({
 *     {Operator::F_INIT, {"port1", "port2"}},
 *     {Operator::O_F, {"port3[]"}}
 *     });
 * \endcode
 *
 * and access elements as
 *
 * \code{.cpp}
 * ports[Operator::F_INIT][0] == "port1";
 * \endcode
 *
 * or for a const reference to a PortsDescription
 *
 * \code{.cpp}
 * ports.at(Operator::F_INIT)[1] == "port2";
 * \endcode
 */
using PortsDescription = std::unordered_map<ymmsl::Operator, std::vector<std::string>>;

} }

