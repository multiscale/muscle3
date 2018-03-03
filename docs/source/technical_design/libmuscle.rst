======================
LibMuscle architecture
======================

LibMuscle is the MUSCLE 3 client library. Kernels link with it to get access to
functionality that lets them be part of a MUSCLE 3 simulation. As kernels can be
written in many languages, a version of LibMuscle will have to be made for each
such language.

LibMuscle has two core responsibilities: it manages configuration information,
and it takes care of communication with other instances. It can also take care
of execution of the kernel, allowing users to create kernels by simply
implementing a set of functions. Another ancillary task is providing centralised
logging.

The user uses the LibMuscle API to talk to it. It has a number of sub-APIs:

* Coordination API
* Configuration API
* Communication API
* Execution API
* Logging API

These API components contain their own logic, and use functionality
implemented by three main LibMuscle components:

* MMP client
* Configuration Store
* Communication Engine


----------------
Coordination API
----------------

The Coordination API consists of a single function, which
initialises MUSCLE 3, contacts the manager, and performs the
instance side of the MUSCLE initialisation process. This function
must always be called first, and should take the form of a
constructor of a central MUSCLE 3 object that all other communcation
goes through.

The init function is passed (if necessary) the command line
arguments, and reads and removes the MUSCLE 3-specific ones. These
tell it where the Manager is, which it uses to initialise the MMP
Client. It is also passed a description of the kernel, which it
passes to the Manager via the MMP Client on registration.

The Coordination API uses the MMP Client to connect to the Manager,
and stores the information obtained via the Manager in the
Configuration Store and the Communication Engine.


-----------------
Configuration API
-----------------

Using the Configuration API, the client can test whether a given
parameter is set, which type it has (in statically typed languages),
and request its value. The Configuration API obtains this
information from the Configuration Store.


-----------------
Communication API
-----------------

The Communication API is used to send and receive messages. It
contains functions for sending and receiving messages, as well as
support for packing complex data structures for transport (using
MessagePack). It uses the Communication Engine to do the actual
work.


-------------
Execution API
-------------

The Execution API implements the Submodel Execution Loop, as well as
execution loops for other types of kernels. It allows the user to
define their model as a class with a set of member functions, one
for each operator. The library then takes care of calling these
functions in the correct order, and passing them messages. See
`LittleMuscle`_'s `submodel.py`_ for a prototype.


-----------
Logging API
-----------

The Logging API is used by the client to log information about its
progress, errors, etc. If something goes wrong in a distributed
system, it is often difficult to find out what happened and why.
Having log output easily available in a single location makes this
much easier, so MUSCLE 3 provides this convenience. Furthermore, the
logging system can be used to obtain basic performance information,
which can be used by the planner to allocate resources more
efficiently.


----------
MMP Client
----------

The MMP Client communicates with the Manager. Its code is partially
generated from the gRPC specification of the MUSCLE Manager
Protocol. It provides functions to the other modules for registering
the instance, getting peers, getting configuration information, and
sending log messages, and implements these by communicating with the
Manager. It is initialised with the network location of the Manager.


-------------------
Configuration Store
-------------------

The Configuration Store contains information about the configuration
of this instance. Like in the Manager, the basic container of
configuration information is a dictionary structure that maps the
name of a model parameter (a string) to a value, which is a string,
integer, floating point number, or nil (None, null).

Unlike the Manager, the Configuration Store contains only
configuration information for its own instance, but it maintains a
stack of these dictionaries. Lookup of a parameter value starts at
the dictionary on the top of the stack, and falls through if the
parameter is not found. A parameter can be set to nil explicitly
(thus overriding any value lower in the stack), or if it is not
present in any of the dictionaries, then it will be nil by default.

When an instance calls the Coordination API (see below) to register
itself, it sends a dictionary with parameters and their default
values. This becomes the bottom layer of its stack.


--------------------
Communication Engine
--------------------

The Communication Engine component of LibMuscle takes care of
communication with other instances. It keeps a list of endpoints,
with for each sending endpoint the location of the peer on the other
side of the conduit connected to the endpoint. This information is
passed to it by the Coordination API as part of starting up. It
sends and receives messages on these end points (as directed by the
Communication API), but does not know anything about the content of
the messages.

Actual communication is done by a TCP submodule, which knows how to
set up a connection to a peer given its network location, and
performs actual communication. In the future, we envision submodules
for other protocols as well, e.g. MPI.
