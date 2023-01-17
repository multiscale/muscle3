Checkpointing deep-dive
=======================

This checkpointing deep-dive explains the details of the distributed
checkpointing implemented in MUSCLE3. Usually you will not need to read or
understand these details when you want to run simulations with checkpointing
(see :ref:`User tutorial`) or implement checkpointing in a MUSCLE3 component
(see :ref:`Developer tutorial`).

.. contents:: Checkpointing deep-dive contents
    :local:


Consistency for simulation time checkpoints
-------------------------------------------

In this section we take a look at the three allowed coupling types in the MMSF:
call/release, interact and dispatch coupling. In the following sections
we will analyze consistency for each of the coupling types.

The underlying assumption is: if we can take consistent snapshots for each pair
of coupled components, we can take consistent snapshots of the whole workflow.

Call/release coupling
`````````````````````

In this section we will look at the call/release coupling mode. The first
example simulation consists of two components: Component 1 and Component 2. They
are coupled as follows:

-   The ``O_I`` port of Component 1 is connected to the ``F_INIT`` port of
    Component 2.
-   The ``O_F`` port of Component 2 is connected to the ``S`` port of
    Component 1.

.. code-block:: text
    :caption: Example run for three iterations of Component 1.

    Component 1:  |Fi|Oi|........ S |Oi|........ S |Oi|........ S |Of|
                        \        /     \        /     \        /
    Component 2:        |Fi|S |Of|..... Fi|S |Of|..... Fi|S |Of|

The above schema shows the Operator (``F_INIT``, ``O_I``, ``S``, ``Of``) that
each comonent is in during the run. The dots (``...``) indicate a blocking
call: in this case it is the ``receive`` during the ``S`` operator of Component
1, and the ``receive`` of the ``F_INIT`` operator of Component 2.

Let's add the simulation time for each component on the example timeline.

-   During ``F_INIT``, the internal time is initialized. Component 1 initializes
    to a constant ``t0``. Component 2 initializes the time to the timestamp
    received in the message.
-   During ``S`` the state is updated and the simulation time may move forward.

.. code-block:: text
    :caption: Example run, also showing simulation times in the components.

      time        |t0            |t2            |t4            |t6
    Component 1:  |Fi|Oi|........ S |Oi|........ S |Oi|........ S |Of|
                        \        /     \        /     \        /
    Component 2:        |Fi|S |Of|..... Fi|S |Of|..... Fi|S |Of|
      time              |t0|t1         |t2|t3         |t4|t5

We assume that each component only moves forward in time, so
:math:`t_0 \le t_2 \le t_4 \le t_6` and :math:`t_0 \le t_1`, :math:`t_2 \le t_3`
and :math:`t_4 \le t_5`. The time evolution of Component 2 should be smaller
than the time step of Component 1 in this coupling type. Therefore:
:math:`t_1 \le t_2`, :math:`t_3 \le t_4` and :math:`t_5 \le t_6`.

.. rubric:: Introducing checkpoints

Component 1 can take checkpoints immediately after the ``S`` operator. Component
2 can only take checkpoints after the ``O_F`` operator. Let's investigate what
needs to happen when a checkpoint :math:`t_c` is requested for different values
of :math:`t_c`:

1.  :math:`t_c \leq t_0`
2.  :math:`t_0 < t_c \leq t_1`
3.  :math:`t_1 < t_c \leq t_2`
4.  :math:`t_2 < t_c  \leq t_4`

Note: a checkpoint :math:`t_4 < t_c  \leq t_6` would behave the same as scenario
4, just at a later point in the simulation, so we won't work out later
checkpoints in detail.

.. tabs::

    .. tab:: :math:`t_c \leq t_0`

        Both components will take a snapshot at the earliest possible moment,
        indicated with a ``C`` block in the timelines below.

        You may notice that the ``C`` block in Component 2 is blocking. Although
        the internal time of Component 2 already exceeded the checkpoint time,
        :ref:`Final snapshots` actually determine if a snapshot should be
        taken based on the message(s) arriving during the next ``F_INIT``.

        .. rubric:: Consistency

        Both snapshots have the same message counts: 1 message sent/received per
        conduit. When resuming, Component 1 starts by sending a new message on
        its ``O_I`` port, and Component 2 runs ``F_INIT`` as usual.

        .. code-block:: text

              time        |t0            |t2                  |t4            |t6
            Component 1:  |Fi|Oi|........ S |C |Oi|........... S |Oi|........ S |Of|
                                \        /        \           /     \        /
            Component 2:        |Fi|S |Of|........ C |Fi|S |Of|..... Fi|S |Of|
              time              |t0|t1               |t2|t3         |t4|t5

    .. tab:: :math:`t_0 < t_c \leq t_1` and :math:`t_1 < t_c \leq t_2`

        For both checkpoint times, a snapshot will be taken at the earliest
        possible moment.

        After the first ``S`` operator, Component 1 is at :math:`t=t_2` which is
        after the checkpoint time, so it takes a snapshot. After the first reuse
        loop, Component 2 receives a message with :math:`t=t_2` which is after
        the checkpoint time, so it will take a snapshot at the end of the first
        reuse loop.

        .. rubric:: Consistency

        Both snapshots have the same message counts: 1 message sent/received per
        conduit. When resuming, Component 1 starts by sending a new message on
        its ``O_I`` port, and Component 2 runs ``F_INIT`` as usual.

        .. code-block:: text

              time        |t0            |t2                  |t4            |t6
            Component 1:  |Fi|Oi|........ S |C |Oi|........... S |Oi|........ S |Of|
                                \        /        \           /     \        /
            Component 2:        |Fi|S |Of|........ C |Fi|S |Of|..... Fi|S |Of|
              time              |t0|t1               |t2|t3         |t4|t5

    .. tab:: :math:`t_2 < t_c  \leq t_4`

        Both components will take a snapshot at the earliest possible moment,
        indicated with a ``C`` block in the timelines below.

        After the first ``S`` operator, Component 1 is at :math:`t=t_2` which is
        before the checkpoint time. After the second ``S`` operator it has
        passed the checkpoint time, so it takes a snapshot. This works similarly
        for Component 2.

        .. rubric:: Consistency

        Both snapshots have the same message counts: 2 messages sent/received
        per conduit. When resuming, Component 1 starts by sending a new message
        on its ``O_I`` port, and Component 2 runs ``F_INIT`` as usual.

        .. code-block:: text

              time        |t0            |t2            |t4                  |t6
            Component 1:  |Fi|Oi|........ S |Oi|........ S |C |Oi|........... S |Of|
                                \        /     \        /        \           /
            Component 2:        |Fi|S |Of|..... Fi|S |Of|........ C |Fi|S |Of|
              time              |t0|t1         |t2|t3               |t4|t5


.. rubric:: Micro component with time integration and intermediate snapshots

Let's see what happens when we replace Component 2 by Component 3, which does
time integration and implements intermediate snapshots.


.. code-block:: text
    :caption: Example run, also showing simulation times in the components.

      time        |t0                  |t4                  |t8
    Component 1:  |Fi|Oi|.............. S |Oi|.............. S |Oi|........
                        \              /     \              /     \
    Component 3:        |Fi|S |S |S |Of|..... Fi|S |S |S |Of|..... Fi|S |S
      time              |t0|t1|t2|t3         |t4|t5|t6|t7         |t8|t9|t10

For the same reasons as with Component 2, :math:`t_i \leq t_{i+1}` for
:math:`i=0,1,...`.

Now, Component 3 can make intermediate snapshots between each ``S``, but also
final snapshots. Let's see what effect that has for different checkpoint times:

.. tabs::

    .. tab:: :math:`t_c \leq t_1`

        In this case, both components will take a snapshot at the first possible
        moment: right after their first ``S`` block.

        .. rubric:: Consistency

        Now the snapshots have different message counts. For the ``O_I ->
        F_INIT`` conduit both components see 1 message sent/received. For the
        other conduit, however, Component 1 already received a message that is
        not sent in Component 3's snapshot.

        When resuming, Component 3 resumes in its state update loop and sends a
        message back to Component 1 during ``O_F``. This message is discarded by
        Component 1. From that point, the simulation can resume as usual.

        .. code-block:: text

              time        |t0                     |t4                     |t8
            Component 1:  |Fi|Oi|................. S |C |Oi|.............. S |Oi|........
                                \                 /        \              /     \
            Component 3:        |Fi|S |C |S |S |Of|........ Fi|S |S |S |Of|..... Fi|S |S
              time              |t0|t1   |t2|t3            |t4|t5|t6|t7         |t8|t9|t10

    .. tab:: :math:`t_1 < t_c \leq t_2`

        This is quite similar to the previous case. The difference is that
        Component 3 takes its snapshot after the second ``S`` block.

        .. code-block:: text

              time        |t0                     |t4                     |t8
            Component 1:  |Fi|Oi|................. S |C |Oi|.............. S |Oi|........
                                \                 /        \              /     \
            Component 3:        |Fi|S |S |C |S |Of|........ Fi|S |S |S |Of|..... Fi|S |S
              time              |t0|t1|t2   |t3            |t4|t5|t6|t7         |t8|t9|t10

    .. tab:: :math:`t_3 < t_c \leq t_4`

        The checkpoint for Component 1 does not change. However, in this case
        Component 3 takes a :ref:`final snapshot <Final snapshots>` instead of
        an :ref:`intermediate snapshot <Intermediate snapshots>`.

        .. rubric:: Consistency

        Both snapshots have the same message counts: 1 message sent/received
        per conduit. When resuming, Component 1 starts by sending a new message
        on its ``O_I`` port, and Component 2 runs ``F_INIT`` as usual.

        .. code-block:: text

              time        |t0                  |t4                        |t8
            Component 1:  |Fi|Oi|.............. S |C |Oi|................. S |Oi|........
                                \              /        \                 /     \
            Component 3:        |Fi|S |S |S |Of|........ C |Fi|S |S |S |Of|..... Fi|S |S
              time              |t0|t1|t2|t3               |t4|t5|t6|t7         |t8|t9|t10


Interact coupling
`````````````````

