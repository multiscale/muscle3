API Documentation for C++
=========================

This page provides full documentation for the C++ API of MUSCLE3.

Namespace libmuscle
-------------------

Data
````
.. doxygenclass:: libmuscle::Data

DataConstRef
````````````
.. doxygenclass:: libmuscle::DataConstRef

Instance
````````
.. doxygenclass:: libmuscle::Instance

InstanceFlags
`````````````
.. doxygenenum:: libmuscle::InstanceFlags

Message
```````
.. doxygenclass:: libmuscle::Message

PortsDescription
````````````````
.. doxygentypedef:: libmuscle::PortsDescription


Namespace ymmsl
---------------

allows_sending
``````````````
.. doxygenfunction:: ymmsl::allows_sending

allows_receiving
````````````````
.. doxygenfunction:: ymmsl::allows_receiving

Conduit
```````
.. doxygenclass:: ymmsl::Conduit

Identifier
``````````
.. doxygenclass:: ymmsl::Identifier
.. doxygenfunction:: ymmsl::operator<<(std::ostream&, Identifier const&)

Operator
````````
.. doxygenenum:: ymmsl::Operator

Port
````
.. doxygenstruct:: ymmsl::Port

Reference
`````````
.. doxygenclass:: ymmsl::Reference
.. doxygenfunction:: ymmsl::operator<<(std::ostream&, Reference const&)
.. doxygenclass:: ymmsl::ReferencePart

Settings
````````
.. doxygenclass:: ymmsl::Settings
.. doxygenfunction:: ymmsl::operator<<(std::ostream&, ymmsl::Settings const&)

SettingValue
````````````
.. doxygenclass:: ymmsl::SettingValue
.. doxygenfunction:: ymmsl::operator<<(std::ostream&, ymmsl::SettingValue const&)

