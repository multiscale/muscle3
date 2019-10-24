#include <ymmsl/model.hpp>

#include <iterator>
#include <sstream>


namespace ymmsl { namespace impl {

Conduit::Conduit(std::string const & sender, std::string const & receiver)
    : sender(sender)
    , receiver(receiver)
{
    check_reference_(sender);
    check_reference_(receiver);
}

Conduit::operator std::string() const {
    std::ostringstream oss;

    oss << "Conduit(" << sender << " -> " << receiver << ")";
    return oss.str();
}

bool Conduit::operator==(Conduit const & rhs) const {
    return sender == rhs.sender && receiver == rhs.receiver;
}

Reference Conduit::sending_compute_element() const {
    Reference stem = stem_(sender);
    return Reference(stem.cbegin(), std::prev(stem.cend()));
}

Identifier Conduit::sending_port() const {
    Reference stem = stem_(sender);
    // We've checked that it is an Identifier during construction
    return std::prev(stem.cend())->identifier();
}

std::vector<int> Conduit::sending_slot() const {
    return slot_(sender);
}

Reference Conduit::receiving_compute_element() const {
    Reference stem = stem_(receiver);
    return Reference(stem.cbegin(), std::prev(stem.cend()));
}

Identifier Conduit::receiving_port() const {
    Reference stem = stem_(receiver);
    // We've checked that it is an Identifier during construction
    return std::prev(stem.cend())->identifier();
}

std::vector<int> Conduit::receiving_slot() const {
    return slot_(receiver);
}

/* Checks an endpoint for validity.
 */
void Conduit::check_reference_(Reference const & ref) const {
    // check that subscripts are at the end
    auto i = ref.cbegin();
    while (i != ref.cend() && i->is_identifier())
        ++i;
    while (i != ref.cend()) {
        if (i->is_identifier()) {
            std::ostringstream oss;
            oss << "Reference " << ref << " contains a subscript that is not";
            oss << " at the end, which is not allowed in conduits.";
            throw std::runtime_error(oss.str());
        }
        ++i;
    }

    // check that the length is at least 2
    if (stem_(ref).length() < 2) {
        std::ostringstream oss;
        oss << "Senders and receivers in conduits must have a compute element";
        oss << " name, a period, and then a port name and optionally a slot.";
        oss << " Reference " << ref << " is missing either the compute element";
        oss << " or the port.";
        throw std::runtime_error(oss.str());
    }
}

/* Extracts the slot from the given reference.
 *
 * The slot is the list of contiguous ints at the end of the reference.
 * If the reference does not end in an int, returns an empty list.
 */
std::vector<int> Conduit::slot_(Reference const & reference) const {
    std::vector<int> result;

    std::size_t i = reference.length() - 1;
    while (reference[i].is_index()) {
        result.insert(result.begin(), reference[i].index());
        --i;
    }
    return result;
}

/* Extracts the part of the reference before the slot.
 *
 * If there is no slot, returns the whole reference.
 */
Reference Conduit::stem_(Reference const & reference) const {
    Reference::const_iterator i = reference.cend();
    while (std::prev(i)->is_index())
        --i;
    return Reference(reference.cbegin(), i);
}

} }

