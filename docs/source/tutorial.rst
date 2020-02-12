Tutorial with Python
====================

In this section, we'll look at a few examples of how to use MUSCLE 3 to create a
multiscale simulation in Python.

`The source code for these examples is here
<https://github.com/multiscale/muscle3/tree/master/docs/source/examples/python>`_.
You can also clone the repository or download the source (see the C++ part of
the Installation section) and go to ``docs/source/examples/python``, or
copy-paste the code from here.

The easiest way to get set up is to create a virtualenv and then install MUSCLE
3 and the additional requirements inside it:

.. code-block:: bash

  example/python$ python3 -m venv venv                    # create venv
  example/python$ . venv/bin/activate                     # activate it
  example/python$ pip3 install -r requirements.txt        # install dependencies


If you get an error message saying amongst others ``error: invalid command
'bdist_wheel'``, try running ``pip3 install wheel`` and then ``pip3 install -r
requirements.txt`` again to fix it.

Our first example is a reaction-diffusion model on a 1D grid. It consists of a
reaction model coupled to a diffusion model in a macro-micro fashion, with the
diffusion model the macro-model and the reaction model the micro-model. In a
macro-micro model with timescale separation, the micro model does a full run (of
many timesteps) for every timestep of the macro-model. Thus, the macro-model
effectively calls the micro-model before each state update, sending it the
current state and using its output as an input for the state update operation.

Here's how to implement that with MUSCLE 3. (A detailed explanation follows
below the code.)

.. literalinclude:: examples/python/reaction_diffusion.py
  :caption: ``docs/source/examples/python/reaction_diffusion.py``
  :language: python

Let's take it step by step.


Importing headers
-----------------

.. code-block:: python

  from collections import OrderedDict
  import logging
  import os

  import numpy as np

  from libmuscle import Instance, Message
  from libmuscle.runner import run_simulation
  from ymmsl import (ComputeElement, Conduit, Configuration, Model, Operator,
                     Settings)


As usual, we begin by importing some required libraries. OrderedDict and logging
come from the Python standard library, and NumPy provides matrix math
functionality. From libmuscle, we import :class:`libmuscle.Instance`, which will
represent a model instance in the larger simulation, and
:class:`libmuscle.Message`, which represents a MUSCLE message as passed between
instances.  The :func:`libmuscle.run_simulation` function allows us to run a
complete simulation from a single Python file, as opposed to having to start the
different instances and the manager separately.

In order to describe our model, we use a number of definitions from
`ymmsl-python`. More about those below.

A simple submodel
-----------------

