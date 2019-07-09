#pragma once

#include <ymmsl/identity.hpp>


/** @file compute_element.hpp
 *
 * Contains helper classes for defining compute elements.
 */

/** The global ymmsl namespace. */
namespace ymmsl {

/** An operator of a Compute Element.
 *
 * This is a combination of the Submodel Execution Loop operators,
 * and operators for other components such as mappers.
 */
enum class Operator {
    NONE = 0,
    F_INIT = 1,
    O_I = 2,
    S = 3,
    B = 4,
    O_F = 5
};

/** Whether the given operator allows sending messages.
 *
 * @param op The operator to check.
 * @return true If and only if the operator allows sending
 */
bool allows_sending(Operator op);

/** Whether the given operator allows receiving messages.
 *
 * @param op The operator to check.
 * @return true If and only if the operator allows receiving
 */
bool allows_receiving(Operator op);

/** A port on a compute element.
 *
 * Ports are used by compute elements to send or receive messages on. They are
 * connected by conduits to enable communication between compute elements.
 *
 * @attribute name The name of the port.
 * @attribute oper The MMSL operator in which this port is used.
 */
struct Port {
    Identifier name;
    Operator oper;

    /** Create a Port.
     *
     * @param name The name of the port.
     * @param oper The MMSL operator in which this port is used.
     */
    Port(Identifier const & name, Operator oper);
};

}

