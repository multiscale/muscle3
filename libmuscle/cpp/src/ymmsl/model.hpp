#pragma once

#include <ymmsl/identity.hpp>

#include <vector>


namespace ymmsl { namespace impl {

/** A conduit transports data between simulation components.
 *
 * A conduit has two endpoints, which are references to a Port on a Component.
 * These references must be of one of the following forms:
 *
 * - submodel.port
 * - namespace.submodel.port (or several namespace prefixes)
 *
 * @attribute sender The sending port that this conduit is connected to.
 * @attribute receiver The receiving port that this conduit is connected to.
 */
class Conduit {
    public:
        Reference sender, receiver;

        /** Create a Conduit.
         *
         * @param sender The sending port that this conduit is connected to,
         *      including the component name and the port name.
         * @param receiver The receiving port that this conduit is connected
         *      to, including the component name and the port name.
         */
        Conduit(std::string const & sender, std::string const & receiver);

        /** Convert to string.
         */
        explicit operator std::string() const;

        /** Compare two conduits for equality.
         *
         * @param rhs The other conduit to compare with.
         * @return true iff the two conduits are identical.
         */
        bool operator==(Conduit const & rhs) const;

        /** Returns a reference to the sending component.
         */
        Reference sending_component() const;

        /** Returns the identity of the sending port.
         */
        Identifier sending_port() const;

        /** Returns the slot on the sending port.
         *
         * If no slot was given, an empty list is returned.
         *
         * Note that conduits connected to specific slots are currently not
         * supported by MUSCLE 3.
         *
         * @return A list of slot indexes.
         */
        std::vector<int> sending_slot() const;

        /** Returns a reference to the receiving component.
         */
        Reference receiving_component() const;

        /** Returns the identity of the receiving port.
         */
        Identifier receiving_port() const;

        /** Returns the slot on the receiving port.
         *
         * If no slot was given, an empty list is returned.
         *
         * Note that conduits connected to specific slots are currently not
         * supported by MUSCLE 3.
         *
         * @return A list of slot indexes.
         */
        std::vector<int> receiving_slot() const;

    private:
        void check_reference_(Reference const & ref) const;
        std::vector<int> slot_(Reference const & reference) const;
        Reference stem_(Reference const & reference) const;
};

} }

