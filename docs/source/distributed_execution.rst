Distributed execution
=====================

In the previous section, we created a simple macro-micro multiscale model with
MUSCLE3, and ran it as a single Python script. This section explains
how to go from there to running separate programs, possibly on multiple nodes.

Previously, we've seen that MUSCLE3 simulations are built out of components, which have
implementations. To get set up, we'll define those here, and add a third concept,
instance:

Component
  Coupled simulations are built out of components. A component simulates some real-world
  process, or it can perform some in-simulation job like data conversion, sampling, or
  load balancing. Components have ports, which can be connected using conduits.
  Components are abstract objects in the MUSCLE3 configuration.

Implementation
  An implementation is a computer program that implements a particular
  component. If you browse through the examples, you'll find implementations of
  the reaction and diffusion models in different programming languages. They all
  simulate the same thing in the same way though, and can be used to implement the same
  components.

Instance
  An instance is a running program. Instances are made by starting, or
  instantiating, an implementation. Components have an attribute called their
  *multiplicity* which specifies how many instances of the associated
  implementation there are. Often and by default this will be one, but for
  e.g. UQ ensembles or spatial scale separation many instances of a component
  may be required.


Making separate implementations
-------------------------------

Previously, we started a simulation by starting a single Python script that
contained all of the implementations and also the model configuration. For
distributed running, we want to run the models separately, so our script needs
to be split up. Doing that is very simple: just copy the model function (and
anything it depends on) to a new file, and add a main clause that runs it.  For
the reaction model of the previous example, that looks like this:

.. literalinclude:: examples/python/reaction.py
  :caption: ``docs/source/examples/python/reaction.py``
  :language: python


Note that the code is exactly the same, we've just removed everything related to
the diffusion model and to the coupling between them. We can do the same to the
diffusion model:

.. literalinclude:: examples/python/diffusion.py
  :caption: ``docs/source/examples/python/diffusion.py``
  :language: python


Again, it's exactly the same code as before, just split off into a separate
file.


yMMSL files
-----------

The third part of our coupled model is the coupling itself. In a distributed set-up,
this is not described in Python, but in a configuration file in the yMMSL format. yMMSL
is a text-based format, YAML in fact, so you can edit it with a normal text editor.

Like before, we'll need to describe the components and conduits, as well as the
settings. Additionally, we now need to tell MUSCLE3 how to start the programs we use as
implementations, and how many resources they'll each need.

It is often convenient to split your configuration over multiple files. That
way, you can easily run the same simulation with different settings for example:
just specify a different settings file while keeping the others the same.

The model
`````````

Here is a yMMSL file describing the model from our previous example. Note that it's one
directory up, in the ``examples/`` dir rather than under ``examples/python``.
This is because there are some examples that mix languages as well.

.. literalinclude:: examples/rd_model.ymmsl
  :caption: ``docs/source/examples/rd_model.ymmsl``
  :language: yaml


As you can see, this has all the same terms we saw in the Python version, but it's
written in YAML format. You can load a yMMSL file from Python using
`ymmsl.load
<https://ymmsl-python.readthedocs.io/en/stable/overview.html#reading-ymmsl-files>`_ and
save it back using `ymmsl.save
<https://ymmsl-python.readthedocs.io/en/stable/overview.html#writing-ymmsl-files>`_.

Let's have a look at this file:

.. code-block:: yaml

  ymmsl_version: v0.2

  models:
    reaction_diffusion:
      description: |
        # Reaction-Diffusion model with time scale separation.

        The diffusion model is run at a much lager timestep than the reaction model,
        making this a multiscale model with the diffusion model simulating the macro
        dynamics and the reaction model the micro dynamics.


This specifies the version of the file format (``v0.2`` is the current version), and the
name of the model. yMMSL files can contain multiple model definitions, but here we have
only one. The model has a description, which is a string that's formatted here using the
``|`` format. This is standard YAML syntax indicating a multi-line string. You can and
should use MarkDown formatting here.

.. code-block:: yaml

  components:
    macro:
      ports:
        o_i: state_out
        s: state_in
      description: |
        This is the macro model, which calculates the diffusion
    micro:
      ports:
        f_init: initial_state
        o_f: final_state
      description: |
        This is the micro model, which calculates the reaction


We have seen the ``macro`` and ``micro`` components before. They have the same ports and
description as in Python.

If a component has multiple ports for an operator, then the names can be added to the
line separated by spaces, or you can specify a list of them in one of these ways:

.. code-block:: yaml

  f_init: port1 port2
  o_i:
  - port3
  - port4
  o_f: [port5, port6]


In this case, there is at most one port per operator.

.. code-block:: yaml

  conduits:
    macro.state_out: micro.initial_state
    micro.final_state: macro.state_in


