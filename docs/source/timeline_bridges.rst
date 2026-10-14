Timeline bridges
================

Timeline bridges are used when simulating processes that run simultaneously and
influence each other, and which run on similar but not identical timelines.

A simple case of this is when two programs run side-by-side on the same timeline. In
that case, they'll start at the same point in time, and then take the same timesteps, so
that after N iterations of each, they are both at the same t_N. In that case,
information can be sent directly from an O_I port on one program to a corresponding S
port on the other program, and vice versa, because the two programs send and receive the
same number of messages for any given section of simulated time.

If the two programs do not run on exactly the same timeline, but one has somewhat
smaller or larger time steps than the other, then we will get clock skew, where the
simulated time in the two components doesn't match anymore and information from the
past or the future is used rather than from the present.

If the number of messages sent doesn't match the number of messages received and
there's bidirectional communication, then we can also get a deadlock, where the
simulation halts because the programs are waiting for each other.

Timeline bridges exist to solve these problems. They allow programs (or entire models)
to interact if the timelines are neither identical nor nested, but similar and possibly
variable depending on how the simulation progresses.

Connecting components using a timeline bridge
---------------------------------------------

The simplest MUSCLE3 timeline bridge provides for unidirectional communication between
two instances' O_I and S ports. The sending side needs to have an O_I port sending the
data needed by the receiver, and the receiver needs the corresponding S port to receive
it. Furthermore, the receiving side needs an O_I port on which arbitrary data is sent
on every time step (if none are available, then you'll need to add a dummy port that
sends an empty message). All messages sent to the timeline bridge need to have correct
timestamps, as explained below.

To use the built-in timeline bridge in your model, you first need to import it:

.. code-block::

  imports:
    - from muscle3.actors.bridges import implementation unidirectional_bridge


You can then use it as the implementation for a component, and connect it to other
components as follows.

On the sending side, connect the sender's O_I port with the data to a port named
``data_in`` on the timeline bridge. On the receiving side, connect an O_I port to the
``clock_in`` port on the timeline bridge, then add a conduit from ``data_out`` on the
timeline bridge to an S port on the receiver.

Multiple parallel data conduits can be used as well, but only if they are all on the
same timeline. In that case, connect each O_I port on the sender to a port
``<something>_data_in`` on the bridge, and connect ``<something>_data_out`` on the
bridge to the corresponding port on the receiver. Make sure that the names of the data
input and output port match, or you'll get the different data items confused.

When a simulation consisting of a sender, receiver, and timeline bridge is started,
sender and receiver will initialise and enter their first iteration, when they send an
initial output on their O_I ports. The timeline bridge will receive the message from the
receiver on its ``clock_in`` port, with the receiver's current time point ``t_r_cur``
and its next time point ``t_r_next`` attached.

The timeline bridge will ignore the contents of that message, but it will use the
timestamps to decide which input messages to send to the receiver in its next message.
It will then receive those messages from the sender if needed and available, and send
the selected one(s) (see below) to the receiver, after which it will receive the next
clock message and repeat.

Sending timestamps to the bridge
--------------------------------

Timeline bridges can only work if both sender and receiver set correct timestamps on the
messages they send. The timeline bridge assumes that there is a consistent global
simulated time dimension that all the timelines in the simulation are defined on. In
simple terms: if two things happen at t=10 in two different instances, then they happen
simultaneously.

The timeline bridge expects each instance to start at a particular point in time and
then repeatedly step forwards, communicating at each step. Sender and receiver may start
and finish at different time points, and they're not required to have the same size
steps.

