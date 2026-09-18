Time bridges
============

Time bridges are used when simulating processes that run simultaneously and influence
each other, and which run on similar but not identical timelines.

A simple case of this is when two programs run side-by-side on the same timeline. In
that case, they'll start at the same point in time, and then take the same timesteps, so
that after N iterations of each, they are both at the same t_N. In that case,
information can be sent directly from an O_I port on one program to a corresponding S
port on the other program, and vice versa, because the two programs send and receive the
same number of messages for any given section of simulated time.

If the two programs do not run on exactly the same timeline, but one has somewhat
smaller or larger time steps than the other or the size of the steps varies, then this
will no longer work, because the number of messages sent by one side will not match the
number of times the other tries to receive. This leads to clock skew (where information
from the past or the future is used instead of from the present), or in the case of
bidirectional communication to deadlock, where the simulation halts because the programs
are waiting for each other.

Time bridges exist to solve these problems, and allow connecting programs (or entire
models) if the time lines are neither identical nor nested, but similar and possibly
variable depending on how the simulation progresses.

Connecting components using a time bridge
-----------------------------------------

The standard MUSCLE3 time bridge provides for unidirectional communication between two
instances' O_I and S ports. The sending side needs to have an O_I port sending the data
needed by the receiver, and the receiver needs the corresponding S port to receive it.
Furthermore, the receiving side needs an O_I port on which arbitrary data is sent on
every time step (if none are available, then you'll need to add a dummy port that sends
an empty message). All messages sent to the time bridge need to have a correct timestamp
value and ``next_timestamp`` set as well, except for the last message on which
``next_timestamp`` must be unset to tell the time bridge to stop receiving.

To use the built-in time bridge in your model, you first need to import it:

```yaml

imports:
  - from muscle3.time_bridges import implementation unidirectional_bridge

```

You can then use it as the implementation for a component, and connect it to other
components as follows.

On the sending side, connect the sender's O_I port with the data to a port named
<something>`_data_in` on the time bridge. On the receiving side, connect an O_I port to
the `clock_in` port on the time bridge, then add a conduit from <something>`_data_out`
on the time bridge to an S port on the receiver. Make sure the names of the data input
and output ports match. More than one data conduit can be connected on both sides, but
they have to be on the same timeline.

When a simulation consisting of a sender, receiver, and time bridge is started, sender
and receiver will initialise and enter their first iteration, when they send an initial
output on their O_I ports. The time bridge will receive the message from the receiver
on its `clock_in` port, with the receiver's current time point `t_r_cur` and its next
time point `t_r_next` attached.

The time bridge will ignore the contents of that message, but it will use the timestamps
to decide which input messages to send to the receiver in its next message. It will then
receive those messages from the sender if needed and available, collate them into a
list, and send that list to the receiver, after which it will receive the next clock
message and repeat.

Deciding which data to send
---------------------------

Which data the receiver needs depends on what it does and how it works, so you will have
to configure the time bridge to work with your specific scenario. Here are a few common
cases, assuming that the receiver is currently at ``t_r_cur`` and is trying to step to
``t_r_next``:

- The receiver uses an explicit Euler solver. In this case, its next state will be
  calculated based on the current state and any other inputs at ``t_r_cur``, and the
  receiver will likely want to use the latest value before ``t_r_cur``.

- The receiver uses an implicit Euler solver. Its next state will be calculated based on
  the current state and any other inputs at ``t_r_next``, so it will likely want to use
  the latest value before ``t_r_next``.

- The receiver integrates or averages the received values, rather than using a point
  sample. In that case, ``t_r_cur`` to ``t_r_next`` is the next integration window, and
  it needs to receive all messages with timestamps within that range.

Note that if the time step of the receiver is smaller than that of the sender, or if the
receiver starts its simulation before the sender starts, then there may not be any
messages with timestamps between ``t_r_cur`` and ``t_r_next``, and the receiver may
receive an empty list.

The standard MUSCLE3 time bridge has three settings that determine which data from the
sender it will send to the receiver:


| Setting | Type | Description |
|---------|------|-------------|
| recv_last_before_cur | int | The last message before or at ``t_r_cur`` |
| recv_last_before_next | int | The last message before or at ``t_r_next`` |
| recv_cur_to_next | bool | All messages after ``t_r_cur`` and before or at ``t_r_next`` |


The types are different here for future extensibility. For now ``recv_last_before_cur``
and ``recv_last_before_next`` can be set to ``0`` or ``1`` only, and
``recv_cur_to_next`` to ``true`` or ``false``.

If ``recv_cur_to_next`` is set and ``recv_last_before_next`` equals ``1``, then the last
message before or at ``t_r_next`` will be included only once.

If ``recv_last_before_cur`` and ``recv_last_before_next`` are both ``1``, then
messages may be received twice, once as the last message before ``t_r_next`` and then
again on the next timestep as the last message before ``t_r_cur``.

At each time step, the receiver will receive a list from the time bridge, containing
each selected message. Each item in the list will be a dictionary with keys
``timestamp``, ``next_timestamp``, and ``data``, each mapping to the corresponding field
from the sender's message. The list will be empty if no matching messages are available.


The following diagram shows sender and receiver timelines, with the sender producing
outputs at the numbered time points and the receiver timesteps indicated by letters in
between its ``t_r_cur`` and ``t_r_next``::

              1 23    4       5    6 7  8    9          10
  sender      | ||    |       |    | |  |    |          |

  receiver    |      |   | |   |      |     |   |   |    |
                 a     b  c  d     e     f    g   h   i

