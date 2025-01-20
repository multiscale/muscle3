=============
Tips & tricks
=============

Deadlock detection
==================

.. versionadded:: 0.8

MUSCLE3 has a deadlock detection mechanism, which can detect when the simulation
is deadlocked because (part of) the components of the simulation are all waiting
for a message from each other. This could happen, for example, due to a bug in
one of the components, or because the components are not correctly wired
together.

The simplest deadlock consists of two components, where the first component is
waiting to receive a message from the second component and vice versa. Because
both components are waiting for eachother, the simulation is stuck and will no
longer progress. MUSCLE3 will abort the simulation run and provide an error
message that indicates that the simulation was deadlocked:

.. code-block:: output
    :caption: Example output of a deadlocked simulation

    muscle_manager 2024-08-20 13:57:58,544 CRITICAL libmuscle.manager.deadlock_detector: Potential deadlock detected:
    The following 2 instances are deadlocked:
    1. Instance 'micro' is waiting for instance 'macro' in a receive on port 'initial_state'.
    2. Instance 'macro' is waiting for instance 'micro' in a receive on port 'state_in'.


.. note::
    MUSCLE3 can only detect deadlocks that are the result of components waiting
    for messages to receive. "Internal" deadlocks in simulation components (for
    example due to bugs in MPI logic) cannot be detected by MUSCLE3.


Configuring the deadlock detection
----------------------------------

With the default settings, MUSCLE3 will detect a deadlock 10 seconds after it
occurs. The simulation is halted after another 15 seconds have passed.
These default settings are chosen to limit the runtime impact of the deadlock
detection. It may be useful to detect deadlocks faster during development of the
simulation. This can be achieved with the special setting
``muscle_deadlock_receive_timeout``:

.. code-block:: yaml
    :caption: Example configuration setting ``muscle_deadlock_receive_timeout``

    ymmsl_version: v0.1
    settings:
      muscle_deadlock_receive_timeout: 1.0

The value provided to this setting is the initial timeout (in seconds) before
MUSCLE3 detects a deadlock. The simulation is halted after 1.5 times that
duration. Deadlock detection is disabled when a negative value is used.


Running simulation components interactively
===========================================

Sometimes you want to run a component interactively, for example when using
:ref:`debuggers <Debugging simulation components>`. This also allows you to inspect the
output of a component in real time.

If you run your simulation in an environment with a graphical interface, you can use the
following trick: run a component inside a new terminal window. Adjust the
implementations section of your configuration as illustrated in below code sample.

.. tabs::

    .. tab:: Original implementations section

        .. code-block:: yaml

            implementations:
                my_component:
                    executable: my_program
                    args:
                    - arg1
                    - arg2

    .. tab:: Use xterm

        .. code-block:: yaml

            implementations:
                my_component:
                    executable: xterm
                    args:
                    - -e
                    - my_program
                    - arg1
                    - arg2

    .. tab:: Use gnome-terminal

        .. code-block:: yaml

            implementations:
                my_component:
                    executable: gnome-terminal
                    args:
                    - --
                    - my_program
                    - arg1
                    - arg2

.. note::

    Other terminal applications should work as well. Please consult the documentation of
    the terminal application you wish to use how to run a command inside the terminal.

If you don't have a graphical interface available, you could use a screen manager like
`GNU screen <https://www.gnu.org/software/screen/>`_.

.. tabs::

    .. tab:: Original implementations section

        .. code-block:: yaml

            implementations:
                my_component:
                    executable: my_program
                    args:
                    - arg1
                    - arg2

    .. tab:: Use GNU screen

        .. code-block:: yaml

            implementations:
                my_component:
                    executable: screen
                    args:
                    - -dmS
                    - my_component_screen_session
                    - my_program
                    - arg1
                    - arg2

Once the component is started, you can connect to the ``screen`` session by
opening a terminal on the machine where the component is running (for example
through SSH) and run the command:

.. code-block:: bash

    $ screen -r my_component_screen_session

Note: ``screen`` can be a daunting application to work with. For more details,
please check the `GNU screen` documentation or other internet sites explaining
``screen`` way better than we ever could.


Debugging simulation components
===============================

You can combine the method described in :ref:`Running simulation components
interactively` with starting a debugger for your program. This allows you to
interactively debug a component.

Below you can see how to start a component inside the `GNU debugger
<https://www.sourceware.org/gdb/>`_ ``gdb`` and how to run a python component with the
`Python Debugger <https://docs.python.org/3/library/pdb.html>`_ ``pdb`` debugger. Please
check their documentation (and/or the general internet) for more details on how to use
these debuggers.

.. tabs::

    .. tab:: Original implementations section

        .. code-block:: yaml

            implementations:
                my_component:
                    executable: my_program
                    args:
                    - arg1
                    - arg2
                my_python_component:
                    executable: python
                    args: my_python_program.py

    .. tab:: With debuggers

        .. code-block:: yaml

            implementations:
                my_component:
                    executable: xterm
                    args:
                    - -e
                    - gdb
                    - --args
                    - my_program
                    - arg1
                    - arg2
                my_python_component:
                    executable: xterm
                    args:
                    - -e
                    - python
                    - -m
                    - pdb
                    - my_python_program.py

        .. note::

            See :ref:`Running simulation components interactively` for alternatives to
            ``xterm``.
