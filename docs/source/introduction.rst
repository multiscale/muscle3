Introduction
============

Welcome to MUSCLE 3!

MUSCLE 3 is the third incarnation of the Multiscale Coupling Library and
Environment, and the successor to MUSCLE 2. Its purpose is to make creating
coupled multiscale simulations easy, and to then enable efficient Uncertainty
Quantification of such models using advanced semi-intrusive algorithms.

MUSCLE 3 uses the Multiscale Modelling and Simulation Language (MMSL) to
describe the structure of a multiscale model. MMSL can be expressed in the form
of a diagram (gMMSL; not yet implemented) or as a YAML file (yMMSL; this is
convenient both for people and for software). The MMSL lets one describe which
*compute elements* (submodels, scale bridges, data converters, UQ components,
etc.) a multiscale model consist of, how many instances of each we need, and how
they are wired together.

MUSCLE 3 is intended to scale from your laptop to the exascale. At the low end,
it supports a non-distributed but parallel mode in which an entire multiscale
simulation, including all compute element implementations and the MMSL
configuration, is in a single (short) Python file. Next is a distributed mode
where the manager and compute element instances are started on multiple nodes
in a cluster, and communicate directly with one another. Beyond that, additional
components and optimisations are envisioned that would allow scaling to huge
machines or combinations of multiple machines. Our goal is to make the
transitions between these modes as smooth as possible, so that extra compute
power can be added gradually, as needed.

MUSCLE 3 consist of three components: **libmuscle**, **ymmsl-python**, and
**muscle_manager**. **Libmuscle** is a library that is used to connect compute
element implementations (e.g. new or existing models) to a coupled simulation.
It offers functions for sending and receiving messages to and from the outside
world, determining whether to restart the model at the end of its run, and
various utilities.

**ymmsl-python** is a Python library that contains class definitions to
represent an MMSL model description. It supports loading a yMMSL file and
converting it to objects, and saving objects to a yMMSL file. Input is validated
and a clear error message is provided in case of errors, and output is formatted
for good readability, courtesy of the `YAtiML <https://yatiml.readthedocs.io>`_
library.  yMMSL files can also contain parameter settings, so that all the
information needed for a simulation run can be described in a single file.

**muscle_manager** is the central run-time component of MUSCLE 3. It is started
together with the compute element intances, and provides a central coordination
point that the instances use to find each other. The manager also collects log
messages from the individual instances to aid in debugging, and some profiling
information to aid in scheduling and performance optimisation.


Current status
==============

The current release includes most of the necessary features to run multiscale
simulations in non-distributed mode, in Python 3. This makes this release
suitable for prototyping and learning to work with MUSCLE 3 and multiscale
modeling in general, and for production work using non-compute intensive Python
models.

In particular, MUSCLE 3 currently provides the following features:

Coupling different submodel instances
-------------------------------------

MUSCLE connects simultaneously running instances of different submodels together
based on an MMSL description of how to do so. Single instances can be connected
to each other, or to sets of instances via so-called vector ports. MUSCLE allows
peer instances to find each other, and then transmit messages between themselves
in a peer-to-peer fashion. Communication between the models therefore does not
suffer from a bottleneck created by a central component.

Spatial and temporal scale separation and overlap
-------------------------------------------------

For a macro-micro coupled model with time scale separation, the micro-model
needs to be run to convergence for each time step of the macro-model. With
MUSCLE, models can be run repeatedly to make this possible. If the macro-model
does not have a fixed number of timesteps (e.g. because it runs until
convergence, and it is not known in advance when that occurs), then the number
of required runs of the micro-model is unknown on beforehand as well. MUSCLE
will automatically coordinate the model's execution in order to ensure that
exactly the right number of runs happen and no deadlocks occur.

For time scale overlap, the models run simultaneously and exchange information
via MUSCLE while running, but interpolation may be needed to synchronise the
data that is exchanged. Messages passed between models via MUSCLE carry
simulation-time timestamps that allow you to implement a suitable interpolation
component.

For spatial scale separation, usually many instances of the micro-model need to
be run to cover the macro-scale domain, and they need to be linked to the
macro-model. This too can be described with the MMSL and implemented using
MUSCLE.

For adjacent spatial scales, information needs to be exchanged between the
micro-model instances. This effectively equivalent to domain decomposition,
which MUSCLE 3 cannot (yet) do. In practice, compute-intensive models usually do
this internally anyway, so this is not a major limitation, although it would be
nice to have.

MUSCLE also supports time-domain adjacency, which is to say a process that
occurs after another one. In this way, it is semantically a superset of a
scientific workflow system.

Settings management
--------------------

