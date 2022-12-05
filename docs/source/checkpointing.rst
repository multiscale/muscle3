Simulation checkpoints
======================

When you execute a long-running simulation, it can be very helpful to store the
state of a simulation at certain intervals. For example, your simulation running
on a HPC cluster may crash, just before it's finished, due to insufficient
memory available. Instead of restarting this simulation from scratch, you could
restart it -- with an increased memory allocation -- from a checkpoint, which
would save a lot of compute time!

Checkpointing in distributed simulations is difficult. Fortunately, MUSCLE3
comes with built-in checkpointing support. This page describes in detail how to
use the MUSCLE3 checkpointing API, how to specify checkpoints in the workflow
configuration and how to resume a workflow.

In the :ref:`user tutorial`, you can read about the checkpointing concepts and
how to use the API when running and resuming MUSCLE3 simulations. This is
followed by a :ref:`developer tutorial`, which explains how to add checkpointing
capabilities to your MUSCLE3 component. Finally, the :ref:`checkpointing
deep-dive` describes in detail the (inner) working of checkpointing in MUSCLE3;
though this level of detail is not required for general usage of the API.


Glossary
--------

.. glossary::

    Checkpoint
        A checkpoint is a moment during the workflow where the user wants
        to have the state of the whole workflow stored.

    Snapshot
        A snapshot is the stored state of an instance in the workflow.

    Workflow snapshot
        A workflow snapshot is a collection of :term:`snapshots<snapshot>` for
        all instances in the workflow, which can be resumed from. This means
        that the snapshots of every combination of :term:`peer instances` must
        be :ref:`consistent <Snapshot consistency>`.

    Peer instances
        Two instances that are connected by a Conduit.


User tutorial
-------------


Defining checkpoints
````````````````````

The first step for using checkpoints is to define checkpoints in your workflow.
The checkpoint definitions are for your whole workflow, and you can specify them
in yMMSL as in the following example:

.. code-block:: yaml
    :caption: Example checkpoint definition in yMMSL.

    checkpoints:
      at_end: true
      simulation_time:
      - every: 10
        start: 0
        stop: 100
      - every: 20
        start: 100
      wallclock_time:
      - every: 3600
      - at:
        - 300
        - 600
        - 1800

Let's break this down: the first element in this example ``checkpoints``
definition is ``at_end``. When this is set to ``true`` (as in the example), it
means that every instance in the workflow will create a snapshot just before the
workflow finishes. This set of snapshots can be used to resume a simulation near
the end and, for example, let it run for a longer time. Some caveats apply,
though, see :ref:`resuming from *at_end* snapshots` for full details.

The other two items in the ``checkpoints`` definition are the time-based
:ref:`simulation time<Simulation time checkpoints>` and
:ref:`wallclock time<Wallclock time checkpoints>`. You can use two types of
rules to set checkpoint moments for these:

.. _at checkpoint rule:

#. ``at`` rules define specific moments. The example rule above request a
   checkpoint to be taken at 300, 600 and 1800 seconds after the start of the
   simulation. You can define multiple times in one ``at`` rule, but you may
   also add multiple ``at`` rules. The following definitions are all equivalent:

   .. tabs::

        .. tab:: Standard

            .. code-block:: yaml

                checkpoints:
                  wallclock_time:
                  - at:
                    - 300
                    - 600
                    - 1800

        .. tab:: Inline list

            .. code-block:: yaml

                checkpoints:
                  wallclock_time:
                  - at: [300, 600, 1800]

        .. tab:: Multiple ``at`` rules

            .. code-block:: yaml

                checkpoints:
                  wallclock_time:
                  - at: 300
                  - at: 600
                  - at: 1800

.. _every checkpoint rule:

