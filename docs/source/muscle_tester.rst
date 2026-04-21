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


How it works
============

Given a yMMSL file that describes your implementation (its ports, executable,
etc.), :class:`~libmuscle.pytest.MuscleTester`:

1. Reads the yMMSL configuration and automatically adds a *tester component*
   that is wired to every port of the implementation under test.
2. Starts a real MUSCLE3 manager in a background process.
3. Returns an :class:`~libmuscle.pytest.implementation_tester.ImplementationTester`
   object that you can use to :meth:`~libmuscle.pytest.implementation_tester.ImplementationTester.send`
   and :meth:`~libmuscle.pytest.implementation_tester.ImplementationTester.receive`
   messages on those ports, just as the real coupled component would.


Quick start
===========

Step 1: Provide the yMMSL file for testing your implementation
---------------------------------------------------

Your implementation needs a yMMSL file that declares its ports. For example,
for a simple micro model that receives a value on ``init`` and sends a result
on ``final``:

.. code-block:: yaml
    :caption: micro.ymmsl

    ymmsl_version: v0.2

    programs:
      micro:
        ports:
          f_init: init
          o_f: final
        executable: python3
        args: "-m micro"

    resources:
      micro:
        threads: 1

Step 2: Use the ``muscle3_tester`` fixture in your test
-------------------------------------------------------

.. code-block:: python
    :caption: test_micro.py

    from libmuscle import Message
    from libmuscle.pytest import MuscleTester


    def test_micro_model(muscle3_tester: MuscleTester) -> None:
        """Test the micro model by acting as the macro."""
        tester = muscle3_tester.start_implementation("micro.ymmsl", "micro")

        # Send a message to the micro model's 'init' port
        tester.send("init", Message(0.0, 10.0, 42))

        # Receive the result from the micro model's 'final' port
        reply = tester.receive("final")

        assert reply.data == 42


Step 3: Run your tests
----------------------

.. code-block:: bash

    pytest test_micro.py


Timeouts and error handling
============================

By default, :meth:`~libmuscle.pytest.MuscleTester.start_implementation`
uses a 60-second timeout for all receive operations. If the implementation
does not send a message within that time, a :class:`RuntimeError` is raised
and the test fails. You can adjust this timeout:

.. code-block:: python

    tester = muscle3_tester.start_implementation(
        "micro.ymmsl", "micro", default_timeout=5.0
    )

You can also override the timeout for individual receive calls:

.. code-block:: python

    reply = tester.receive("final", timeout=2.0)


API reference
=============

.. autoclass:: libmuscle.pytest.MuscleTester
   :members:
   :undoc-members:
   :special-members: __init__, __enter__, __exit__

.. autoclass:: libmuscle.pytest.implementation_tester.ImplementationTester
   :members:
   :undoc-members:
   :special-members: __init__
