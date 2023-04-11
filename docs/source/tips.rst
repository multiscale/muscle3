=============
Tips & tricks
=============

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
