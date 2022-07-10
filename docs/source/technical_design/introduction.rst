========================
MUSCLE3 Technical Design
========================

------------
Introduction
------------

Computational science involves the development of simulation models of complex
natural systems. Often, several processes in such a system are relevant to the
research question being posed, and in many cases these processes act at
different scales in time and space. To model such a system, several submodels,
one for each process, are combined together into a multi-scale model.

To implement a multiscale model in software, some kind of subsystem is required
that is responsible for *coupling* the models. This subsystem ensures that the
submodels can exchange information when needed, that the model configuration
and parameters are available to the submodels, and in case of dynamic use of
compute resources, that the correct set of submodels is running when needed.
Thus, the coupling library provides coordination and communication in addition
to the computing done by the submodels.

MUSCLE3 is the third major version of the Multiscale Coupling Library and
Environment. MUSCLE is grounded in a solid theoretical basis provided by the
Multiscale Modelling Language (MML), which is being extended to include a
mechanism for running large, dynamically sized sets of submodels. Using MUSCLE
3, submodels written in different programming languages can be coupled
together, with data exchanged via a network to facilitate distributed
execution. As such, MUSCLE3 is a core component of the Multiscale Modelling
and Simulation Framework (MMSF) for high-performance distributed computing.


-------------------------------
Anatomy of a MUSCLE3 simulation
-------------------------------

A MUSCLE3 simulation run consists of a set of kernels (which include submodels
as well as other components), which are separate programs running independently
and exchanging information while doing so, and a manager that coordinates their
activity. The simulation starts with a start-up phase, during which the kernels
are connected to each other and settings are exchanged. Once all kernels are in
place and able to communicate, the execution phase starts. During the execution
phase, the kernels operate independently, exchanging information when needed.
The manager remains active to handle dynamic instantiation of new kernels, as
well as logging.

For execution across multiple high-performance computing (HPC) resources, a
separate program is usually required that forwards messages between the
clusters, due to constraints imposed by the network architecture (i.e.
firewalls that are in the way). This is the MUSCLE Transport Overlay (MTO).
Details about the MTO will be added to this document later.

MUSCLE3 provides four components for building a simulation. First is the
central manager, which keeps track of where kernels are executing and informs
them of each other's location, so that communication channels can be set up. It
also provides a central facility for kernel configuration, it does centralised
logging, and it starts extra kernels on demand.

LibMuscle is a library that submodels and other kernels link with, and which
provides them with all the functionality needed to be part of a MUSCLE3
simulation. LibMuscle will be available in several programming languages, so
that existing kernels can be used as-is, and so that users are free to choose a
suitable language.

Besides these two pieces of software, MUSCLE3 comprises two communication
protocols. The first is the MUSCLE Manager Protocol (MMP), which is used by
kernels to communicate with the manager. The second is the MUSCLE Data Protocol
(MDP), which is used for exchange of data between kernels.


----------------------
Simulation walkthrough
----------------------

In this section, a MUSCLE3 simulation is described in a bit more detail. As
described above, a MUSCLE simulation consists of a start-up phase followed by
an execution phase. We assume that the simulation is initiated by a launcher,
some external program that starts up the manager and an initial set of kernel
instances on one or more machines.

On start-up, the manager begins by reading a configuration file that describes
the model. This file is in the yMML format, a YAML-based representation of the
Multiscale Modelling Language. It contains a description of the submodels, the
connection topology between them, and a set of parameter values to run the
various submodels with. After having read the configuration file, the manager
waits for the instances to contact it.

When the instances start up, they contact the manager (having been passed its
network location via the command line) and register themselves, by providing
their name, a description of their communication endpoints, and the network
location they listen on). After registration, each instance will contact the
manager again to request the network locations of the peers with which it
should communicate. The manager passes the instance this information, which is
a combination of the contents of the yMML file and the information sent to it
by the other instances. Next, the instance will request a set of parameter
values from the manager, which returns the ones read from the yMML file. After
this, the kernel instance will start its execution.

During execution, an instance will normally execute in a loop, sending and
receiving messages before, during, and after loop execution. It does this in
terms of a set of endpoints. An endpoint can be either a sending endpoint, or a
receiving endpoint. These endpoints are a property of each kernel. Information
about which other instance each endpoint is connected to, is managed by
LibMuscle, and not seen or used by the user's code.

