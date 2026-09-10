#pragma once

#include <functional>
#include <string>

#include <ymmsl/component.hpp>
#include <ymmsl/identity.hpp>


/** @file ports.hpp
 *
 * Contains classes for describing ports and the timelines they're on.
 */

namespace ymmsl { namespace impl {
    class Timeline;
} }

namespace std {
    template<> struct hash<::ymmsl::impl::Timeline> {
        typedef ::ymmsl::impl::Timeline argument_type;
        typedef size_t result_type;

        std::size_t operator()(::ymmsl::impl::Timeline const &) const noexcept;
    };
}


namespace ymmsl { namespace impl {

/** Identifies a timeline on which a port sends or receives.
 *
 * Timelines have a string representation, which is a ":"-joined path of
 * component names, with a leading colon if the Timeline is absolute.
 */
class Timeline {
    public:
        /** Create a Timeline from its string representation.
         *
         * @param timeline A ":"-joined timeline string.
         */
        explicit Timeline(std::string const & timeline);

        /** Conversion to std::string.
         *
         * @return The string representation of this Timeline.
         */
        explicit operator std::string() const;

        /** Compares for equality.
         *
         * @param rhs The Timeline to compare against.
         *
         * @return True iff both Timelines are equal.
         */
        bool operator==(Timeline const & rhs) const;

        /** Return the number of parts in the Timeline.
         */
        std::size_t size() const;

    private:
        std::string timeline_;
};


/** A port on a component.
 *
 * Ports are used by components to send or receive messages on. They are
 * connected by conduits to enable communication between components.
 */
struct Port {
    Identifier name;    /// The name of the port.
    Operator oper;      /// The MMSL operator in which this port is used.
    Timeline timeline;  /// The timeline this port is on, relative to its component.

    /** Create a Port.
     *
     * @param name The name of the port.
     * @param oper The MMSL operator in which this port is used.
     * @param timeline The timeline this port is on. Defaults to the empty,
     *      relative timeline.
     */
    Port(Identifier const & name, Operator oper, Timeline const & timeline = Timeline(""));
};

} }
