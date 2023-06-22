API Documentation for C++
=========================

This page provides full documentation for the C++ API of MUSCLE3.

Note that in a few places, classes are referred to as
``libmuscle::_MUSCLE_IMPL_NS::<class>`` or ``ymmsl::impl::<class>``. This
is a bug in the documentation rendering process, the class is actually
available as ``libmuscle::<class>`` and should be used as such.


Namespace libmuscle
-------------------

.. doxygenclass:: libmuscle::_MUSCLE_IMPL_NS::Data
.. doxygenclass:: libmuscle::_MUSCLE_IMPL_NS::DataConstRef
.. doxygenclass:: libmuscle::_MUSCLE_IMPL_NS::Instance
.. doxygenenum:: libmuscle::_MUSCLE_IMPL_NS::InstanceFlags
.. doxygenclass:: libmuscle::_MUSCLE_IMPL_NS::Message
.. doxygentypedef:: libmuscle::_MUSCLE_IMPL_NS::PortsDescription


Namespace ymmsl
---------------

.. doxygenfunction:: ymmsl::impl::allows_sending
.. doxygenfunction:: ymmsl::impl::allows_receiving

.. doxygenclass:: ymmsl::impl::Conduit
.. doxygenclass:: ymmsl::impl::Identifier
.. doxygenfunction:: ymmsl::impl::operator<<(std::ostream&, Identifier const&)
.. doxygenenum:: ymmsl::impl::Operator
.. doxygenstruct:: ymmsl::impl::Port
.. doxygenclass:: ymmsl::impl::Reference
.. doxygenfunction:: ymmsl::impl::operator<<(std::ostream&, Reference const&)
.. doxygenclass:: ymmsl::impl::ReferencePart
.. doxygenclass:: ymmsl::impl::Settings
.. doxygenfunction:: ymmsl::impl::operator<<(std::ostream&, ymmsl::impl::Settings const&)
.. doxygenclass:: ymmsl::impl::SettingValue
.. doxygenfunction:: ymmsl::impl::operator<<(std::ostream&, ymmsl::impl::SettingValue const&)

