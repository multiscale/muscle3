API Documentation for C++
=========================

This page provides full documentation for the C++ API of MUSCLE3.

Namespace libmuscle
-------------------

.. doxygenclass:: libmuscle::Data
.. doxygenclass:: libmuscle::DataConstRef
.. doxygenclass:: libmuscle::Instance
.. doxygenenum:: libmuscle::InstanceFlags
.. doxygenclass:: libmuscle::Message
.. doxygentypedef:: libmuscle::PortsDescription


Namespace ymmsl
---------------

.. doxygenfunction:: ymmsl::allows_sending
.. doxygenfunction:: ymmsl::allows_receiving

.. doxygenclass:: ymmsl::Conduit
.. doxygenclass:: ymmsl::Identifier
.. doxygenfunction:: ymmsl::operator<<(std::ostream&, Identifier const&)
.. doxygenenum:: ymmsl::Operator
.. doxygenstruct:: ymmsl::Port
.. doxygenclass:: ymmsl::Reference
.. doxygenfunction:: ymmsl::operator<<(std::ostream&, Reference const&)
.. doxygenclass:: ymmsl::ReferencePart
.. doxygenclass:: ymmsl::Settings
.. doxygenfunction:: ymmsl::operator<<(std::ostream&, ymmsl::Settings const&)
.. doxygenclass:: ymmsl::SettingValue
.. doxygenfunction:: ymmsl::operator<<(std::ostream&, ymmsl::SettingValue const&)