#. ``every`` rules define a recurring set of checkpoints. In the simplest form
   you indicate the interval at which checkpoints should be taken -- every hour
   in the ``wallclock_time`` example above. You may optionally indicate a
   ``start`` or ``stop`` -- as in the ``simulation_time`` example above.

   .. tabs::

        .. tab:: Simple

            .. code-block:: yaml
                :caption: Without ``start`` and ``stop`` indicated, this rule creates a snapshot every hour of elapsed time.

                checkpoints:
                  wallclock_time:
                    every: 3600

        .. tab:: Start and stop

            .. code-block:: yaml
                :caption: This combination of rules define a checkpoint at ``t=0``, ``t=10``, ..., until ``t=100``. Afterwards it continues indefinitely every 20 time units (``t=120``, ``t=140``, ...).

                checkpoints:
                  simulation_time:
                  - every: 10
                    start: 0
                    stop: 100
                  - every: 20
                    start: 100

        .. tab:: Overlapping ranges

            .. code-block:: yaml
                :caption: Overlapping ranges work as well. This combination defines a checkpoint every unit of time (``t=0``, ``t=1``, ...), and additionally at ``t=0.25``, ``t=0.75``, ``t=1.25`` and ``t=1.75``.

                checkpoints:
                  simulation_time:
                  - every: 1
                  - every: 0.25
                    start: 0
                    stop: 2

   .. note::

        When ``stop`` is specified, the stop time is included when ``stop ==
        start + n * every``, with ``n`` a positive whole number. However, this
        might give surprising results due to the inaccuracies of floating point
        computations. Compare for example:

        .. code-block:: yaml
            :caption: This specifies a checkpoint at 0, 1, 2, ..., 6 and 7.

            checkpoints:
              simulation_time:
              - every: 1
                start: 0
                stop: 7

        .. code-block:: yaml
            :caption: However this only checkpoints at 0, 0.1, 0.2, ... 0.5 and 0.6!

            checkpoints:
              simulation_time:
              - every: 0.1
                start: 0
                stop: 0.7

        Why the difference? Well - compare in python:

        .. code-block:: python

            >>> 7 * 1.0
            7.0
            >>> 7 * 0.1
            0.7000000000000001

        Since ``0.7000000000000001`` is larger than ``0.7``, no checkpoint will
        be generated for this time.

.. seealso::

    yMMSL documentation on :external+ymmsl:ref:`Checkpoints`

    yMMSL API reference: :external:py:class:`ymmsl.Checkpoints`,
    :external:py:class:`ymmsl.CheckpointAtRule`,
    :external:py:class:`ymmsl.CheckpointRangeRule`