In this section we will look at the interact coupling mode. This example
simulation consists of two components: Component 1 and Component 2. They are
coupled as follows:

-   The ``O_I`` port of Component 1 is connected to the ``S`` port of
    Component 2.
-   The ``O_I`` port of Component 2 is connected to the ``S`` port of
    Component 1.

.. code-block:: text
    :caption: Example lock-step interact run for three iterations.

      time        |t0   |t1   |t2   |t3
    Component 1:  |Fi|Oi|S |Oi|S |Oi|S |Of|
                        X     X     X
    Component 2:  |Fi|Oi|S |Oi|S |Oi|S |Of|
      time        |t0   |t1   |t2   |t3

Let's see what happens for different checkpoint times:

.. tabs::

    .. tab:: :math:`t_c \leq t_1`

        In this case, both components make a snapshot After the first ``S``
        block.

        .. rubric:: Consistency

        Both snapshots have the same message counts: 1 message sent/received
        per conduit. When resuming, both components send the next message at
        ``O_I`` and continue with their ``S``.

        .. code-block:: text

                  time        |t0   |t1      |t2   |t3
                Component 1:  |Fi|Oi|S |C |Oi|S |Oi|S |Of|
                                    X        X     X
                Component 2:  |Fi|Oi|S |C |Oi|S |Oi|S |Of|
                  time        |t0   |t1      |t2   |t3

    .. tab:: :math:`t_1 < t_c \leq t_2`

        This is almost the same as on the previous tab, just at a later point in
        the run.

        .. code-block:: text

                  time        |t0   |t1   |t2      |t3
                Component 1:  |Fi|Oi|S |Oi|S |C |Oi|S |Of|
                                    X     X        X
                Component 2:  |Fi|Oi|S |Oi|S |C |Oi|S |Of|
                  time        |t0   |t1   |t2      |t3