Most models have some, or many, model parameters and other settings that
determine how the simulation proceeds. In a large coupled simulation, managing
these settings is tedious, as they need to be distributed over various
configuration files, which then need to be put into the correct location for
models to pick them up. With MUSCLE, settings can be defined in the yMMSL file
that defines the simulation to run, and queried in each submodel. This
simplifies deployment and collecting metadata, and ensures that settings that
are used in different models are always the same (unless explicitly set to
different values).

For Uncertainty Quantification and Sensitivity Analysis, an ensemble is usually
run, with the values of some parameters varying amongst the ensemble members.
With MUSCLE 3, components can be introduced into the simulation that connect to
a set of instances and inject different values for some of the settings into
each one. This makes it possible to implement advanced semi-intrusive methods
for efficient UQ and SA of multiscale models.

Combining features
------------------

The most powerful feature of the MMSL, and MUSCLE 3, is the ability to
arbitrarily combine the above features in a single model. For instance, if your
macro-micro model exhibits both time scale and spatial scale separation, then
you can have a set of instances that each are reused many times. You can then
make a set of each of these (i.e. a set of macro-model instances, and a set of
sets of micro-model instances) and attach a UQ sampler to the macro-model in
order to run an Uncertainty Quantification. The overlaid parameters will then
be propagated automatically by MUSCLE 3 to the correct micro-model instances.

Other scenarios could include combining two macro-micro set-ups into a
macro-meso-micro model, or connecting a macro-model to an ensemble of stochastic
micro-models via a component that replicates the message from the macro-model to
each micro-model instance, and another component that calculates the ensemble
mean of the results and passes it back to the macro-model.

This feature is important because MUSCLE 3 is a tool for scientific research.
While the MUSCLE 3 developers cannot predict what you will invent in the future,
its flexibility greatly increases the probability that you will be able to use
MUSCLE 3 to implement it.


Ongoing development
-------------------

Language support
````````````````
Currently, MUSCLE 3 is entirely written in Python 3, and it has no support for
other programming languages. As Python's performance is generally not sufficient
for compute-intensive models, support for other languages is needed. This mainly
entails porting libmuscle, as the manager is a separate program, and writing
tools to manipulate yMMSL files is probably best done in Python.

We have started work on a C++ implementation of libmuscle, which will have
wrappers for C, Fortran, probably Java and perhaps other languages. If you feel
strongly about support for a specific language, please `make a ticket on GitHub
<https://github.com/multiscale/muscle3/issues>`_.

Distributed execution
`````````````````````
Distributed execution is not yet officially supported. While libmuscle is
currently capable of using TCP for communication between submodels, more testing
is needed to ensure that instances can reliably find each other in different
networking environments. If you want to experiment on your laptop or your
supercomputer, please have a look at the `Distributed execution`_ section of the
manual.

In order to avoid writing job scripts and staging files manually, some kind of
launcher is needed. We are collaborating with the `VECMA project
<https://www.vecma.eu>`_ on getting MUSCLE 3 support into `FabSim3
<https://fabsim3.readthedocs.io/en/latest/>`_.


Dynamic instantiation
`````````````````````
Some simulations require varying amounts of compute resources over the course of
a run. For instance, the time taken by a set of micro-models may depend on the
state of the macro-model, which changes over the course of the simulation. In
these cases, it may be necessary to change the number of instances of the
micro-model during the simulation. MUSCLE 3 does not yet support this. Some kind
of pilot job framework, such as `QCG PilotJob
<https://github.com/vecma-project/QCG-PilotJob>`_ will have to be integrated
with MUSCLE 3 to make this work.

It should be noted that in most cases, the resources have been allocated to the
user by a scheduler, and whether or not they are used does not affect the cost
of the simulation in core hours. Energy use is of course affected, and in some
cases wall-clock time can be reduced by redistributing the available resources
over fewer needed instances. Also, when running on a cloud, it may be possible
to return resources when they are no longer needed, and avoid paying for them.

The simple case of repeated instantiation of a micro-model is taken care of by
the model reuse facility that MUSCLE 3 does offer; dynamic instantiation is not
needed for this.

Profiling
`````````

MUSCLE 3 contains most of the implementation of a simple profiler, which can
measure the amount of time it takes to send messages between the instances.
While measurements are taken and the information is sent to the manager, it is
not yet saved to disk for further processing. This should be a simple addition.


Installing
==========

The Python 3 version of MUSCLE 3 requires Python 3.5 or 3.6; 3.7 may work but is
untested. It is an ordinary Python package, which may be installed via

```
pip3 install muscle3
```

This will also install ymmsl-python, and any required dependencies.

To install ymmsl-python without muscle3, you can use:

```
pip3 install ymmsl
```