Simulation time checkpoints
'''''''''''''''''''''''''''

Checkpoints defined in the ``simulation_time`` section are taken based on the
time inside your simulation. It will only work correctly if all components in
the simulation have a shared concept of time, which only increases during the
simulation. This should be no problem for physics-based simulations, though it
does require that the instances make correct use of the :ref:`timestamp in
MUSCLE3 messages <message timestamps>`. When this requirement is fulfilled,
checkpoints based on simulation time are the most reliable way to checkpoint
your workflow.

MUSCLE3 does not interpret or convert the units that you configure in the
checkpoints. The units are the same as the components in the simulation use for
the timestamps in the messages. Typically this will be in SI seconds, but
components may deviate from this standard. MUSCLE3 assumes that all components
in the workflow use the same time units in the interfaces to libmuscle.

.. note::

    MUSCLE3 does not assume anything about the start time of a simulation. Your
    simulation time may start at any value, even negative! Therefore,
    :ref:`checkpoint ranges <every checkpoint rule>` include 0 and negative
    numbers when no ``start`` value is provided.

    Because MUSCLE3 does not know what internal time your simulation starts on,
    an ``every`` rule without a ``start`` value will always trigger a checkpoint
    at the first possible moment in the simulation. You should supply a
    ``start`` value if you do not want this to happen.


Wallclock time checkpoints
''''''''''''''''''''''''''

Checkpoints defined in the ``wallclock_time`` section are taken based on the
elapsed wallclock time of your simulation (also known as *elapsed real time*).
Each component in the simulation will make a snapshot at the earliest possible
moment after a checkpoint is passed.

The checkpoint times in the configuration are interpreted as seconds since the
initialization of ``muscle_manager``.

.. warning::

    Wallclock time checkpoint definitions are (currently) not a reliable way to
    create :term:`workflow snapshots <workflow snapshot>`. While each instance
    in the simulation will create a snapshot when requested, there is no
    guarantee that all snapshots are :ref:`consistent <Snapshot consistency>`.

    When a simulation has relatively simple coupling between components, i.e.
    only one peer instance per :external:py:class:`~ymmsl.Operator`,
    checkpointing based on wallclock time usually works fine.

    However for co-simulation (the *interact* coupling type) and more complex
    coupling, it is likely that not all checkpoints lead to a consistent
    :term:`workflow snapshot`.


Running a simulation with checkpoints
`````````````````````````````````````

Starting a simulation with checkpoints is no different than starting one
without. You need to start the ``muscle_manager`` with the configuration yMMSL
file (or files), as well as the individual components (or let ``muscle_manager``
start them for you with the ``--start-all`` flag). The sole difference is that
the yMMSL configuration must contain a :ref:`checkpoints section <Defining
checkpoints>`.

When ``muscle_manager`` is started with checkpoints configured, a couple of
things change. First, **all** of the component implementations **must** support
checkpointing: the simulation will stop with an error if this is not the case.
The simulation may also stop with an error if there is an issue in the
checkpointing implementation of any of the components.

Second, all components are instructed to make snapshots according to the
configured checkpoints. ``muscle_manager`` keeps track of all created snapshots
during the simulation, looking for :term:`workflow snapshots <workflow
snapshot>`. When a workflow snapshot is detected, ``muscle_manager`` writes a
yMMSL file that can be used to :ref:`resume the simulation <Resuming a
simulation>`.

During the simulation, all of the created snapshots are stored on the file
system. See below table for the directories where MUSCLE3 stores the files.
Note: a run-directory is automatically created when using the ``--start-all``
flag for ``muscle_manager``. You may also specify a custom run directory through
the ``--run-dir DIRECTORY`` option. When you do not provide a run directory, the
last column in below table indicates where snapshots are stored.

.. list-table:: Directories where MUSCLE3 stores snapshot files.
    :header-rows: 1

    * - Snapshot type
      - Run directory provided
      - No run directory provided
    * - Workflow
      - ``run_dir/snapshots/``
      - Working directory of ``muscle_manager``
    * - Instance
      - ``run_dir/instances/<instance>/snapshots/``,

        with ``<instance>`` the name of the instance.
      - Working directory of the instance

.. note::

    When running a :ref:`distributed simulation <distributed execution>` on
    multiple compute nodes, MUSCLE3 assumes that the run directory is accessible
    to all nodes (i.e. on a shared or distributed file system). This is usually
    the case on HPC clusters.


Example: running the reaction-diffusion model with checkpoints
''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

The reaction-diffusion example model from the :ref:`Tutorial with Python` also
has a variant with checkpointing enabled. To run this yourself, navigate in a
command line prompt to the ``docs/source/examples`` folder in the MUSCLE3 git
repository. Then execute the following command:

.. code-block:: bash

    $ mkdir run_rd_example
    $ muscle_manager --start-all --run-dir run_rd_example rd_implementations.ymmsl rd_checkpoints.ymmsl rd_settings.ymmsl

.. note::

    You may get an error ``File 'rd_implementations.ymmsl' does not exist.`` To
    fix this, you need to build the examples in the MUSCLE3 source; in the root
    of the git repository, execute:

    .. code-block::

        $ make test_examples

Above command runs the ``muscle_manager`` and starts all components (the
reaction model and the diffusion model). The ``rd_checkpoints.ymmsl`` file
contains the checkpoint definitions used in this example:

.. literalinclude:: examples/rd_checkpoints.ymmsl
    :caption: ``docs/source/examples/rd_checkpoints.ymmsl, lines 31-33``
    :lines: 31-33
    :language: yaml

MUSCLE3 will create the run directory ``run_rd_example`` for you. In it you'll
find the instance snapshots in ``instances/macro/snapshots`` and
``instances/micro/snapshots``. The workflow snapshots are stored in the
``snapshots`` folder in the run directory.

Resuming a simulation
`````````````````````

You can resume a simulation from a :term:`workflow snapshot` stored in a
previous run of the simulation. This works by appending a workflow snapshot
yMMSL file from a previous run to the regular yMMSL configuration. If you
started your original simulation with::

    $ muscle_manager --run-dir ./run1 configuration.ymmsl

You can resume it from a snapshot of this run like so::

    $ muscle_manager --run-dir ./run2 configuration.ymmsl ./run1/snapshots/snapshot_20221202_112840.ymmsl

Here we choose a different run directory, and resume from the snapshot file
``snapshot_20221202_112840.ymmsl`` that was produced by the first run. This file
contains the information required to resume the workflow:

-   It contains a ``description`` which allows you to inspect metadata of the
    workflow snapshot. It indicates the trigger or triggers leading to this
    snapshot, and some information of the state of each component in the
    workflow. This data is for informational purposes only, and ignored by
    ``muscle_manager``.
-   It also contains the paths to the snapshots that each instance needs to
    resume. Note that these snapshots must still exist on the same location. If
    you move or delete them (or a parent directory), resuming your simulation
    will fail with an error message::

        Unable to load snapshot: <snapshot filename> is not a file. Please ensure this path exists and can be read.


Example: resuming the reaction-diffusion model
''''''''''''''''''''''''''''''''''''''''''''''

To resume the reaction-diffusion model from a snapshot created in the
:ref:`previous section <Example: running the reaction-diffusion model with
checkpoints`, replace ``<date>`` and ``<time>`` in the following command to poin
to the snapshot you want to resume from and execute it.

.. code-block:: bash
    :caption: Resume from an earlier snapshot. Replace ``<date>`` and ``<time>`` to point to an actual snapshot file.

    $ mkdir run_rd_resume
    $ muscle_manager --start-all --run-dir run_rd_resume rd_implementations.ymmsl rd_checkpoints.ymmsl rd_settings.ymmsl run_rd_example/snapshots/snapshot_<date>_<time>.ymmsl

When the command completes you can see the output in the new working directory
``run_rd_resume``.