If the two components do not use the same time step, a scale bridge is required
to interpolate. See ``docs/source/examples/python/interact_coupling.py`` for an
implementation of such a component. The timeline becomes a bit more complicated
now:

.. code-block:: text
    :caption: Example interact run. Component 1 has a smaller time step than Component 2.

      time        |t0            |t1                     |t2         |t4
    Component 1:  |Fi|Oi|........ S |Oi|................. S |Oi|..... S |Oi|...........
                        \        /     \                 /     \     /     \
    Scale bridge:       |S |S |Oi|..... S |Oi|..... S |Oi|..... S |Oi|..... S |Oi|.....
                           /                 \     /                             \
    Component 2:     |Fi|Oi|................. S |Oi|............................. S |Oi
      time           |t0                     |t3                                 |t5

Let's see what happens for different checkpoint times:

.. tabs::

    .. tab:: :math:`t_c \leq t_0`

        In this case, both components make a snapshot after the first ``S``
        block. The scale bridge creates a snapshot after the first two ``S`` are
        complete.

        .. rubric:: Consistency

        Both component snapshots have received one more message on ``S`` than
        the scale bridge has sent. This is no problem: when resuming, the scale
        bridge will send the messages again, but those are discarded by both
        components.

        .. code-block:: text

              time        |t0               |t1                           |t2         |t4
            Component 1:  |Fi|Oi|........... S |C |Oi|.................... S |Oi|..... S |Oi|...........
                                \           /        \                    /     \     /     \
            Scale bridge:       |S |S |C |Oi|........ S |Oi|........ S |Oi|..... S |Oi|..... S |Oi|.....
                                /                          \        /                             \
            Component 2:     |Fi|Oi|....................... S |C |Oi|............................. S |Oi
              time           |t0                           |t3                                    |t5

    .. tab:: :math:`t_0 < t_c \leq t_1`

        In this case, both components make a snapshot after the first ``S``
        block. The scale bridge creates a snapshot after receiving the second
        message from Component 2.

        .. rubric:: Consistency

        In this case, the scale bridge has received one more message on its
        ``S`` port at its checkpoint moment, than the components have sent at
        their checkpoints. Again, this is no problem: the components send their
        messages again when resuming, but these are discarded by the scale
        bridge.

        .. code-block:: text

              time        |t0            |t1                              |t2         |t4
            Component 1:  |Fi|Oi|........ S |C |Oi|....................... S |Oi|..... S |Oi|...........
                                \        /        \                       /     \     /     \
            Scale bridge:       |S |S |Oi|........ S |Oi|........ S |C |Oi|..... S |Oi|..... S |Oi|.....
                                /                       \        /                                \
            Component 2:     |Fi|Oi|.................... S |C |Oi|................................ S |Oi
              time           |t0                        |t3                                       |t5

    .. tab:: :math:`t_1 < t_c \leq t_2`

        Now component 1 takes a snapshot after its second ``S`` phase. Component
        still takes a snapshot after its first ``S`` phase. The scale bridge
        checkpoints after receiving the third message from Component 1.

        .. rubric:: Consistency

        Again, the scale bridge has received one more message on its
        ``S`` port at its checkpoint moment, than the components have sent at
        their checkpoints. Again, this is no problem: the components send their
        messages again when resuming, but these are discarded by the scale
        bridge.

        .. code-block:: text

              time        |t0            |t1                        |t2               |t4
            Component 1:  |Fi|Oi|........ S |Oi|.................... S |C |Oi|......... S |Oi|...........
                                \        /     \                    /        \        /     \
            Scale bridge:       |S |S |Oi|..... S |Oi|........ S |Oi|........ S |C |Oi|..... S |Oi|.....
                                /                    \        /                                   \
            Component 2:     |Fi|Oi|................. S |C |Oi|................................... S |Oi
              time           |t0                     |t3                                          |t5


