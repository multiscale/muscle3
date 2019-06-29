#pragma once

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

}

