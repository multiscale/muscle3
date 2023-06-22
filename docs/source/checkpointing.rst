Simulation checkpoints
======================

When you execute a long-running simulation, it can be very helpful to store the
state of a simulation at certain intervals. For example, your simulation running
on a HPC cluster may crash due to insufficient
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

.. contents:: Contents
    :local:
    :depth: 1


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

This user tutorial explains all you need to know about checkpointing for running
and resuming simulations. Some details are deliberately left out, though you
can read all about those in the :ref:`developer tutorial` or :ref:`checkpointing
deep-dive`.

.. contents:: User tutorial contents
    :local:


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

#. ``at`` rules select specific moments. The example rule above request a
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
    :external:py:class:`ymmsl.CheckpointRangeRule`.


Simulation time checkpoints
'''''''''''''''''''''''''''

Checkpoints defined in the ``simulation_time`` section are taken based on the
time inside your simulation. This will only work correctly if all components in
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

    When a simulation has relatively simple coupling between components,
    checkpointing based on wallclock time usually works fine.

    However for co-simulation (the *interact* coupling type) and more complex
    coupling, it is likely that not all checkpoints lead to a consistent
    :term:`workflow snapshot`.

    If you intend to use wallclock time checkpoints and find that you often
    don't get a consistent workflow snapshot, you may try the following
    workaround: instead of requesting a wallclock time checkpoint at (for
    example) 600 seconds, you can specify checkpoints at 600, 601, 602, 603, 604
    and 605 seconds. The "right" interval to use will depend on the typical
    compute times of your components and coupling in the simulation.


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
system. See the table below for the directories where MUSCLE3 stores the files.
Note: a run-directory is automatically created when using the ``--start-all``
flag for ``muscle_manager``. You may also specify a custom run directory through
the ``--run-dir DIRECTORY`` option. When you do not provide a run directory, the
last column in the table below indicates where snapshots are stored.

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
    $ muscle_manager --start-all --run-dir run_rd_example rd_implementations.ymmsl rd_checkpoints_python.ymmsl rd_settings.ymmsl

.. note::

    You may get an error ``File 'rd_implementations.ymmsl' does not exist.`` To
    fix this, you need to build the examples in the MUSCLE3 source; in the root
    of the git repository, execute:

    .. code-block::

        $ make test_examples

The above command runs the ``muscle_manager`` and starts all components (the
reaction model and the diffusion model). The ``rd_checkpoints_python.ymmsl`` file
contains the checkpoint definitions used in this example:

.. literalinclude:: examples/rd_checkpoints_python.ymmsl
    :caption: ``docs/source/examples/rd_checkpoints_python.ymmsl, lines 31-33``
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
checkpoints>`, replace ``<date>`` and ``<time>`` in the following command to
point to the snapshot you want to resume from.

.. code-block:: bash
    :caption: Resume from an earlier snapshot. Replace ``<date>`` and ``<time>`` to point to an actual snapshot file.

    $ mkdir run_rd_resume
    $ muscle_manager --start-all --run-dir run_rd_resume rd_implementations.ymmsl rd_checkpoints_python.ymmsl rd_settings.ymmsl run_rd_example/snapshots/snapshot_<date>_<time>.ymmsl

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
    Resuming from an ``at_end`` snapshot only will immediately complete.


Snapshot consistency
````````````````````

MUSCLE3 checkpointing was designed for consistency: no messages between the
components must be lost when restarting. When we fulfill this criterium, a
simulation can resume from a checkpoint as if it was never interrupted.

During a simulation run, each component creates snapshots independently from
all other components. For :ref:`simulation time checkpoints`, the MUSCLE3
checkpointing algorithm is guaranteed to give consistent :term:`workflow
snapshots <workflow snapshot>` when all components adhere to the
:ref:`Multiscale Modeling and Simulation Framework (MMSF) <citation needed>`.

:ref:`Wallclock time checkpoints` in the currrent implementation are less
reliable: components may take snapshots while messages are still in transit.
When that happens an inconsistent state is produced and no workflow snapshots
are written by ``muscle_manager``.

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

Once you find the root cause of your problem, check the list below for common
issues and their resolutions. You may also have found a bug in MUSCLE3: please
help us and your fellow MUSCLE3 users by :ref:`creating an issue <Make an
issue>` on GitHub.

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

    -   One of your components has a bug that is triggered when resuming from a
        previous snapshot, or perhaps your snapshot belonged to a different
        version of the component. Please ask your component developer(s) for
        help.



Developer tutorial
------------------

This developer tutorial explains all you need to know about implementing
checkpointing in your MUSCLE3 simulation component. If you're not a developer
and want to learn how to define checkpoints and resume simulations, please have
a look at the :ref:`user tutorial`.

Some details are deliberately left out in this developer tutorial, though you
can read all about those in the :ref:`checkpointing deep-dive`.

.. contents:: Developer totorial contents
    :local:


Start situation: components without checkpointing
`````````````````````````````````````````````````

In this tutorial we will add checkpointing to the reaction and diffusion
components from the :ref:`Python <Tutorial with Python>`, :ref:`C++ <MUSCLE and C++>`
and :ref:`Fortran <MUSCLE and Fortran>` tutorials.

Additionally, we will do the same for a generic MUSCLE3 component template.
These templates illustrate the structure of a MUSCLE3 component, but they are
not complete and cannot be executed.

.. tabs::

    .. group-tab:: Reaction model

        .. tabs::

            .. group-tab:: Python

                .. literalinclude:: examples/python/reaction.py
                    :caption: ``docs/source/examples/python/reaction.py``
                    :language: python

            .. group-tab:: C++

                .. literalinclude:: examples/cpp/reaction.cpp
                    :caption: ``docs/source/examples/cpp/reaction.cpp``
                    :language: c++

            .. group-tab:: Fortran

                .. literalinclude:: examples/fortran/reaction.f90
                    :caption: ``docs/source/examples/fortran/reaction.f90``
                    :language: fortran

    .. group-tab:: Diffusion model

        .. tabs::

            .. group-tab:: Python

                .. literalinclude:: examples/python/diffusion.py
                    :caption: ``docs/source/examples/python/diffusion.py``
                    :language: python

            .. group-tab:: C++

                .. literalinclude:: examples/cpp/diffusion.cpp
                    :caption: ``docs/source/examples/cpp/diffusion.cpp``
                    :language: c++

            .. group-tab:: Fortran

                .. literalinclude:: examples/fortran/diffusion.f90
                    :caption: ``docs/source/examples/fortran/diffusion.f90``
                    :language: fortran

    .. group-tab:: Generic template

        .. tabs::

            .. group-tab:: Python

                .. literalinclude:: templates/instance.py
                    :caption: ``docs/source/templates/instance.py``
                    :language: python

            .. group-tab:: C++

                .. literalinclude:: templates/instance.cpp
                    :caption: ``docs/source/templates/instance.cpp``
                    :language: c++

            .. group-tab:: Fortran

                .. literalinclude:: templates/instance.f90
                    :caption: ``docs/source/templates/instance.f90``
                    :language: fortran


Step 1: Set ``USES_CHECKPOINT_API`` on instance creation
````````````````````````````````````````````````````````

As first step, you need to indicate that you intend to use the checkpoint API.
You do this through the :py:attr:`~InstanceFlags.USES_CHECKPOINT_API` flag when
creating the instance:

.. tabs::

    .. group-tab:: Python

        .. code-block:: Python

            from libmuscle import Instance, USES_CHECKPOINT_API

            ...

            ports = ...
            instance = Instance(ports, USES_CHECKPOINT_API)

        .. seealso::

            API documentation for
            :py:attr:`~libmuscle.InstanceFlags.USES_CHECKPOINT_API`.

    ..  group-tab:: C++

        .. code-block:: C++

            #include <libmuscle/libmuscle.hpp>
            #include <ymmsl/ymmsl.hpp>

            using libmuscle::PortsDescription;
            using libmuscle::Instance;
            using libmuscle::InstanceFlags;

            ...

            int main(int argc, char * argv[]) {
                PortsDescription ports = ...;
                Instance instance(argc, argv, ports, InstanceFlags::USES_CHECKPOINT_API);

                ...
            }

        .. seealso::

            API documentation for
            :cpp:enumerator:`~libmuscle::impl::InstanceFlags::USES_CHECKPOINT_API`.

    .. group-tab:: Fortran

        .. code-block:: Fortran

            use ymmsl
            use libmuscle

            type(LIBMUSCLE_PortsDescription) :: ports
            type(LIBMUSCLE_Instance) :: instance

            ports = ...
            instance = LIBMUSCLE_Instance_create( &
                ports, LIBMUSCLE_InstanceFlags(USES_CHECKPOINT_API=.true.))

        .. seealso::

            API documentation for :f:func:`LIBMUSCLE_InstanceFlags`.


If you do not set this flag, you'll get a runtime error when trying to use any
of the checkpointing API calls on the Instance object.


Step 2: Implement checkpoint hooks
``````````````````````````````````

The first step in implementing the checkpointing API is implementing the
checkpoint hooks. These are the points where your component can make
checkpoints:

1.  :ref:`Intermediate snapshots`

    Intermediate snapshots are taken inside the reuse-loop, **immediately
    after** the ``S`` Operator of your component.

2.  :ref:`Final snapshots`

    Final snapshots are taken at the **end of the reuse-loop**, after the
    ``O_F`` Operator of your component.


Intermediate snapshots
''''''''''''''''''''''

