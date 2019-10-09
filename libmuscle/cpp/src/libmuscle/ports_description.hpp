#include <string>
#include <unordered_map>
#include <vector>

#include <ymmsl/ymmsl.hpp>


namespace libmuscle { namespace impl {

/** A description of which ports a compute element has.
 *
 * You can create one like this:
 *
 * PortsDescription ports({
 *     {Operator::F_INIT, {"port1", "port2"}},
 *     {Operator::O_F, {"port3[]"}}
 *     });
 *
 * and access elements as
 *
 * ports[Operator::F_INIT][0] == "port1";
 *
 * or for a const reference to a PortsDescription
 *
 * ports.at(Operator::F_INIT)[1] == "port2";
 */
using PortsDescription = std::unordered_map<ymmsl::Operator, std::vector<std::string>>;

} }

