#include "libmuscle/port.hpp"

#include <stdexcept>
#include <string>

#include "libmuscle/operator.hpp"
#include <ymmsl/compute_element.hpp>
#include <ymmsl/identity.hpp>


using namespace std::string_literals;
using ymmsl::Identifier;
using ymmsl::Operator;


namespace libmuscle { namespace impl {

Port::Port(
        std::string const & name, Operator oper,
        bool is_vector, bool is_connected,
        int our_ndims, std::vector<int> peer_dims)
    : ::ymmsl::Port(Identifier(name), oper)
{
    is_connected_ = is_connected;
    if (is_vector) {
        if (our_ndims == static_cast<int>(peer_dims.size()))
            length_ = 0;
        else if ((our_ndims + 1) == static_cast<int>(peer_dims.size()))
            length_ = peer_dims.back();
        else if (our_ndims > static_cast<int>(peer_dims.size()))
            throw std::runtime_error("Vector port '"s + name + "' is connected"
                    + " to an instance set with fewer dimensions. It should be"
                    + " connected to a scalar port on a set with one more"
                    + " dimension, or to a vector port on a set with the same"
                    + " number of dimensions.");
        else
            throw std::runtime_error("Port '"s + name + "' is connected to an"
                    + " instance set with more than one dimension more than"
                    + " its own, which is not possible.");
        is_open_ = std::vector<bool>(length_, true);
    }
    else {
        if (our_ndims < static_cast<int>(peer_dims.size()))
            throw std::runtime_error("Scalar port "s + name + " is connected"
                    + " to an instance set with more dimensions. It should be"
                    + " connected to a scalar port on an instance set with the"
                    + " same dimensions, or to a vector port on an instance"
                    + " set with with one less dimension.");
        else if (our_ndims > static_cast<int>(peer_dims.size()) + 1)
            throw std::runtime_error("Scalar port "s + name + " is connected"
                    + " to an instance set with at least two fewer dimensions,"
                    + " which is not possible.");
        length_ = -1;
        is_open_.push_back(true);
    }

    is_resizable_ = is_vector && (our_ndims == static_cast<int>(peer_dims.size()));
}

bool Port::is_connected() const {
    return is_connected_;
}

bool Port::is_open() const {
    return is_open_.at(0u);
}

bool Port::is_open(int slot) const {
    return is_open_.at(slot);
}

bool Port::is_open(Optional<int> slot) const {
    if (slot.is_set())
        return is_open(slot.get());
    return is_open();
}

bool Port::is_vector() const {
    return length_ >= 0;
}

bool Port::is_resizable() const {
    return is_resizable_;
}

int Port::get_length() const {
    if (length_ < 0)
        throw std::runtime_error("Tried to get length of scalar port "s + name);
    return length_;
}

void Port::set_length(int length) {
    if (!is_resizable_)
        throw std::runtime_error("Tried to resize port "s + name + ", but it is"
                + " not resizable");
    if (length != length_) {
        length_ = length;
        is_open_ = std::vector<bool>(length_, true);
    }
}

void Port::set_closed() {
    is_open_[0] = false;
}

void Port::set_closed(int slot) {
    is_open_[slot] = false;
}

} }