Intermediate snapshots are taken inside the reuse-loop, **immediately after**
the ``S`` Operator of your component.

Taking intermediate snapshots is optional. However, we recommend implementing
intermediate snapshots when any of the following points holds for your
component:

1.  Your component has a loop containing ``O_I`` and ``S``, and you communicate
    during Operator ``O_I`` or Operator ``S``.

    Implementing intermediate checkpointing allows submodels connected to your
    component to also create checkpoints.

    .. warning::

        If you do not implement intermediate checkpoints in this case, then it
        is likely that a large amount of user-provided checkpoints will not lead
        to consistent :term:`workflow snapshots <workflow snapshot>`. Please
        implement intermediate snapshots to give the users of your component a
        good checkpointing experience.

2.  There is no communication during ``O_I`` and ``S``, but the state update
    ``S`` is executed in a (time-integration) loop which takes a relatively long
    time.

    In this case, intermediate checkpointing allows users to create checkpoints
    of your component during long-running computations.

In all other cases, there usually is little or no added value in implementing
intermediate snapshots in addition to :ref:`Final snapshots`.

You implement taking intermediate snapshots as follows:

1.  Find out where in your code to implement the checkpointing calls. Typically
    there is a state update loop (e.g. a ``while`` or ``for`` loop) in a
    component. You should implement the checkpointing calls **at the end** of
    this state update loop. In this way, your code can resume immediately at the
    begin of that loop. This allows for consistent restarts with the least
    amount of code.
