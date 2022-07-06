Current status
==============

The current release includes most of the necessary features to run multiscale
simulations in both non-distributed and distributed mode, in Python 3, C++ and
Fortran. This makes this release suitable for prototyping and learning to work
with MUSCLE 3 and multiscale modeling in general, and for production work using
Python, C++ and Fortran models.

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
needs to be run once for each time step of the macro-model. With MUSCLE, models
can be run repeatedly to make this possible. If the macro-model does not have a
fixed number of timesteps (e.g. because it runs until convergence, and it is not
known in advance when that occurs), then the number of required runs of the
micro-model is unknown on beforehand as well. MUSCLE will automatically
coordinate the model's execution in order to ensure that exactly the right
number of runs happen and no deadlocks occur.

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
configuration files (or worse, source files), which then need to be put into the
correct location for models to pick them up. With MUSCLE, settings can be
defined in the yMMSL file that defines the simulation to run, and queried in
each submodel. This simplifies deployment and collecting metadata, and ensures
that settings that are used in different models are always the same (unless
explicitly set to different values).

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
Currently, MUSCLE 3 supports Python 3, C++ and Fortran. While that covers quite
some existing models in computational science, support for other languages is
still needed. This mainly entails porting libmuscle, as the manager is a
separate program, and writing tools to manipulate yMMSL files is probably best
done in Python.

Next on the list in terms of language support are C and possibly Java and
Octave, then perhaps other languages. If you feel strongly about support for a
specific language, please `make an issue on GitHub
<https://github.com/multiscale/muscle3/issues>`_.

Distributed execution
`````````````````````
Distributed execution is now officially supported, although not yet widely
tested. If you want to experiment on your laptop or your supercomputer, please
have a look at the `Distributed Execution`_ section of the manual. MUSCLE 3 can
start all the submodels and other components within a cluster allocation through
the use of `QCG PilotJob <https://github.com/vecma-project/QCG-PilotJob>`_.

Dynamic instantiation
`````````````````````
Some simulations require varying amounts of compute resources over the course of
a run. For instance, the time taken by a set of micro-models may depend on the
state of the macro-model, which changes over the course of the simulation. In
these cases, it may be necessary to change the number of instances of the
micro-model during the simulation. MUSCLE 3 does not yet support this, but we
plan to extend it to do so in the future.

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
MUSCLE 3 contains a partial implementation of a simple profiler, which can
measure the amount of time it takes to send messages between the instances.
While measurements are taken and the information is sent to the manager, it is
not yet saved to disk for further processing and not yet supported in C++. This
should be a simple addition.