Here are the conduits that connect the models together. The ports used here
should match those given above, of course. As before, ``macro`` sends messages
on its ``state_out`` port to ``micro``'s ``initial_state``, and ``micro`` sends
its answer on its ``final_state`` port, which is routed to ``macro``'s
``state_in``.

Like in Python, we'll need some implementations. These can be specified directly for
each component like this:

.. code-block:: yaml

  components:
    micro:
      ports:
        f_init: initial_state
        o_f: final_state
      implementation: reaction_python


Usually, you have specific models that you're connecting together, and then this is the
easiest way to specify them.

In this case we have many examples that all run this model, but with implementations
written in different languages. To avoid duplication, we've made ``rd_model.py``
generic, and to run the model with Python implementations we have a second file
``rd_python.py``:

.. code-block:: yaml

  ymmsl_version: v0.2

  imports:
  - from rd_model import implementation reaction_diffusion
  - from rd_programs import implementation diffusion_python
  - from rd_programs import implementation reaction_python

  custom_implementations:
    reaction_diffusion.macro: diffusion_python
    reaction_diffusion.micro: reaction_python


Here, we import the ``reaction_diffusion`` model from ``rd_model``, and the
implementations we want to use from ``rd_programs``. Then we use the
``custom_implementations`` section to specify which implementation should be used for
which component of the model.

Note the syntax: there's the name of the model we want to customise,
``reaction_diffusion``, then a period, then the name of the component within that model
whose implementation we want to set, ``macro``. Then a colon, and the name of the
implementation ``diffusion_python``.


Settings
````````

To simulate a specific system, we'll need to configure the model with some settings.
These are in a file named ``rd_settings.ymmsl``:

.. literalinclude:: examples/rd_settings.ymmsl
  :caption: ``docs/source/examples/rd_settings.ymmsl``
  :language: yaml


This matches what we've seen before in the integrated Python example, it's now
just written up as YAML.


Programs
````````

To run the simulation MUSCLE3 will have to start our Python programs, and we need to
tell it how to do that. This is done by some definitions in ``rd_programs.ymmsl``, which
we imported above. Note that this file actually contains definitions for all of our
programs, but we'll focus on the ``reaction_python`` one here:

.. code-block:: yaml

  programs:
    reaction_python:
      ports:
        f_init: initial_state
        o_f: final_state
      supported_settings:
        t_max: float  Time point at which to end the simulation
        dt: float     Time step size
        k: float      Reaction coefficient
      description: Reaction model implemented in Python
      executable: python
      args: <muscle3_src>/docs/source/examples/python/reaction.py

The first thing to note here is that there are three kinds of metadata: ports, supported
settings, and a description.

Programs usually have a fixed set of ports on which they expect to communicate, and
which are hard-coded into them. These ports can be documented here, and you should do so
because this will allow MUSCLE3 to check that the program actually fits with the
component it is implementing, and give an easy to understand error message rather than a
crash or a hang.

The same goes for any MUSCLE3 settings that the program uses. If you list them under
``supported_settings``, with their type and a description, then users of your program
can quickly see what's what, and MUSCLE3 can check for settings that have the wrong type
and give a nice error message. Supported types are ``str``, ``bool``, ``int``,
``float``, ``[int]`` (a list of ints), ``[float]``, and ``[[float]]`` (list of lists of
floats), and note that the description is separated from the type by whitespace. In
particular, don't put a ``#`` in front of the description, because that will make it
into a YAML comment and make it invisible to the documentation tools.

Finally, there's a description, which is very brief here but for a real model should be
more extensive, explaining what the model does and how to use it. 

Next is some information on how to run the program.  As you can see, there are some
absolute paths here, with a prefix shown here as ``<muscle3_src>``. If you've run
``make`` in the ``docs/source/examples/`` directory then you should have a version of
this file with the correct paths for your local setup.

There are two programs shown here, which the components above refer to by
name. They are Python scripts, so we need to run ``python /path/to/reaction.py``
or equivalent for the ``diffusion.py`` script, and that is exactly these
definitions do. Of course, it's also possible to add a ``#!/usr/bin/env
python3`` line to the top of the Python script and start it directly as an
executable.

The scripts have some dependencies, which will be installed in a virtual
environment in which we'll run the whole simulation, so we don't need to do any
other environment setup here, but MUSCLE3 is capable of running each
program in a separate environment if needed. See `the yMMSL
documentation on programs
<https://ymmsl-python.readthedocs.io/en/stable/api.html#ymmsl.v0_2.Program>`_
for more information on how to specify a virtual environment, set environment variables,
load environment modules, and more.