2.  Ask libmuscle if you need to store your state and create an intermediate
    snapshot with the API call ``should_save_snapshot(t)``. You must provide the
    current time ``t`` in your simulation, such that MUSCLE3 can determine if
    :ref:`Simulation time checkpoints` are triggered.
3.  Collect the state that you need to store.
4.  Create a ``libmuscle.Message`` object to put your state in.
5.  Store the snapshot Message with the API call ``save_snapshot(message)``.

See :ref:`Example: implemented checkpoint hooks` for example implementations in
the reaction-diffusion models and the component template.

.. seealso::

    - Python API documentation:
      :py:meth:`~libmuscle.Instance.should_save_snapshot`,
      :py:meth:`~libmuscle.Instance.save_snapshot`.
    - C++ API documentation:
      :cpp:func:`~libmuscle::impl::Instance::should_save_snapshot`,
      :cpp:func:`~libmuscle::impl::Instance::save_snapshot`.
    - Fortran API documentation:
      :f:func:`LIBMUSCLE_Instance_should_save_snapshot`,
      :f:func:`LIBMUSCLE_Instance_save_snapshot`.


Final snapshots
'''''''''''''''

Final snapshots **must** be implemented by all components supporting
checkpointing. You implement taking a final snapshot as follows:

1.  You must implement the checkpoint calls at the end of the :ref:`reuse loop
    <The reuse loop>`.
2.  Ask libmuscle if you need to store your state and create a final snapshot
    with the API call ``should_save_final_checkpoint()``. Contrary to the
    intermediate checkpoints, this call may block to determine if a checkpoint
    is needed (this is also the reason it must happen at the end of the reuse
    loop).
3.  Collect the state that you need to store.
4.  Create a ``libmuscle.Message`` object to put your state in.
5.  Store the snapshot Message with the API call
    ``save_final_snapshot(message)``.

See :ref:`Example: implemented checkpoint hooks` for example implementations in
the reaction-diffusion models and the component template.

.. seealso::

    - Python API documentation:
      :py:meth:`~libmuscle.Instance.should_save_final_snapshot`,
      :py:meth:`~libmuscle.Instance.save_final_snapshot`.
    - C++ API documentation:
      :cpp:func:`~libmuscle::impl::Instance::should_save_final_snapshot`,
      :cpp:func:`~libmuscle::impl::Instance::save_final_snapshot`.
    - Fortran API documentation:
      :f:func:`LIBMUSCLE_Instance_should_save_final_snapshot`,
      :f:func:`LIBMUSCLE_Instance_save_final_snapshot`.


Example: implemented checkpoint hooks
'''''''''''''''''''''''''''''''''''''

Note that below examples only shows the changes compared to the :ref:`start
situation <Start situation: components without checkpointing>`. You can view the
full contents of the files in the git repository.

.. tabs::

    .. group-tab:: Reaction model

        .. rubric:: Intermediate snapshots

        The state we need to store consists of three parts: the current ``U``,
        the current time ``t_cur`` and the end-time for the time integration
        ``t_stop``. The current time is stored as the ``timestamp`` attribute of
        the ``Message`` object. The rest is stored in ``Message.data``.

        .. rubric:: Final snapshots

        For the final snapshot there is no state that is required for resuming.
        The complete state will be received with the next message on the
        ``initial_state`` port.

        .. tabs::

            .. group-tab:: Python

                .. literalinclude:: tutorial_code/checkpointing_reaction_partial.py
                    :caption: ``docs/source/tutorial_code/checkpointing_reaction_partial.py``
                    :language: python
                    :diff: examples/python/reaction.py

            .. group-tab:: C++

                .. literalinclude:: tutorial_code/checkpointing_reaction_partial.cpp
                    :caption: ``docs/source/tutorial_code/checkpointing_reaction_partial.cpp``
                    :language: c++
                    :diff: examples/cpp/reaction.cpp

            .. group-tab:: Fortran

                .. literalinclude:: tutorial_code/checkpointing_reaction_partial.f90
                    :caption: ``docs/source/tutorial_code/checkpointing_reaction_partial.f90``
                    :language: fortran
                    :diff: examples/fortran/reaction.f90

    .. group-tab:: Diffusion model

        .. rubric:: Intermediate snapshots

        The state we need to store consists of two parts: the current time
        ``t_cur`` and the history of ``U``: ``Us``. Note that the last value of
        ``U`` is contained in ``Us``, so we do not need to save ``U``
        explicitly. The current time is stored as the ``timestamp`` attribute of
        the ``Message`` object. ``Us`` is stored in ``Message.data``.

        .. rubric:: Final snapshots

        The same state is stored as for intermediate snapshots.

        .. tabs::

            .. group-tab:: Python

                .. literalinclude:: tutorial_code/checkpointing_diffusion_partial.py
                    :caption: ``docs/source/tutorial_code/checkpointing_diffusion_partial.py``
                    :language: python
                    :diff: examples/python/diffusion.py

            .. group-tab:: C++

                .. literalinclude:: tutorial_code/checkpointing_diffusion_partial.cpp
                    :caption: ``docs/source/tutorial_code/checkpointing_diffusion_partial.cpp``
                    :language: c++
                    :diff: examples/cpp/diffusion.cpp

            .. group-tab:: Fortran

                .. literalinclude:: tutorial_code/checkpointing_diffusion_partial.f90
                    :caption: ``docs/source/tutorial_code/checkpointing_diffusion_partial.f90``
                    :language: fortran
                    :diff: examples/fortran/diffusion.f90

    .. group-tab:: Generic template

        .. tabs::

            .. group-tab:: Python

                .. literalinclude:: tutorial_code/checkpointing_instance_partial.py
                    :caption: ``docs/source/tutorial_code/checkpointing_instance_partial.py``
                    :language: python
                    :diff: templates/instance.py

            .. group-tab:: C++

                .. literalinclude:: tutorial_code/checkpointing_instance_partial.cpp
                    :caption: ``docs/source/tutorial_code/checkpointing_instance_partial.cpp``
                    :language: c++
                    :diff: templates/instance.cpp

            .. group-tab:: Fortran

                .. literalinclude:: tutorial_code/checkpointing_instance_partial.f90
                    :caption: ``docs/source/tutorial_code/checkpointing_instance_partial.f90``
                    :language: fortran
                    :diff: templates/instance.f90


Step 3: Implement resume
````````````````````````

Now that the checkpoint hooks are implemented, we can add support for resuming
from a previously created checkpoint. When resuming, there are two options:
resuming from an intermediate checkpoint and resuming from a final checkpoint.

When resuming from an intermediate checkpoint, your component first loads its
state from the checkpoint. Then it should continue where it left off, which is
at the beginning of ``O_I``. This means that it has to skip ``F_INIT`` in
order to run as if it had never stopped.

When resuming from a final checkpoint, your component first loads its state from
the checkpoint. Next, your component executes the ``F_INIT`` operator as usual,
as it would have had it continued after writing the snapshot.

Steps to implement the resumption logic:

1.  At the start of -- but inside -- the reuse loop you check if you need to
    resume from a previous snapshot with the API call ``resuming()``.

    .. note::

        This takes place inside the reuse loop. Currently resuming can only
        happen during the first iteration of the reuse loop. However, additional
        checkpointing features are planned that would allow a model to resume
        multiple times inside one run. By implementing the resume logic inside
        the reuse loop, your component will be forwards-compatible with this.

2.  When resuming, you load the previously stored snapshot with
    ``load_snapshot()`` and restore the state of your component.
3.  Afterwards check if initialization is required with ``should_init()`` and
    run the regular initialization logic.
4.  Continue with the time-integration loop.

See :ref:`Example: implemented checkpoint hooks and resume` for example
implementations in the reaction-diffusion models and the component template.

.. seealso::

    - Python API documentation:
      :py:meth:`~libmuscle.Instance.resuming`,
      :py:meth:`~libmuscle.Instance.load_snapshot`,
      :py:meth:`~libmuscle.Instance.should_init`.
    - C++ API documentation:
      :cpp:func:`~libmuscle::impl::Instance::resuming`,
      :cpp:func:`~libmuscle::impl::Instance::load_snapshot`,
      :cpp:func:`~libmuscle::impl::Instance::should_init`.
    - Fortran API documentation:
      :f:func:`LIBMUSCLE_Instance_resuming`,
      :f:func:`LIBMUSCLE_Instance_load_snapshot`,
      :f:func:`LIBMUSCLE_Instance_should_init`.

Reload settings when resuming
'''''''''''''''''''''''''''''

