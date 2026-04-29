.. _muscle-tester:

==========================
Testing your MUSCLE3 model
==========================

When developing a MUSCLE3 component, it is useful to be able to test it in
isolation — without having to set up and run the full coupled simulation. The
:class:`~libmuscle.pytest.MuscleTester` class (together with the
``muscle3_tester`` pytest fixture) makes this easy: it starts a real MUSCLE3
manager in the background and connects a *tester component* to all ports of
your implementation, so you can send and receive messages programmatically from
within a pytest test.

.. note::

   The testing infrastructure described here relies on `pytest
   <https://docs.pytest.org>`_, which is **not** installed automatically as
   part of muscle3. If you have not installed it yet, you can do so with:

   .. code-block:: bash

       pip install pytest

   Tests are written as ordinary Python functions whose names start with
   ``test_``, and pytest discovers and runs them automatically.
   
   A *fixture* is a reusable helper that pytest prepares before a test and
   cleans up afterwards. You request a fixture simply by adding a parameter with
   the same name to your test function. 

Quick start
===========

Step 1: Provide the yMMSL file for testing your implementation
---------------------------------------------------

Your implementation needs a yMMSL file that declares its ports. We recommend
placing this file in a ``tests/`` folder at the root of your project, next to
your test files:

.. code-block:: text

    my_project/
    ├── micro.py
    └── tests/
        ├── micro.ymmsl
        └── test_micro.py

For example, for a simple micro model that receives a value on ``init`` and
sends a result on ``final``:

.. code-block:: yaml
    :caption: tests/micro.ymmsl

    ymmsl_version: v0.2

    programs:
      micro:
        ports:
          f_init: init
          o_f: final
        executable: python3
        args: micro.py

    resources:
      micro:
        threads: 1

.. note::

    The path passed to
    :meth:`~libmuscle.pytest.MuscleTester.start_implementation` is resolved
    relative to the directory from which you run ``pytest`` — typically the
    project root. The executable in the yMMSL file is also launched from that
    directory, so make sure your implementation is importable from there.

Step 2: Use the ``muscle3_tester`` fixture in your test
-------------------------------------------------------

.. code-block:: python
    :caption: tests/test_micro.py

    from libmuscle import Message
    from libmuscle.pytest import MuscleTester


    def test_micro_model(muscle3_tester: MuscleTester) -> None:
        """Test the micro model by acting as the macro."""
        tester = muscle3_tester.start_implementation("tests/micro.ymmsl", "micro")

        # Send a message to the micro model's 'init' port
        tester.send("init", Message(0.0, 10.0, 42))

        # Receive the result from the micro model's 'final' port
        reply = tester.receive("final")

        assert reply.data == 42


Step 3: Run your tests
----------------------

Run ``pytest`` from the project root so that all paths resolve correctly:

.. code-block:: bash

    cd my_project
    pytest


Timeouts and error handling
============================

By default, :meth:`~libmuscle.pytest.MuscleTester.start_implementation`
uses a 60-second timeout for all receive operations. If the implementation
does not send a message within that time, a :class:`RuntimeError` is raised
and the test fails.

You may want to **increase** the timeout when your implementation performs
expensive work between messages, for example, a micro-model that runs a
numerical solver for several minutes per time step. In those cases the default
60 seconds may expire before the component has had a chance to reply, causing a
spurious test failure.

Conversely, you may want to **decrease** the timeout in fast unit tests so
that a missing ``send`` call is detected quickly rather than making the test
suite hang for a full minute.

You can adjust this timeout:

.. code-block:: python

    tester = muscle3_tester.start_implementation(
        "tests/micro.ymmsl", "micro", default_timeout=5.0
    )

You can also override the timeout for individual receive calls:

.. code-block:: python

    reply = tester.receive("final", timeout=2.0)


API reference
=============

The full API for :class:`libmuscle.pytest.MuscleTester` and
:class:`libmuscle.pytest.implementation_tester.ImplementationTester` is
documented in the :doc:`python_api`.