In some cases, dynamic instantiation of a kernel may be needed. This is
achieved by including a dynamic conduit in the model description. A dynamic
conduit connects a sending endpoint of a running instance, to a receiving
endpoint of an instance that is to be started on demand. When the sending
instance sends a message on the sending endpoint (which must happen through
LibMuscle), LibMuscle will contact the manager and ask it to provide a suitable
receiving submodel instance. The manager looks up what kind of instance to
provide, creates or reuses an instance, and returns the network location of the
new receiving instance. LibMuscle then sends it the message.

During execution, instances generate log messages that can be used for checking
progress and for debugging. If the log level of the message is at or above the
threshold set for local logging, it will be written to a log file on the
machine where the instance is running. If the log level is at or above the
threshold for central logging, then it will be sent to the manager for
recording in the central log file.


-----------------
Model description
-----------------

The description of a model comprises a description of its kernels, the
instances of those kernels that the running model is made of, and the
conduits that carry information between the instances. This information is read
by the manager from a configuration file in yMML format. In this section, the
model description is described in more detail.


Kernels
-------

A kernel is (in this context) a computer program that uses MUSCLE to
communicate with the outside world.  As a kernel executes, it runs through a
succession of *Operators*. The Multiscale Modelling Language specifies three
kinds of kernels: Submodels, Mappers, and Proxies, each with their own set of
operators and execution order. MUSCLE supports these specifically, but also
provides a generic interface that can be used if some other kind of kernel is
required.

A Submodel kernel has five operators, which are run through according to the
Submodel Execution Loop (SEL). In the SEL, a submodel, after startup, first
receives one or more messages that determine its initial state (f_init). Then,
it sends one or more messages describing (parts of) this initial state (O_i).
Next, it performs a state update, possibly receiving messages that provide
additional input (S). Next, it updates its boundary conditions, again possibly
receiving messages (B). Then, it loops back to sending messages describing the
new state.  After the boundary condition update, the submodel may leave the
loop if it is done, send one final set of messages describing its final state
(O_f), and end this present run. If needed, the submodel (as with any kernel)
may then be restarted from the beginning.

A Mapper has only a single operator, M, a set of receiving endpoints, and a set
of sending endpoints. A mapper with a single receiving endpoint and several
sending endpoints is a fan-out mapper; a mapper with several receiving
endpoints and a single sending endpoint is a fan-in mapper. A mapper first
receives one message on each of its receiving endpoints, and then sends one
message on each of its sending endpoints. The mapper may then be restarted, and
receive-and-send again. A mapper must send a message on each of its sending
endpoints whenever it receives messages on each of its receiving endpoints.

The Proxy is a new kind of kernel in MUSCLE3 with a single operator, P, and
four sets of conduits. It will be described in more detail later.


Endpoints
---------

Endpoints are used by kernels to communicate with the outside world. They have
a unique (for that kernel) name, an associated operator, and a data type.
Operators may come with restrictions on endpoints, e.g. the submodel's S
operator may only receive messages. A sending endpoint with associated operator
S is therefore invalid.


Instances
---------

An instance is a process, a kernel running on some computer. Models may contain
one or more (and even very many) instances of the same kernel, for example with
each instance calculating some part of the spatial domain. The model
description contains a list of all the instances comprising the model. Each
instance definition specifies which kernel it is an instance of, and it
contains configuration information for the kernel.

The configuration consists of three parts: the space and time scales of the
modelled process, MUSCLE3 built-in settings, and kernel parameters.

Scales in MUSCLE are defined by their grain (step or cell size), and extent
(total size). For a kernel operating on a grid, the space scales specify the
grid size. For kernels with a repeated solving step, the time scale specifies
the size of the time step and the overall duration of the simulation. Spatial
and temporal scales should be chosen with care, dependent on the spatial and
temporal characteristics of the modelled phenomenon.

MUSCLE3 built-in settings are settings that are used by LibMuscle, not by the
user-written kernel code. These include e.g. configuration of the logging
subsystem.

Finally, kernel parameters are defined by the maker of the kernel, and can be
any kind of model parameters or configuration.


Conduits
--------

Conduits connect instances, allowing them to exchange messages. More
specifically, a conduit connects a sending endpoint on a given instance to a
receiving endpoint on another instance.