Next is the reaction model. It is defined as a single Python function that takes
no arguments and returns nothing. (Note that this code uses type annotations to
show the types of function arguments and return values. These are ignored by the
Python interpreter, and also by MUSCLE 3, so you don't have to use them if you
don't want to.)

The first step in a MUSCLE model is to create an :class:`libmuscle.Instance`
object:

.. code-block:: python

  def reaction() -> None:
      instance = Instance({
              Operator.F_INIT: ['initial_state'],       # list of float
              Operator.O_F: ['final_state']})           # list of float
      # ...

The constructor takes a single argument, a dictionary that maps operators to
lists of ports. Ports are used by submodels to exchange messages with the
outside world. Ports can be input ports or output ports, but not both at the
same time. In this model, we have a single input port named ``initial_state``
that will receive an initial state at the beginning of the model run, and a
single output port named ``final_state`` that sends the final state of the
reaction simulation to the rest of the simulation. Note that the type of data
that is sent is documented in a comment. This is obviously not required, but it
makes life a lot easier if someone else needs to use the code or you haven't
looked at it for a while, so it's highly recommended. Available types are
described below.

The operators will become clear shortly.

The reuse loop
--------------

.. code-block:: python

  while instance.reuse_instance():
      # F_INIT
      # State update loop
      # O_F

Now that we have an :class:`libmuscle.Instance` object, we can start the *reuse
loop*. In multiscale simulations, submodels often have to run multiple times,
for instance because they're used as a micro-model or because they are part of
an ensemble that cannot be completely parallelised. In order to accomplish
this, the entire model is wrapped into a loop. Exactly when this loop ends
depends on the behaviour of the whole model, and is not easy to determine, but
fortunately MUSCLE will do that for us if we call the
:meth:`libmuscle.Instance.reuse_instance` method.

Initialisation: Settings and receiving messages
-----------------------------------------------

.. code-block:: python

  while instance.reuse_instance():
      # F_INIT
      t_max = instance.get_setting('t_max', 'float')
      dt = instance.get_setting('dt', 'float')
      k = instance.get_setting('k', 'float')

      msg = instance.receive('initial_state')
      U = np.array(msg.data)

      t_cur = msg.timestamp


Next is the first part of the model, in which the state is initialised. Pretty
much every model has such an initialisation phase at the beginning. In MUSCLE's
abstract idea of what a submodel does, the Submodel Execution Loop, this part of
the code is referred to as the F_INIT operator. Here, we ask MUSCLE for the
values of some settings that we're going to need later, in particular the total
time to simulate, the time step to use, and the model parameter ``k``. The
second argument, which specifies the expected type, is optional. If it's given,
MUSCLE will check that the user specified a value of the correct type, and if
not raise an exception. Note that getting settings needs to happen *within* the
reuse loop; doing it before can lead to incorrect results.

After getting our settings, we receive the initial state on the
``initial_state`` port. Note that we have declared that port above, and declared
it to be associated with the F_INIT operator. During F_INIT, messages can only
be received, not sent, so that declaration makes ``initial_state`` a receiving
port.

The message that we receive contains several bits of information. Here, we are
interested in the ``data`` attribute, which we assume to be an array of floats
containing our initial state, which we'll call ``U``. We'll initialise our
simulation time to the time at which that state is valid, which is contained in
the ``timestamp`` attribute. This is a double-precision float containing the
number of simulated (not wall-clock) seconds since the whole simulation started.

The state update loop
---------------------

.. code-block:: python

  # F_INIT

  while t_cur + dt < msg.timestamp + t_max:
      # O_I

      # S
      U += k * U * dt
      t_cur += dt

  # O_F

Having initialised the model, it is now time for the state update loop. This
code should look familiar: we loop until we reach our maximum time (now
relative to when we started), and on each iteration update the state according
to the model equation. This update is called operator S in the Submodel
Execution Loop, and in this model, it is determined entirely by the current
state.  Since no information from outside is needed, we do not receive any
messages, and in our :class:`libmuscle.Instance` declaration above, we did not
declare any ports associated with ``Operator.S``.

The Submodel Execution Loop specifies another operator within the state update
loop, which is called O_I and comes before S. This operator provides for
observations of intermediate states. In other words, here is where you can send
a message to the outside world with (part of) the current state. In this case,
the O_I operator is empty; we're not sending anything. While this makes the
model a bit less reusable (it won't work as a macro-model like this), it is
perfectly legal. MUSCLE tries hard to let you break the rules unless doing so
would break the model, and in that case it tries to give a helpful error
message.

Sending the final result
------------------------

.. code-block:: python

  # O_F
  instance.send('final_state', Message(t_cur, None, U.tolist()))


After the update loop is done, the model has arrived at its final state. We
finish up by sharing that final state with the outside world, by sending it on
the ``final_state`` port. The part of the code after the state update loop (but
still within the reuse loop) is known as the O_F operator in the Submodel
Execution Loop, so that is where we declared this port to live in our
:class:`libmuscle.Instance` declaration above.

To send a message, we specify the port on which to send (which must match the
declaration by name and operator), and a Message object containing the current
simulation time and the current state, converted to a plain Python list. The
optional second parameter is a second timestamp, which will be discussed below,
and is set to ``None`` here.

MUSCLE 3 uses `MessagePack <https://msgpack.org>`_ to encode messages between
models. MessagePack is a binary encoding format which can be thought of as a
binary version of JSON. That means that the message can be an integer, float,
bool, string, or a list or dictionary containing such. Like with JSON, these can
be nested, so you can send a dictionary containing lists of floats for example.

MessagePack is self-describing, so you can inspect the received message to find
out what you were sent. In most cases, all data you send on a particular
port will be of the same type, and you will expect data in a particular format
when receiving. We intentionally chose a self-describing format to keep you from
having to change a definition and recompile bindings every time you change what
you send. That does have a downside in that it makes it more difficult to see
what should be sent to someone elses submodel. So please make sure that you
document, for each port, which data type you're expecting or sending! Your
future colleagues (and possibly your future self) will thank you.

MessagePack is an extensible format, and since sending grids is very common in
these kinds of models it would be nice if NumPy arrays could be sent directly.
That's not yet implemented, but should be in a future version of MUSCLE 3.

Finally, if you want to use your own encoding, you can just send a ``bytes``
object, which will be transmitted as-is, with minimal overhead.

This concludes our reaction model. As you can see, submodels that are used with
MUSCLE 3 very much look like they would without. With one additional variable,
one extra loop, and a few send and receive statements you're ready to connect
your model into a larger simulation.


Message timestamps
------------------

In order to make a coupled simulation, we need at least two models. The second
model is the diffusion model. Its overall structure is the same as for the
reaction model, but it has a few additional features. The first of these is an
O_I operator.

.. code-block:: python

  # O_I
  t_next = t_cur + dt
  if t_next + dt > t_max:
      t_next = None
  cur_state_msg = Message(t_cur, t_next, U.tolist())
  instance.send('state_out', cur_state_msg)


Since the diffusion model is the macro-submodel in this model, it needs to send
its state to the outside world on every timestep. This is done in the O_I
operator. The message simply contains the state, converted to a standard Python
list, and it is sent on the ``state_out`` port, which was declared for the O_I
operator when we made the :class:`libmuscle.Instance` for this model. The
message is sent with the current simulation time, and a second timestamp that
gives the simulation time for the next message that will be sent on this port.
Since our time steps are fixed, this is easy to calculate. We do need to take
care to send ``None`` if this is the final message on this port however, since
there won't be another message in that case.

This deserves a bit more explanation. First, MUSCLE 3 does not use the
timestamps that are attached to the messages for anything, and in this
particular case, always sending ``None`` for the second timestamp will work
fine.  These timestamps are necessary if two submodels with timescale overlap
need to be connected together. In this case, both models will run concurrently,
and they will exchange messages between their O_I and S operators.

If their time scales (step sizes) do not match exactly, then the number of
messages sent by one submodel does not match the number of messages that the
other submodel is trying to receive, and one will end up waiting for the other,
bringing the whole simulation to a halt. To avoid this, an intermediate
component needs to be inserted, which interpolates the messages. In order to
send and receive in the correct order, this component needs to know when the
next message will be sent, and that is when the second timestamp is required.

So, to make your submodel more generically usable, it's good to set the second
timestamp. But perhaps you're trying to connect an existing codebase that uses
varying timestep sizes, and it's not easy to get it to tell you how big the
next timestep will be. In that case, if you're not doing time scale overlap,
just put ``None`` there and move on to the next problem, it'll work just fine.

Receiving messages with a default
---------------------------------

.. code-block:: python

  # S
  msg = instance.receive('state_in', default=cur_state_msg)
  if msg.timestamp > t_cur + dt:
      logger.warning('Received a message from the future!')
  U = np.array(msg.data)


The diffusion model being the macro-model, it will need to receive input for its
state update from the micro-model, which it does by calling
:meth:`libmuscle.Instance.receive`. This receive is a bit special in that we
are passing a default message. The default message is returned if this port is
not connected. We are cleverly passing the message containing our current
state, so that if this port is not connected, the model continues from its
current state.  Since MUSCLE 3 will simply ignore a send command on a
disconnected port, this makes it possible to run the diffusion model without a
micro-model attached.

Of course, a sensible default value will not be available in all cases, but if
there is one, using it like this is a good idea.

Next, we check that we didn't receive a message from the future. This can happen
if the micro-model runs for longer than our macro-model timestep. In this case,
the number of steps is fixed, so that this warning will never be emitted.
However, if the micro-model runs until it detects convergence, then it can
happen that it runs for longer than the timestep of the macro-model, and that
would indicate that there is no timescale overlap anymore. In that case, the
result could be wrong, and a warning is appropriate.

The S operator here calls the ``laplacian()`` function. There is no requirement
for a submodel to be a single function, you can split it up, call library
functions, and so on. There has to be a top-level function however if you want
to run more than one submodel in a single Python program. Also, you cannot share
any data with other components, other than by sending and receiving messages. In
particular, you can't use global variables to communicate between models. This
is intentional, because it doesn't work if you're running as separate programs
on different computers.


Connecting it all together
--------------------------

With both models defined, we now need to instruct MUSCLE 3 on how to connect
them together. We do this by creating an object of type
``ymmsl.Configuration``, which contains all the information needed to run the
simulation. It often helps to draw a diagram first:

.. figure:: reaction_diffusion.png
  :scale: 40 %
  :align: center

  gMMSL diagram of the reaction-diffusion model.


This is a gMMSL diagram of the reaction-diffusion model. It shows that there are
two compute elements named ``macro`` and ``micro``. A conduit connects port
``state_out`` on ``macro`` to ``state_in`` on ``micro``. The symbols at the ends
of the conduit show the operators that the ports belong to, O_I for
``macro.state_out`` and F_INIT for ``micro.state_in``. Another conduit connects
port ``micro.final_state`` (O_F) to ``macro.state_in`` (S).

Note that there's a mnemonic here: Operators O_I and S, which are within the
state update loop, have a circular symbol, while F_INIT and O_F use a diamond
shape. Also, filled symbols designate ports on which messages are sent, while
open symbols designate receiving ports. We can therefore see that for each state
update, ``macro`` will send on ``state_out``, after which ``micro`` will do a
full run and send its final result as input for the next state update of
``macro``.

Since diagrams aren't valid Python, we need an alternative way of describing
this model in our code. For this, we use the ``ymmsl`` library to create a set
of objects that form a description.

.. code-block:: python

    elements = [
            ComputeElement('macro', 'diffusion'),
            ComputeElement('micro', 'reaction')]


First, we describe the two compute elements in this model. Compute elements can
be submodels, or helper components that convert data, control the simulation, or
otherwise implement required non-model functionality. In this simple example, we
only have two submodels: one named ``macro`` and one named ``micro``. Macro is
implemented by an implementation named ``diffusion``, while micro is implemented
by an implementation named ``reaction``.

The name of a compute element is used by MUSCLE as an address for communication
between the models. The implementation name is intended for use by a launcher,
which would start the corresponding program to create an instance of a compute
element. It is these instances that form the actual running simulation.

.. code-block:: python

    conduits = [
            Conduit('macro.state_out', 'micro.initial_state'),
            Conduit('micro.final_state', 'macro.state_in')]

    model = Model('reaction_diffusion', elements, conduits)


Next, we need to connect the compute elements together. This is done by
conduits, which have a sender and a receiver. Here, we connect sending port
``state_out`` on compute element ``macro`` to receiving port ``initial_state``
on compute element ``micro``. Note that these ports are actually defined in the
implementations, and not in this configuration file, and they are referred to
here.

The compute elements and the conduits together form a ``Model``, which has a
name and those two sets of components.

.. code-block:: python

    settings = Settings(OrderedDict([
                ('micro.t_max', 2.469136e-6),
                ('micro.dt', 2.469136e-8),
                ('macro.t_max', 1.234568e-4),
                ('macro.dt', 2.469136e-6),
                ('x_max', 1.01),
                ('dx', 0.01),
                ('k', -4.05e4),     # reaction parameter
                ('d', 4.05e-2)      # diffusion parameter
                ]))

    configuration = Configuration(model, settings)


Finally, we define the settings for our simulation. We are using an
``OrderedDict`` instead of a normal (unordered) Python dictionary because having
these in a logical order is really really useful if you're trying to edit them
and quickly find things. For complex models, you'll have many settings, and
having them ordered allows you to group them logically. Of course, the order in
this source code will not change, but if you save this to YAML, you want to
preserve the order, and for that OrderedDict is required. (Unofficially in
Python 3.6, and officially in Python 3.7, ``dict`` is now ordered, but for
compatibility with older versions, we'll use an OrderedDict here.)

Note that there are two duplicated names between the two models: ``t_max`` and
``dt``. With MUSCLE 3, you can create a global setting with that name to set it
to the same value everywhere (handy for settings that are used by multiple
compute elements), or you can prepend the name of the compute element to set the
value for a specific one. Specific settings go before generic ones, so if you
specify both ``micro.t_max`` and ``t_max``, then the ``micro`` compute element
will use ``micro.t_max`` and all others will use ``t_max``.

The model and the settings are combined into a Configuration, which contains
everything needed to run the simulation. A Configuration object is also the
Python-side equivalent to a yMMSL YAML file.


Launching the simulation
------------------------

Launching a simulation is strictly speaking outside of the scope of MUSCLE 3,
which primarily does coordination (helping instances find each other) and
communication (sending messages between them). However, for testing,
experimentation, learning, and small scale production use, having some means of
running a whole simulation from a single Python file is very nice. So MUSCLE 3
has a small facility for this in the form of the
:func:`libmuscle.run_simulation` function:

.. code-block:: python

  implementations = {'diffusion': diffusion, 'reaction': reaction}
  run_simulation(configuration, implementations)


Here, we make a dictionary that maps implementation names to the corresponding
Python functions. We then pass the configuration and the implementations to
:func:`libmuscle.run_simulation`, which will start the muscle_manager and the
implementations, and then wait for the simulation to finish.

Note that this will actually fork off a separate process for the manager and for
each implementation, so that this is a real distributed simulation, albeit on a
single machine. That makes this mode of operation a more realistic test case
for a real distributed run on an HPC machine, smoothing the transition to larger
compute resources.


Log output
----------

If you run the script, e.g. using

.. code-block:: bash

  (venv) python$ python3 reaction_diffusion.py

it will pop up a plot showing the state of the simulated system over time. If
you are on a machine without graphics support, then you will get an error
message if you run the above, saying something like ``couldn't connect to
display``. In that case, try the below command to disable graphical output:

.. code-block:: bash

  (venv) python$ DONTPLOT=1 python3 reaction_diffusion.py

You will also find three log files in this directory: ``muscle3_manager.log``,
``muscle3.macro.log`` and ``muscle3.micro.log``. These contain log output for
the manager and the submodel instances respectively. You can log messages in the
usual Python way in your models, and MUSCLE 3 will automatically take care of
writing them to the log file. Any messages at level ``WARNING`` or higher will
be sent to the manager log as well. This helps give an overview of what went
wrong in a single place in case of errors.
