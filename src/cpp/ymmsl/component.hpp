#pragma once

#include <string>


/** @file component.hpp
 *
 * Contains helper classes for defining simulation components.
 */

/** The global ymmsl namespace. */
namespace ymmsl { namespace impl {

/** An operator of a component.
 *
 * This is a combination of the Submodel Execution Loop operators,
 * and operators for other components such as mappers.
 */
enum class Operator {
    F_INIT = 1,
    O_I = 2,
    S = 3,
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

/** Return the name of the given operator
 * 
 * @param op The operator
 * @return The name: "F_INIT", "O_I", "S" or "O_F"
 */
std::string operator_name(Operator op);

/** Return the operator from its name
 * 
 * @param name The operator name
 * @return The operator enum instance
 */
Operator operator_for_name(std::string const & name);

} }

// Older compilers (GCC < 6) do not have std::hash defined for enum classes.
// This was a defect in C++14, and took some time to get fixed. To make things
// compile on older compilers, we add a custom overload here.
namespace std {
    template <> struct hash<::ymmsl::impl::Operator> {
        size_t operator()(::ymmsl::impl::Operator const & op) const {
            return hash<int>()(static_cast<int>(op));
        }
    };
}