You will notice in the :ref:`examples <Example: implemented checkpoint hooks and
resume>` that the resume logic is not executed first in the reuse-loop.
Instead, the components all retrieve settings. The reason behind this is that it
allows the user to resume a simulation with slightly different settings and have
those settings take effect immediately after resuming.

It is not required to do this, so you get to decide if (and when) you reload
settings after resuming. Be sure to include the behaviour of your component in
the documentation, such that users of your component know what they can expect.


Example: implemented checkpoint hooks and resume
````````````````````````````````````````````````

Note that below examples only shows the changes compared to the :ref:`start
situation <Start situation: components without checkpointing>`. You can view the
full contents of the files in the git repository.


.. tabs::

    .. group-tab:: Reaction model

        .. rubric:: Resume logic

        In :ref:`Example: implemented checkpoint hooks` we made the choice to
        store different data in the message for intermediate and final
        snapshots. When resuming we therefore need to handle these two cases.

        .. tabs::

            .. group-tab:: Python

                .. literalinclude:: examples/python/checkpointing_reaction.py
                    :caption: ``docs/source/examples/python/checkpointing_reaction.py``
                    :language: python
                    :diff: examples/python/reaction.py

            .. group-tab:: C++

                .. literalinclude:: examples/cpp/checkpointing_reaction.cpp
                    :caption: ``docs/source/examples/cpp/checkpointing_reaction.cpp``
                    :language: c++
                    :diff: examples/cpp/reaction.cpp

            .. group-tab:: Fortran

                .. literalinclude:: examples/fortran/checkpointing_reaction.f90
                    :caption: ``docs/source/examples/fortran/checkpointing_reaction.f90``
                    :language: fortran
                    :diff: examples/fortran/reaction.f90

    .. group-tab:: Diffusion model

        .. rubric:: Resume logic

        For the diffusion model we stored the same state for intermediate and
        final snapshots. This makes resuming easier because we do not have to
        distinguish between the data stored in the loaded ``Message`` object.

        .. tabs::

            .. group-tab:: Python

                .. literalinclude:: examples/python/checkpointing_diffusion.py
                    :caption: ``docs/source/examples/python/checkpointing_diffusion.py``
                    :language: python
                    :diff: examples/python/diffusion.py

            .. group-tab:: C++

                .. literalinclude:: examples/cpp/checkpointing_diffusion.cpp
                    :caption: ``docs/source/examples/cpp/checkpointing_diffusion.cpp``
                    :language: c++
                    :diff: examples/cpp/diffusion.cpp

            .. group-tab:: Fortran

                .. literalinclude:: examples/fortran/checkpointing_diffusion.f90
                    :caption: ``docs/source/examples/fortran/checkpointing_diffusion.f90``
                    :language: fortran
                    :diff: examples/fortran/diffusion.f90

    .. group-tab:: Generic template

        .. tabs::

            .. group-tab:: Python

                .. literalinclude:: templates/checkpointing_instance.py
                    :caption: ``docs/source/templates/checkpointing_instance.py``
                    :language: python
                    :diff: templates/instance.py

            .. group-tab:: C++

                .. literalinclude:: templates/checkpointing_instance.cpp
                    :caption: ``docs/source/templates/checkpointing_instance.cpp``
                    :language: c++
                    :diff: templates/instance.cpp

            .. group-tab:: Fortran

                .. literalinclude:: templates/checkpointing_instance.f90
                    :caption: ``docs/source/templates/checkpointing_instance.f90``
                    :language: fortran
                    :diff: templates/instance.f90


