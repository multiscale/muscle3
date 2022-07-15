Distributed execution
=====================

In the previous section, we created a simple macro-micro multiscale model with
MUSCLE3, and ran it as a single Python script. This section briefly explains
how to go from there to a distributed simulation, possibly on multiple nodes.

Note that distributed simulations are not as easy to use as we would like them
to be yet. All the necessary pieces are in place however. Below, we explain how
they work. If you want to run the example below using a premade script, then you
can go to the ``docs/examples/`` directory in the source code, and set up and
run the Python example like this:

.. code-block:: bash

  docs/examples$ make python
  docs/examples$ ./reaction_diffusion_python.sh


Below, we explain how it works and how to run it by hand. First though, a bit of
terminology:

Component
  Coupled simulations are built out of components. A component is a model, or
  some none-model helper component that e.g. converts data, samples parameters,
  or does load balancing. Components have ports, which can be connected by
  conduits. Components are abstract things in the MUSCLE3 configuration.

Implementation
  An implementation is a computer program that implements a particular
  component. If you browse through the examples, you'll find implementations of
  the reaction and diffusion models in different programming languages. They all
  implement the same model (component) though.

Instance
  An instance is a running program. Instances are made by starting, or
  instantiating, an implementation. Components have an attribute called their
  *multiplicity* which specifies how many instances of the associated
  implementation there are. Often, and by default, this will be one but for
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

In a distributed set-up, the manager and each instance run as separate programs,
communicating via the network. To make this work, we need to describe how the
different models need to be connected, how the programs implementing them need
to be started, and we may want to configure them by specifying some simulation
settings. All this information is stored in one or more yMMSL files. This is the
YAML version of the Multiscale Modelling and Simulation Language, in case you
were wondering about the acronym.

It is often convenient to split your configuration over multiple files. That
way, you can easily run the same simulation with different settings for example:
just specify a different settings file while keeping the others the same.

Here is a yMMSL file describing our previous example. Note that it's one
directory up, in the ``examples/`` dir rather than under ``examples/python``.
This is because there are some examples that mix languages as well.

.. literalinclude:: examples/rd_python.ymmsl
  :caption: ``docs/source/examples/rd_python.ymmsl``
  :language: yaml


As you can see, this looks like the object representation, although there are a
few more things being specified. You can load a yMMSL file from Python using
`ymmsl.load
<https://ymmsl-python.readthedocs.io/en/stable/overview.html#reading-ymmsl-files>`_ and
save it back using `ymmsl.save
<https://ymmsl-python.readthedocs.io/en/stable/overview.html#writing-ymmsl-files>`_.

Let's have a look at this file:

.. code-block:: yaml

  ymmsl_version: v0.1

  model:
    name: reaction_diffusion_python


This specifies the version of the file format (``v0.1`` is currently the only
version), and the name of the model.

.. code-block:: yaml

  components:
    macro:
      implementation: diffusion_python
      ports:
        o_i: state_out
        s: state_in

    micro:
      implementation: reaction_python
      ports:
        f_init: initial_state
        o_f: final_state


We have seen the ``macro`` and ``micro`` components before. The implementations
have an added ``_python`` in their names here, because there are also examples
in other languages. A new thing is that the ports are now declared in the
configuration (they are also still in the code, and need to be). The manager
needs this information to be able to assign resources to the components. You
can write a list of ports if you have more than one port for an operator, see
`ymmsl.Ports
<https://ymmsl-python.readthedocs.io/en/develop/api.html#ymmsl.Ports>`_.

.. code-block:: yaml

  conduits:
    macro.state_out: micro.initial_state
    micro.final_state: macro.state_in


Here are the conduits that connect the models together. The ports used here
should match those given above, of course. As before, ``macro`` sends messages
on its ``state_out`` port to ``micro``s ``initial_state``, and ``micro`` sends
its answer on its ``final_state`` port, which is routed to ``macro``s
``state_in``.

.. code-block:: yaml

  resources:
    macro:
      threads: 1
    micro:
      threads: 1


Finally, we need to tell MUSCLE3 which resources each model instance should be
given. For the moment, only the number of threads or MPI processes can be
specified. In this case, the implementations are single-threaded Python
scripts, so we specify one thread each. See `the yMMSL documentation on
resources
<https://ymmsl-python.readthedocs.io/en/master/ymmsl_python.html#resources>`_
for other options.

To be able to instantiate this model, we still need to define the
``diffusion_python`` and ``reaction_python`` implementations. We also need some
settings for the configuration. These are specified in two additional files,
``rd_implementations.ymmsl`` and ``rd_settings.ymmsl``. The former actually
contains definitions for all the example implementations, but we'll focus on the
parts that define the Python ones we're using here:

.. code-block:: yaml

  implementations:
    reaction_python:
      virtual_env: <muscle3_src>/docs/source/examples/python/build/venv
      executable: python
      args: <muscle3_src>/docs/source/examples/python/reaction.py

    diffusion_python:
      virtual_env: <muscle3_src>/docs/source/examples/python/build/venv
      executable: python
      args: <muscle3_src>/docs/source/examples/python/diffusion.py