Making changes to your simulation
'''''''''''''''''''''''''''''''''

MUSCLE3 checkpointing is designed for resuming simulations as if they never
stopped. This means that resuming is only supported for :ref:`consistent
snapshots <Snapshot consistency>` and for simulation configurations that have
not changed.

MUSCLE3 does not support any changes to the model when resuming, such as adding
or removing components, or changing conduits. Attempting this will likely lead
to deadlocks or error messages.

You are allowed to change the settings of your simulation when resuming.
However, it depends on the implementation of your components if and when changed
settings take effect. Please ask the developers of your simulation components
for this information.


Resuming from *at_end* snapshots
''''''''''''''''''''''''''''''''

.. warning::
    Resuming from only ``at_end`` snapshot will immediately complete.
    TODO: Need to think about this still.


Snapshot consistency
````````````````````

MUSCLE3 checkpointing was designed for consistency: no messages between the
components must be lost when restarting. When we fulfill this criterium, a
simulation can resume from a checkpoint as if it was never interrupted.

During a simulation run, each component creates snapshots independent from all
other components. For :ref:`simulation time checkpoints`, the MUSCLE3
checkpointing algorithm is guaranteed to give consistent :term:`workflow
snapshots <workflow snapshot>` when all components adhere to the
:ref:`Multiscale Modeling and Simulation Framework (MMSF) <citation needed>`.

:ref:`Wallclock time checkpoints` in the currrent implementation are less
reliable: components may take snapshots while messages are still in transit.
When that happens, it would lead to an inconsistent state and no workflow
snapshots would be written by ``muscle_manager``.

MUSCLE3 does not support combining inconsistent snapshots, so it is not possible
to freely mix snapshots produced during a simulation. When resuming, MUSCLE3
checks the consistency of all snapshots. The run will end with an error when an
inconsistent state is detected::

    Received message on <port> with unexpected message number <num>. Was
    expecting <num>. Are you resuming from an inconsistent snapshot?

When resuming from a :ref:`snapshot yMMSL <Running a simulation with
checkpoints>` written by ``muscle_manager``, you should not encounter this
error.


Troubleshooting
```````````````

General troubleshooting strategy:

1.  First try to find the root cause of the problem that your simulation ran
    into. You can start by looking in the log file of the ``muscle_manager``,
    located in ``<run directory>/muscle3_manager.log``. This log file may show
    the error message or point you in the right direction.
2.  If the ``muscle_manager`` log did not display an error, it may indicate
    which component failed first. Have a look at the logs of that component to
    figure out what went wrong. The output of an instance is usually found in
    ``<run directory>/instances/<instance name>/``. Open ``stdout.txt`` and
    ``stderr.txt`` to find out what went wrong.
3.  If the ``muscle_manager`` logs did not point to a specific instance, you
    should have a look at the log files of each instance (see point 2 for
    instructions). Note that some instances may log ``Broken Pipe`` errors --
    this usually happens when a peer component has crashed and it is typically
    not the root cause of your simulation crash.

Once you find the root cause of your problem, check below list for common issues
and their resolutions. You may also have found a bug in MUSCLE3: please help us
and your fellow MUSCLE3 users by :ref:`creating an issue <Make an issue>` on
github.

1. The simulation crashes when using checkpoints.
    The first thing you should check is: does the simulation run error-free when
    checkpoints are disabled? You can test this by commenting the checkpointing
    section of your input ymmsl file(s).

    If it runs error-free without checkpoints, have a look at the error message
    in the log file generated by your run. MUSCLE3 attempts to have clear error
    messages to explain what went wrong and give you pointers to a solution.

    When the error message indicates a problem with the implementation of the
    checkpointing API, please check with the developer of the component to fix
    this. If you are the developer of the component, please see the
    :ref:`Developer tutorial` section for additional resources.

2. The simulation crashes when resuming.
    Some common causes for this are:

    -   The snapshot files that the instances are resuming from no longer exist.
        This could for example happen when a previous run directory has been
        moved or deleted. For distributed execution, some compute nodes may not
        be able to access the directories where the instance snapshots are
        stored. See also :ref:`Resuming a simulation`.
    -   Your simulation configuration has incompatible changes compared to the
        original simulation that the snapshots were from. See :ref:`Making
        changes to your simulation`. Luckily, MUSCLE3 stores the previous
        simulation configuration in the run directory. If the snapshot that your
        resume from is stored in ``run1/snapshots/snapshot_xyz.ymmsl``, then you
        can find that configuration in ``run1/configuration.ymmsl``. Try
        resuming with that configuration first to see if this is the real
        problem::
            $ muscle_manager --run-dir run2 run1/configuration.ymmsl run1/snapshots/snapshot_xyz.ymmsl
    -   One of your components has a bug with resuming from a previous snapshot,
        or perhaps your snapshot belonged to a different version of the
        component. Please ask your component developer(s) for help.



Developer tutorial
------------------

TODO


Checkpointing deep-dive
-----------------------

TODO