Components that do not keep state between reuse
```````````````````````````````````````````````

Some components do not need to keep state between reuses. An example of that is
the reaction model from the above examples. In the final snapshot, no state
needs to be stored to allow properly resuming this component, see
:ref:`Example: implemented checkpoint hooks`.

Other examples of such components may be data transformers, receiving data
on an ``F_INIT`` port and sending the converted data on an ``O_F`` port.

If you indicate to libmuscle that your component does not keep state between
reuse, libmuscle automatically provides checkpointing for your component. You do
this by providing the ``~InstanceFlags.KEEPS_NO_STATE_FOR_NEXT_USE`` flag
when creating the instance. See the below example for a variant of the example
reaction model.

.. tabs::

    .. group-tab:: Python

        .. literalinclude:: examples/python/reaction_no_state_for_next_use.py
            :caption: ``docs/source/examples/python/reaction_no_state_for_next_use.py``
            :language: python
            :diff: examples/python/reaction.py

    .. group-tab:: C++

        .. literalinclude:: examples/cpp/reaction_no_state_for_next_use.cpp
            :caption: ``docs/source/examples/cpp/reaction_no_state_for_next_use.cpp``
            :language: c++
            :diff: examples/cpp/reaction.cpp

    .. group-tab:: Fortran

        .. literalinclude:: examples/fortran/reaction_no_state_for_next_use.f90
            :caption: ``docs/source/examples/fortran/reaction_no_state_for_next_use.f90``
            :language: fortran
            :diff: examples/fortran/reaction.f90

.. seealso::

    - Python API documentation: :py:class:`~libmuscle.InstanceFlags`.
    - C++ API documentation :cpp:enum:`~libmuscle::impl::InstanceFlags`.
    - Fortran API documentation :f:type:`LIBMUSCLE_InstanceFlags`.


Builtin validation
``````````````````

MUSCLE3's checkpointing API was carefully designed to allow consistenly resuming
a simulation. This is only possible when components carefully implement the
checkpointing API. To support you in this task, MUSCLE3 tries to detect any
issues with the checkpointing implementation. When MUSCLE3 detects a problem, an
error is raised to indicate what went wrong and point you in the right direction
for fixing the problem.


Checkpointing in MPI-enabled components
```````````````````````````````````````