Dispatch coupling
`````````````````

Finally, we take a look at two component coupled in dispatch:

-   The ``O_F`` port of Component 1 is connected to the ``F_INIT`` port of
    Component 2.

This leads to the following timeline:

.. code-block:: text
    :caption: Example lock-step interact run for three iterations.

      time        |t0|t1|t2|t3
    Component 1:  |Fi|S |S |S |Of|
                                 \
    Component 2:                 |Fi|S |S |S |Of|
      time                       |t3|t4|t5|t6

.. tabs::

    .. tab:: :math:`t_c \leq t_1`

        In this case, both components make a snapshot after the first ``S``
        block.

        .. rubric:: Consistency

        The snapshot of Component 1 can be combined with the snapshot of
        Component 2, but then all remaining work of Component 1 will be ignored
        by Component 2. It is also possible to restart Component 2 from scratch
        (this is also consistent).

        .. code-block:: text

              time        |t0|t1   |t2|t3
            Component 1:  |Fi|S |C |S |S |Of|
                                            \
            Component 2:                    |Fi|S |C |S |S |Of|
              time                          |t3|t4|   t5|t6

    .. tab:: :math:`t_1 < t_c \leq t_2`

        This is similar to the previous tab. However, Component 1 takes a
        snapshot at a later point.


    .. tab:: :math:`t_3 < t_c \leq t_4`

        In this case, Component 1 does not take a snapshot, unless either:

        1.  A :ref:`checkpoint rule is defined <Defining checkpoints>` for
            ``at_end``, or
        2.  Component 1 is executed again (for example, when this is a
            sub-workflow in a call/release coupling) and a final snapshot is
            triggered.

        .. rubric:: Consistency

        When a final snapshot is taken by Component 1, it will be consistent
        with any checkpoint taken during the exeuction of Component 2 and we can
        restart the workflow.

        .. code-block:: text

              time        |t0|t1|t2|t3
            Component 1:  |Fi|S |S |S |Of|C?
                                         \
            Component 2:                 |Fi|S |C |S |S |Of|
              time                       |t3|t4|   t5|t6


(In)consistency for wallclock time checkpoints
----------------------------------------------

In the current implementation, wallclock time checkpoints are taken as soon as
possible after exceeding a certain wallclock time. Let's look at an example
where this is not leading to consistent workflow snapshots.

This example is similar to the :ref:`Interact coupling` example seen previously.

-   The ``O_I`` port of Component 1 is connected to the ``S`` port of
    Component 2.
-   The ``O_I`` port of Component 2 is connected to the ``S`` port of
    Component 1.

However, let's now look at the wallclock time and assume that Component 1's
``S`` Operator takes longer than Component 2's, compute time indicated by
``~~``:

.. code-block:: text

    Wallclock time:         |w1|w2    |w3|w4
    Component 1:  |Fi|Oi|.S ~~~|Oi|.S ~~~|Oi|.S ~~~|Of|
                        \/      __\/      __\/
                        /\     /   \     /   \
    Component 2:  |Fi|Oi|.S |Oi|... S |Oi|... S |Of|

Because Component 1 spends more time in ``S``, Component 2 is waiting in each
following iteration of ``S``. Let's see what happens for different wallclock
time checkpoint moments :math:`w_c`:

.. tabs::

    .. tab:: :math:`w_c \leq w_1`

        In this case, both components make a snapshot after the first ``S``
        block.

        .. rubric:: Consistency

        At the moment of snapshot, both components have the same number of
        messages sent/received on their conduits. This is consistent.

        .. code-block:: text

            Wallclock time:         |w1|w2       |w3|w4
            Component 1:  |Fi|Oi|.S ~~~|C |Oi|.S ~~~|Oi|.S ~~~|Of|
                                \/         __\/      __\/
                                /\        /   \     /   \
            Component 2:  |Fi|Oi|.S |C |Oi|... S |Oi|... S |Of|

    .. tab:: :math:`w_1 < w_c \leq w_2`

        Component 1 takes a snapshot after the first ``S`` block, but Component
        2 after its second ``S`` block.

        .. rubric:: Consistency

        The created snapshots are not consistent: Component 2 has sent 1 more
        message than Component 1 has received. When resuming Component 1 would
        wait for a message that never comes again, so this is not a valid resume
        point.

        .. code-block:: text

            Wallclock time:         |w1|w2       |w3|w4
            Component 1:  |Fi|Oi|.S ~~~|C |Oi|.S ~~~|Oi|.S ~~~|Of|
                                \/      _____\/        \/
                                /\     /      \        /\
            Component 2:  |Fi|Oi|.S |Oi|...... S |C |Oi|. S |Of|

As you can see, the second scenario does not lead to consistent checkpoints.