Given these timelines and the settings, the messages received by the receiver are as
follows (with rows deduplicated, so the list received in step ``a`` is ``[1, 2, 3]`` if
all three outputs are enabled):

+-------------------+-----------------+-------------+------------------+
| receiver timestep | last_before_cur | cur_to_next | last_before_next |
|                   |        1        |    true     |        1         |
+===================+=================+=============+==================+
|         a         |        1        |     2 3     |        3         |
+-------------------+-----------------+-------------+------------------+
|         b         |        3        |      4      |        4         |
+-------------------+-----------------+-------------+------------------+
|         c         |        4        |             |        4         |
+-------------------+-----------------+-------------+------------------+
|         d         |        4        |      5      |        5         |
+-------------------+-----------------+-------------+------------------+
|         e         |        5        |     6 7     |        7         |
+-------------------+-----------------+-------------+------------------+
|         f         |        7        |      8      |        8         |
+-------------------+-----------------+-------------+------------------+
|         g         |        8        |      9      |        9         |
+-------------------+-----------------+-------------+------------------+
|         h         |        9        |             |        9         |
+-------------------+-----------------+-------------+------------------+
|         i         |        9        |     10      |        10        |
+-------------------+-----------------+-------------+------------------+


Variable timestepping
---------------------

In some cases, a model may not know in advance how large its next timestep will be.
Implicit integrators do not always converge at a given timestep size, and which timestep
size works may vary across time. Instead of always running at a very small timestep,
it's common practice to set a maximum timestep, try to advance time using that, and if
the solver fails to converge reduce the timestep and try again.

When the solver eventually converges for some timestep size, the simulation advances to
a new point in time that becomes the new ``t_cur``, and we want to send a new message
based on the new state. The ``timestamp`` on that message should be ``t_cur``, but it's
impossible at this point to say what ``next_timestamp`` should be because we don't know
at which ``dt`` the solver will converge on the next try, and even if we could predict
that in principle, that solve may depend on data that we will receive after sending this
message and then so will the maximum achievable ``dt``.

If you have such an implicit integrator connected to a time bridge as a receiver, then
you'll want to use the value of the input at whichever ``t_cur + dt`` you're stepping
to, and that point will change as you reduce ``dt``. So the best solution in this case
is to send ``t_cur + dt_max`` as the value for ``next_timestamp``, and configure the
time bridge with ``cur_to_next`` set to ``true``. You'll then receive all messages
between ``t_cur`` and ``t_cur + dt_max``, meaning that you can always pick a value close
to ``t_cur + dt`` from the list, or interpolate, while trying to find a ``dt`` for which
the solver converges.

If the implicit integrator is connected to a time bridge as a sender, then the only way
for the sender to know for sure what the last message before the receiver's ``t_cur`` or
``t_next`` is, is to receive the sender's first message past that point. This will work
if there's a one way connection, because then the sender can simply run ahead a little
bit of the receiver.

However, if there's bidirectional communication and both sides are trying to receive the
last message before ``t_next``, then we can get into a situation where both time bridges
are trying to receive that first message past ``t_next`` of each model, which will never
arrive because neither model can step to its ``t_next`` because it's still waiting for
input. As a result, no progress is possible, a situation called a deadlock. MUSCLE3 will
detect this and shut down the simulation, but of course that does not give us the
simulation result we want.

There are a few potential solutions to this. The simplest is to have the sender set
``next_timestamp`` to ``t_cur + dt_max``. This will result in the time bridge receiving
messages from the sender until the last one before the first one that could potentially
step past the ``t_next`` of the receiver. If it actually makes a smaller time step, then
its next message will be in range, but won't be sent to the receiver. The receiver will
then use what it has, or possibly extrapolate a bit, which will hopefully still give
good results.

Another solution is to have a component that can predict the future. This typically
happens when modelling closed-loop control systems, where e.g. a model describing the
physical system is connected to a simulated sensor, which connects to a simulated
controller, which connects to a simulated actuator, which in turn connects back to the
physical system model.

A natural way to model closed-loop control in MUSCLE3 is to run each of the four
components on its own timeline, according to the physics, sampling rate, or control loop
frequency, and then connect them together pairwise using time bridges. If the physics
model uses variable time stepping, then it would have to run past the end of the
sensor's next measurement window, and to do that it needs control input valid until that
time.

This may seem impossible at first, because the control input is based on the
measurement, but causality dictates that the control input is based on a *past*
measurement, not a simultaneous one. In practice, what happens is that the physics model
runs past the end of the measument window, its state is sent to the sensor simulation
which produces a simulated measurement, which is sent to the next run of the
controller's control loop. This produces a feedback, which is sent to the actuator
model, which produces a description of the actuator's response over the time period
until the next feedback, which gets sent to the physics model.

If the time period covered by this actuator response data runs forward far enough to
cover the next measurement window of the sensor plus ``dt_max``, then the physics model
will have enough data to proceed and no deadlock will occur. If you're not quite getting
there, it may help to reduce ``dt_max``, explicitly model processing and transmission
delays in and between sensor, controller, and actuator, or make the actuator simulation
produce values a little bit beyond the next point in time at which it will produce data,
in hopes that the extension won't differ too much from the start of the next data it
sends.