As you can see, there are some absolute paths here, with a prefix shown here as
``<muscle3_src>``. If you've run ``make`` in the ``docs/source/examples/``
directory then you should have a version of this file with the correct paths for
your local setup.

There are two implementations shown here, which the components above refer to by
name. They are Python scripts, and they have some dependencies which are
installed in the virtual environment created earlier by ``make``. So in order to
run them, that virtualenv has to be activated, and then we can run ``python
/path/to/reaction.py`` or equivalent for the ``diffusion.py`` script, and that
is exactly these definitions do. Of course, it's also possible to add a
``#!/usr/bin/env python3`` line to the top of the Python script and start it
directly as an executable.

Finally, the settings in ``rd_settings.ymmsl``:

.. literalinclude:: examples/rd_settings.ymmsl
  :caption: ``docs/source/examples/rd_settings.ymmsl``
  :language: yaml


This matches what we've seen before in the integrated Python example, it's now
just written up as YAML.


Starting the simulation
-----------------------

With the above in place, we now have all the pieces we need to start a
distributed simulation. We do this by starting the MUSCLE3 manager and giving it
the configuration files. It will then start the needed model instances, help
then to find each other, and distribute the settings to them. The instances will
then connect to each other via the network and run the simulation.

The manager is included with the Python version of MUSCLE3. Running ``make`` or
``make python`` in the ``docs/source/examples`` directory will create a virtual
env with MUSCLE3 and all the dependencies needed by the examples installed.
With that set up, you can run the simulation from the ``docs/source/examples``
directory like this:

.. code-block:: bash

  . python/build/venv/bin/activate
  muscle_manager --start-all rd_implementations.ymmsl rd_python.ymmsl rd_settings.ymmsl


This will start the manager, run the simulation, plot the results on the screen,
and when you close the plot, finish the simulation. It will also produce a
directory named ``run_reaction_diffusion_python_<date>_<time>`` in which some
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
requiring the use of High-Performance Computing facilities. MUSCLE3 has support
for running inside of an allocation on an HPC cluster running the SLURM
scheduling system. It can determine the available resources (nodes and cores),
suballocate them to the various instances required to run the simulation, and
start each instance on its allocated resources. (With thanks to its friend
`QCG-PilotJob <https://qcg-pilotjob.readthedocs.io/en/stable/>`_.)

Determining resource requirements
`````````````````````````````````

The MUSCLE Manager will automatically detect when it's inside of a SLURM
allocation, and instantiate implementations accordingly. However, that
allocation still needs to be made by the user, and to do that we need to know
how many resources to request. Since instances may share resources (cores) in
some cases, this is not easy to see from the configuration.

Fortunately, MUSCLE3 can do this for us, using the ``muscle3 resources``
command:

.. code-block:: bash

  muscle3 resources --cores-per-node <n> <ymmsl files>


This will print a single number, the number of nodes to allocate, which can then
be passed to ``sbatch -N <n>``.

For example, for the Python example above, we can run:

.. code-block:: bash

  muscle3 resources --cores-per-node 16 rd_implementations.ymmsl rd_python.ymmsl rd_settings.ymmsl


and be informed that we'll need only a single node. (``rd_settings.ymmsl`` is
actually redundant here and could be omitted, the analysis is based only on the
model components, conduits, implementations and resources.)

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

To determine whether models can overlap, MUSCLE3 assumes that models do not do
any significant amount of computation before receiving the F_INIT messages, in
between having sent the O_I messages and receiving the S messages, and after
having sent the O_F messages. If an implementation does do this, then the
simulation will still run, but different models may end up competing for the
same cores. This will slow down the simulation. To avoid this, an implementation
may be marked as not being able to share resources:

.. code-block::

  implementations:
    industrious:
      executable: /home/user/models/industrious
      execution_model: openmpi
      can_share_resources: false


If an implementation is marked as such, the MUSCLE Manager will give it a set of
cores of its own, so that it can compute whenever it wants.

Loading modules
```````````````

On an HPC machine, you often need to load some environment modules to make
needed software available. If an implementation needs to have modules available
to run, then you should use the ``modules`` option when describing the
implementation:

.. code-block:: yaml

  implementations:
    on_hpc:
      modules: c++ openmpi
      executable: /home/user/models/mpi_model
      execution_model: openmpi


Hyperthreading
``````````````

If hyperthreading is enabled on the HPC cluster you are running on, then SLURM
will allocate threads, not cores. This may give you a performance boost, it may
make no difference, or it may decrease performance. To disable hyperthreading
and allocate full physical cores, you can pass ``--ntasks-per-node=<x>`` to
sbatch, with ``<x>`` being the number of physical cores per node. This will
cause SLURM to tell MUSCLE3 (via QCG-PilotJob) to only use the first ``x``
virtual cores on each machine, which then get a physical core to themselves
because the second set of virtual cores isn't used.

