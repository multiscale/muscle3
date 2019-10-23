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
various utilities like centralised settings (for convenience and UQ),
centralised logging (to make debugging easier) and basic profiling.

**ymmsl-python** is a Python library that contains class definitions to
represent an MMSL model description. It supports loading a yMMSL file and
converting it to objects, and saving objects to a yMMSL file. Input is validated
and a clear error message is provided in case of errors, and output is formatted
for good readability, courtesy of the `YAtiML <https://yatiml.readthedocs.io>`_
library.  yMMSL files can also contain settings, so that all the information
needed for a simulation run can be described in a single file.

**muscle_manager** is the central run-time component of MUSCLE 3. It is started
together with the compute element intances, and provides a central coordination
point that the instances use to find each other. The manager also collects log
messages from the individual instances to aid in debugging, and some profiling
information to aid in scheduling and performance optimisation.