Checkpionting in MPI-enabled components works in the same way as for non-MPI components.
The main difference is that some API methods must be called by all processes, while
others can only be called from the root process.

- ``resuming()`` must be called simultaneously in all processes.
- ``load_snapshot()`` may only be called on the root process. It is up to the model code
  to scatter or broadcast the snapshot state to the non-root processes, if necessary.
- ``should_init()`` must be called simultaneously in all processes.
- ``should_save_snapshot()`` and ``should_save_final_snapshot()`` must be called
  simultaneously in all processes.
- ``save_snapshot()`` and ``save_final_snapshot()`` may only be called on the root
  process. It is therefore up to the model code to gather the necessary state from the
  non-root processes before saving the snapshot.

.. seealso::

    - C++ API documentation:

      - :cpp:func:`~libmuscle::impl::Instance::resuming`
      - :cpp:func:`~libmuscle::impl::Instance::load_snapshot`
      - :cpp:func:`~libmuscle::impl::Instance::should_init`
      - :cpp:func:`~libmuscle::impl::Instance::should_save_final_snapshot`
      - :cpp:func:`~libmuscle::impl::Instance::save_final_snapshot`
      - :cpp:func:`~libmuscle::impl::Instance::should_save_snapshot`
      - :cpp:func:`~libmuscle::impl::Instance::save_snapshot`

    - Fortran API documentation:

      - :f:func:`LIBMUSCLE_Instance_resuming`
      - :f:func:`LIBMUSCLE_Instance_load_snapshot`
      - :f:func:`LIBMUSCLE_Instance_should_init`
      - :f:func:`LIBMUSCLE_Instance_should_save_final_snapshot`
      - :f:func:`LIBMUSCLE_Instance_save_final_snapshot`
      - :f:func:`LIBMUSCLE_Instance_should_save_snapshot`
      - :f:func:`LIBMUSCLE_Instance_save_snapshot`