Resources
`````````

Finally, we need to tell MUSCLE3 which resources each model instance should be
given. This information is contained in ``rd_resources.ymmsl``:

.. literalinclude:: examples/rd_resources.ymmsl
  :caption: ``docs/source/examples/rd_resources.ymmsl``
  :language: yaml


In this case, the implementations are single-threaded Python
scripts, so we specify one thread each. See `the yMMSL documentation on
resources
<https://ymmsl-python.readthedocs.io/en/master/ymmsl_python.html#resources>`_
for other options, including for OpenMP and MPI.


Starting the simulation
-----------------------

With the above in place, we now have all the pieces we need to start a
distributed simulation. We do this by starting the MUSCLE3 manager and giving it
the configuration files. It will then start the needed model instances, help
them to find each other, and distribute the settings to them. The instances will
then connect to each other via the network and run the simulation.

The manager is included with the Python version of MUSCLE3. Running ``make`` or
``make python`` in the ``docs/source/examples`` directory will create a virtual
env with MUSCLE3 and all the dependencies needed by the examples installed.
With that set up, you can run the simulation from the ``docs/source/examples``
directory like this:

.. code-block:: bash

  . python/build/venv/bin/activate
  YMMSL_PATH=. muscle_manager --start-all rd_python.ymmsl rd_settings.ymmsl rd_resources.ymmsl


(The YMMSL_PATH variable points the manager to the ``rd_model.ymmsl`` and
``rd_programs.ymmsl`` we are importing from.)

This will start the manager, run the simulation, plot the results on the screen,
and when you close the plot, finish the simulation. It will also produce a
directory named ``run_reaction_diffusion_<date>_<time>`` in which some
output is written. Have a look at the ``muscle3_manager.log`` file for an
overview of the execution, or see ``instance/<instance>/stderr.txt`` for log
output of a particular instance (we use the default Python logging configuration
here, which writes to standard error, which is redirected to this file by the
manager).

If you want, you can change the log levels in ``rd_settings.ymmsl`` to ``DEBUG``
and re-run the simulation to have a more detailed look at what's going on. The
remote log level setting determines the minimum severity a message needs to have
to be sent from the instance to the manager to be included in the manager log.
The local log level determines whether the message will be logged to the local
Python logger. This is also very useful if something goes wrong and you need to
debug, of course.


High-Performance Computing
--------------------------

Coupled simulations often take a significant amount of compute resources,
requiring the use of High-Performance Computing (HPC) facilities. MUSCLE3 has
support for running inside of an allocation on an HPC cluster running the SLURM
scheduling system. It can determine the available resources (nodes and cores),
suballocate them to the various instances required to run the simulation, and
start each instance on its allocated resources.

Determining resource requirements
`````````````````````````````````

The MUSCLE Manager will automatically detect when it's inside of a SLURM
allocation, and instantiate programs accordingly. However, that
allocation still needs to be made by the user, and to do that we need to know
how many resources to request. Since instances may share resources (cores) in
some cases, this is not easy to see from the configuration.

Fortunately, MUSCLE3 can do this for us, using the ``muscle3 resources``
command:

.. code-block:: bash

  muscle3 resources --cores-per-node <n> <ymmsl files>


This will print a single number, the number of nodes to allocate, which can then
be passed to ``sbatch --nodes <n>``.

For `--cores-per-node`, you should pass the number of cores (not hardware
threads) that each node in your cluster has. This can usually be found in the
documentation, or else ask your administrator.

For example, for the Python example above, we can run:

.. code-block:: bash

  muscle3 resources --cores-per-node 16 rd_model.ymmsl rd_settings.ymmsl rd_programs.ymmsl rd_resources.ymmsl


and be informed that we'll need only a single node. (``rd_settings.ymmsl`` is
actually redundant here and could be omitted, the analysis is based only on the
model components, conduits, programs and resources.)

To get more insight into how the instances will be divided over the available
resources, you can use the ``-v`` option to enable verbose output. For the
Python model, this prints:

.. code-block::

    A total of 1 node will be needed, as follows:

    macro: Resources(node000001: 0)
    micro: Resources(node000001: 0)


As we can see, the models are allocated a single core each (they are both
single-threaded), and MUSCLE3 has determined that they can share a core because
they won't be computing at the same time due to the macro-micro multiscale
coupling pattern. For more interesting output, try this command on the example
from the :ref:`Uncertainty Quantification` section, and increase the number of
instances a bit.

To determine whether models can overlap, MUSCLE3 assumes that programs do not do
any significant amount of computation before receiving the ``F_INIT`` messages, in
between having sent the ``O_I`` messages and receiving the ``S`` messages, and after
having sent the ``O_F`` messages. If a program does do this, then the
simulation will still run, but different models may end up competing for the
same cores, which will slow down the simulation. To avoid this, a program
may be marked as not being able to share resources:

.. code-block::

  programs:
    industrious:
      executable: /home/user/models/industrious
      execution_model: openmpi
      can_share_resources: false


If a program is marked as such, the MUSCLE Manager will give it a set of
cores of its own, so that it can compute whenever it wants.

Loading modules
```````````````