Messages sent on O_I by the sender and the receiver to the bridge must have
``timestamp`` set to their current time point, and the ``next_timestamp`` attribute must
be set to the next time point the instance will step to, except for on the last message
when ``None`` must be used instead to signal to the timeline bridge that no more
messages will be coming. [#f1]_

If multiple data channels are used, then the timestamps on their messages must be
identical (i.e. they have to be on the same timeline).

If an instance has variable time stepping and it doesn't know in advance how large the
next timestep will be, for example because it uses an implicit method and decreases the
``dt`` until the solver converges, then some trade-offs need to be considered. We'll
come back to this below.

Deciding which data to send
---------------------------

Which data the receiver needs depends on what it does and how it works, so you will have
to configure the timeline bridge to work with your specific scenario. The timeline
bridge can operate in two modes, one supports the theta method and the other simply
aggregates data.

Theta scheme
````````````

The theta scheme generalises the Crank-Nicolson method to include explicit and implicit
Euler schemes. It introduces a parameter ``theta`` which determines at which point
between the current and the next time point the derivative is evaluated. For the
explicit Euler scheme, ``theta`` is zero, meaning the current time point, for an
implicit scheme it is one, meaning the next time point, and for Crank-Nicolson it is one
half, meaning exactly in the middle of the time step and yielding a second-order
integrator.

In theta mode (the default), the time bridge is configured by setting ``theta`` to the
desired value in the component's settings. The bridge will use the receiver's clock
input and ``theta`` to determine the time point at which the receiver needs data, and
will then forward the last message from the sender before that point.

This is not necessarily the message closest in time to the desired point, as the first
one past the desired point may in fact be closer, and therefore may be a better
approximation. However, it is also in the future, and if two or more components form a
communication loop then this can lead to a deadlock, where each instance is waiting to
receive a message from the future, and no one can progress to produce such a message
because of that.

So, by default, only messages from before the theta point are considered by the timeline
bridge. However, if you have set up the coupling in such a way that receiving from the
future is safe, then you can set ``strict_causality`` to ``false``, which will cause the
timeline bridge to consider the next message past the theta point too.

Data aggregation
````````````````

The second mode is enabled by setting ``all_in_window`` to ``true``. In this case,
``theta`` is ignored, and the timeline bridge will send to the receiver all the
information sent by the sender in between the timestamps from the receiver's clock
message. This is sent as a list of lists, where the inner lists contain a timestamp and
the data, i.e. ``[[ts_0, data_0], [ts_1, data_1], ..., [ts_n, data_n]]`` where each
``ts_<i>`` is in the range ``[t_r_cur, t_r_next)``.

Note that if the time step of the receiver is smaller than that of the sender, or if the
receiver starts its simulation before the sender starts, then there may not be any
messages with timestamps between ``t_r_cur`` and ``t_r_next``, and the receiver may
receive an empty list.

In some cases, you may want to process the data sent by the timeline bridge before
passing it to the receiver. This can be done by adding an additional component which
receives the list (or value) from the timeline bridge on an ``F_INIT`` port, processes
it, and sends some value expected by the receiver on an ``O_F`` port. This can be used
to inter- or extrapolate, or to use a default value if the sender has no data and the
receiver cannot deal with empty inputs.

Settings
````````

The MUSCLE3 unidirectional timeline bridge has three settings that determine which data
from the sender it will send to the receiver:

+------------------+-------+---------------------------------------------------------+
|      Setting     | Type  | Description                                             |
+==================+=======+=========================================================+
|       theta      | float | Determines the point in time at which to send data as   |
|                  |       | (1 - theta) * t_r_cur + theta * t_r_next                |
+------------------+-------+---------------------------------------------------------+
| strict_causality | bool  | If ``true``, ensures that the bridge will never try to  |
|                  |       | receive messages past the theta point, or past          |
|                  |       | ``t_r_next`` if in aggregation mode.                    |
+------------------+-------+---------------------------------------------------------+
|  all_in_window   | bool  | Send all messages at or after ``t_r_cur`` and before    |
|                  |       | ``t_r_next`` in a list; ignore theta                    |
+------------------+-------+---------------------------------------------------------+



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

+-------------------+-----------+-----------+-----------+---------------+
| receiver timestep | theta = 0 | theta = 1 | theta = 1 | all_in_window |
|                   |   strict  |   strict  |  !strict  |               |
+===================+===========+===========+===========+===============+
|         a         |     1     |     3     |     4     |     1 2 3     |
+-------------------+-----------+-----------+-----------+---------------+
|         b         |     3     |     4     |     4     |       4       |
+-------------------+-----------+-----------+-----------+---------------+
|         c         |     4     |     4     |     5     |  empty list   |
+-------------------+-----------+-----------+-----------+---------------+
|         d         |     4     |     5     |     5     |       5       |
+-------------------+-----------+-----------+-----------+---------------+
|         e         |     5     |     7     |     7     |      6 7      |
+-------------------+-----------+-----------+-----------+---------------+
|         f         |     7     |     8     |     9     |       8       |
+-------------------+-----------+-----------+-----------+---------------+
|         g         |     8     |     9     |     9     |       9       |
+-------------------+-----------+-----------+-----------+---------------+
|         h         |     9     |     9     |     10    |  empty list   |
+-------------------+-----------+-----------+-----------+---------------+
|         i         |     9     |     10    |     10    |      10       |
+-------------------+-----------+-----------+-----------+---------------+


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

If you have such an implicit integrator connected to a timeline bridge as a receiver,
then you'll want to use the value of the input at whichever ``t_cur + dt`` you're
stepping to, and that point will change as you reduce ``dt``. So the best solution in
this case is to send ``t_cur + dt_max`` as the value for ``next_timestamp``, and
configure the timeline bridge with ``all_in_window`` set to ``true``. You'll then
receive all messages between ``t_cur`` and ``t_cur + dt_max`` with timestamps, meaning
that you can always pick a value close to ``t_cur + dt`` from the list, or interpolate,
while trying to find a ``dt`` for which the solver converges.

If the implicit integrator is connected to a timeline bridge as a sender, then the only
way for the sender to know for sure what the last message before the receiver's
``t_cur`` or ``t_next`` is, is to receive the sender's first message past that point.
This will work if there's a one way connection, because then the sender can simply run
ahead a little bit of the receiver.

In this case, you can set ``strict_causality`` to ``false``, which will cause the bridge
to ignore the ``next_timestamp`` on the sender's messages and keep receiving until it
has the first message past the point where it needs data, thus ensuring that it will
send the closest message (in theta mode) or all messages in the window with
``all_in_window`` set to ``true``.

If there's bidirectional communication and both sides are trying to receive the last
message before ``t_next``, then we can get into a situation where both timeline bridges
are trying to receive that first message past ``t_next`` of each model, which will never
arrive because neither model can step to its ``t_next`` because it's still waiting for
input. As a result, no progress is possible, a situation called a deadlock. MUSCLE3 will
detect this and shut down the simulation, but of course that does not give us the
simulation result we want.

There are a few potential solutions to this. The simplest is to have the sender set
``next_timestamp`` to ``t_cur + dt_max`` while leaving ``strict_causality`` at the
default ``true``. This will result in the timeline bridge receiving messages from the
sender until the last one before the first one that could potentially step past the
``t_next`` of the receiver. If the sender actually makes a smaller time step, then its
next message will be in range, but won't be sent to the receiver. The receiver will then
use what it has, or possibly extrapolate a bit, which will hopefully still give good
results.

Another solution is to have a component that can predict the future. This typically
happens when modelling closed-loop control systems, where e.g. a model describing the
physical system is connected to a simulated sensor, which connects to a simulated
controller, which connects to a simulated actuator, which in turn connects back to the
physical system model.

A natural way to model closed-loop control in MUSCLE3 is to run each of the four
components on its own timeline, according to the physics, sampling rate, or control loop
frequency, and then connect them together pairwise using timeline bridges. If the
physics model uses variable time stepping, then it would have to run past the end of the
sensor's next measurement window to ensure that the sensor gets all data, and to do that
it needs control input valid until that time.

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

.. rubric:: Footnotes

.. [#f1] Using ``None`` here to signal that this is the last message is not perfect.
   It looks like it may be possible to avoid this if we extend MUSCLE3 a bit, but that
   needs a bit more thought and work. For now, this is how to do it.
