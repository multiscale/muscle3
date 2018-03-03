====================
Manager architecture
====================

The MUSCLE 3 manager consists of several modules, each with a specific
responsibility. Together, they perform all the tasks required of the manager.
These components are:

* the MMP Server, which listens for connections from kernels and responds to
  them,
* the Logger, which gets log messages and writes them to a log file,
* the Instance Registry, which stores information about instances,
* the Configuration Store, which stores kernel configuration information,
* the Topology Store, which stores information on connections between instances,
* LibMML, which reads yMML files and extracts information about kernels,
  instances, and conduits,
* Main, which creates the other components and performs start-up tasks.


----------
MMP Server
----------

The MMP Server is a gRPC server. It listens for requests from instances, and
services them by calling on functionality in the Logger, Instance Registry,
Configuration Store and Topology Store. These requests include:

* Log Requests
* Registration Requests
* Configuration Requests
* Peer Requests
* Deregistration Requests
* Dynamic Peer Requests (will be described later)

A Log Request is a request to log a message. Instances send these for log
messages with a high enough log level (e.g. critical errors, log messages used
for performance tracking). Log messages are structured (see below at the
description of the Logger).

A Registration Request is how an instance makes itself known to the manager.
The instance sends its name, a list of its endpoints, and the network location
it is listening on (a string). The server sends this information to the
Instance Registry, and returns nothing.

A Configuration Request is sent by an instance. It sends its instance name, and
receives a dictionary of parameters and their values (see below under
Configuration Store).

A Peer Request is sent by an instance after registering itself. It sends its
instance name, and receives either an error message, if its peers have not yet
registered themselves, or a list of records containing

* sender endpoint name
* slot number
* target network location
* receiver name
* receiver endpoint name

with one such record for each endpoint the instance registered in its
Registration Request. These are all strings, with the exception of the slot
number, which is an integer that is always equal to 0 (this will change when
vector conduits are added, to be described later). The MMP Server obtains this
information from the Instance Registry (to get the sending endpoints of the
requesting instance), the Topology Store (to get the outgoing conduit and the
name of the receiving instance), and again from the Instance Registry (to get
the network location of the receiving instance).

A Deregistration Request is sent by an instance when it shuts down. It contains
the instance's name, and causes the MMP Server to remove the instance from the
Instance Registry.


------
Logger
------

The logger component takes log messages, which consist of

* instance name
* operator
* time stamp
* log level
* message text

and writes them to a log file in text format. Initially, this can just be a
fixed muscle3.log in the current directory, with configurability of the
location and other niceties added later. The log level should be configurable
though. In the future, we will want the ability to write (instance name,
operator, time stamp) for a given log level to a second file in
machine-readable format (e.g. JSON).


-----------------
Instance Registry
-----------------

The Instance Registry stores information about the currently running instances.
It is a simple in-memory database. Its user is the MMP Server, which adds,
requests and removes entries. The Instance Registry stores the following
information for each instance:

* instance name
* network location
* list of endpoints

where each endpoint has a

* name
* operator
* data type.

New instances can be added to the Instance Registry, instances can be deleted
given their name, and instances can be retrieved by name.


-------------------
Configuration Store
-------------------

The Configuration Store contains information about the configuration of the
model that is being run. The basic container of configuration information is a
dictionary structure that maps the name of a model parameter (a string) to a
value, which is a string, integer, floating point number, or nil (None, null).

The Configuration Store maintains such a dictionary for each instance. This
dictionary is read from the yMML file on start-up by the Main component and
passed to the Configuration Store. Later, the MMP Server will request the
dictionary for a given instance in order to service a request from that
instance.


--------------
Topology Store
--------------

The Topology Store stores a list of conduits. Each conduit has the sending
instance's name, the sending endpoint name, the receiving instance's name, and
the receiving endpoint name. These are also read from the yMML file. This
information is used by the MMP Server to service Peer Requests.


------
LibMML
------

LibMML is a Python library for reading and writing yMML files, which are
YAML-based representations of MML graphs. The yMML file format still needs to
be designed; it will be based on xMML, with some extensions to support the
ComPat patterns.

LibMML will be based on the Python YAML library, with a shim layer to add some
syntactic sugar to the file format, to make it easier to type by hand. LibMML
is not a part of MUSCLE 3, but will be used by it.

yMML files will contain information on kernels, instances, the connections
between them, and the parameters to use them with. Information on how to deploy
the simulation will probably be kept separate, although the two are of course
related.


----
Main
----

The Main component of the MUSCLE 3 Manager performs start-up of the manager. It
parses the command line, setting the log level as given, and reading the yMML
file location. It then constructs all the other components, loads the yMML file
and stores the information into the Configuration Store and Topology Store. It
then starts the MMP Server and passes it control.