On an HPC machine, you often need to load some environment modules to make
needed software available. If a program needs to have modules available
to run, then you should use the ``modules`` option when describing the
program:

.. code-block:: yaml

  programs:
    on_hpc:
      modules: GCC/14.3.0 OpenMPI/5.0.3
      executable: /home/user/models/mpi_model
      execution_model: openmpi


Submitting jobs
```````````````

HPC clusters typically serve large numbers of users, who all want to run
calculations. The available compute resources are managed by a *scheduler*, to
which users can submit work in the form of *jobs*. These jobs are then put into
a queue, and run whenever it's their turn and sufficient resources are
available. MUSCLE3 currently supports only the SLURM scheduler, which
fortunately is used almost everywhere.

To submit a SLURM job, you use the `sbatch` command with a *batch script* which
describes what you want to do. A complete introduction is beyond the scope of
this documentation, so if you're new to this please browse on over to `HPC
Carpentry <https://carpentries-incubator.github.io/hpc-intro/>`_ for an
introduction.

For MUSCLE3 simulations this works the same as for any other job. Of course, a
coupled simulation is a bit more complicated than the usual SLURM/MPI scenarios
in which only a single program is run, but MUSCLE3 takes care of all the
details, so this is actually a bit easier than usual. You do need to make
sure that SLURM actually makes all the resources it allocates to you available
to MUSCLE3. (This sounds silly, but by default SLURM will assume that you want
to run one task per node, thus using only a single core on each of your nodes,
instead of all of them.)

All this gets complicated if you try to read the SLURM documentation, so here's
the gist: you need to either 1) specify a number of nodes, and how many tasks
you want to have on each node, or 2) specify a number of tasks. Either way will
suit MUSCLE3 fine, but don't mix them up or SLURM will get confused and then
confuse you too.

Here's an example batch script that does option 1), nodes first:


.. code-block:: bash

  #!/bin/bash

  #SBATCH -J my_muscle3_job
  #SBATCH --time=1:00:00
  #SBATCH --nodes=4
  #SBATCH --ntasks-per-node=16

  . /path/to/muscle3-venv/bin/activate
  muscle_manager --start-all model.ymmsl


In this case, we're assuming that each node has 16 cores available, and we tell
SLURM that we'll use all of them. Whether that actually happens depends on the
MUSCLE3 configuration, but this way at least all of them will be available to
MUSCLE3.

Note that this number `16` should match what you passed to the
`--cores-per-node` option of `muscle3 resources` above, and `4` would be the
number of nodes it told you it would need.

To set up the same job using tasks, option 2), you could do this:

.. code-block:: bash

  #!/bin/bash

  #SBATCH -J my_muscle3_job
  #SBATCH --time=1:00:00
  #SBATCH --ntasks=64

  . /path/to/muscle3-venv/bin/activate
  muscle_manager --start-all model.ymmsl


Assuming that SLURM has been configured with 16 so-called *slots* per node, it
will then give you 64 / 16 = 4 nodes with all cores available.

If the MUSCLE3 manager complains about oversubscribing in the log file, then
something went wrong and you did not get enough resources. MUSCLE3 will still
try to run the simulation for you, but different model instances will likely end
up trying to use the same cores at the same time, which will cost performance.

The manager logs which resources it detected, any discrepancies between what
SLURM claims we got and what we actually have access to, and which instances it
assigned to which cores, which will hopefully help solve the problem. (You can
use `--log-level DEBUG` to get more details.)


Hyperthreading
``````````````

Hyperthreading, or symmetric multithreading (SMT) to use the generic term, is a
hardware feature that allows multiple processes to share a core more
efficiently. It does not really add more compute resources however, and using it
may speed up a simulation, but can also slow it down. In practice the performance
difference is typically somewhere between -30% and +30%, and predicting in
advance whether it will help or hurt is impossible even for experts (as usual
with this kind of low-level optimisation).

MUSCLE3 currently assigns a full core to each thread or MPI process, regardless
of whether the hardware supports SMT and whether it is enabled. (Note that this
has changed: versions 0.7.2 and earlier would assign hardware threads if
available and whole cores if not.)

We could add support for hyperthreading on a per-component basis in the future
however, if there is a need (as well as other granularities like sockets or NUMA
domains).  Please make an issue on GitHub if you'd like to see this, so that we
know someone is interested.

