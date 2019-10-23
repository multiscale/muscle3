MUSCLE and C++
==============

This section shows how to use MUSCLE 3 from C++, based on the same
reaction-diffusion model given in the Python tutorial.
`The source code for the examples in this section is here
<https://github.com/multiscale/muscle3/tree/master/docs/source/examples/cpp>`_.
You can also go to ``docs/source/examples/cpp`` in the source directory (that's
easiest, and has some handy scripts and a Makefile), or copy-paste the code from
here.

Building and running the examples
---------------------------------

If you've just built and installed the C++ version of libmuscle, then you're all
set to build the examples. Go into the ``docs/source/examples/cpp`` subdirectory
of the source directory, and type ``MUSCLE3_HOME=<PREFIX> make`` and the
examples will be compiled and linked against your new libmuscle. In order to run
them, you'll need the Python version of MUSCLE 3 installed, because you need the
MUSCLE Manager. The following (or something similar, if you used different
directories) should work:

.. code-block:: bash

  ~/muscle3_source$ cd docs/source/examples/cpp
  ~/muscle3_source/docs/source/examples/cpp$ MUSCLE3_HOME=~/muscle3 make
  ~/muscle3_source/docs/source/examples/cpp$ . ~/muscle3_venv/bin/activate
  (muscle3_venv)~/muscle3_source/docs/source/examples/cpp$ MUSCLE3_HOME=~/muscle3 ./reaction_diffusion.sh


Log output
----------

When you run a MUSCLE 3 simulation, the manager will produce a
``muscle3_manager.log`` file with log messages collected from the submodels. You
can set the log level for C++ instances by adding a ``muscle_remote_log_level``
setting to the yMMSL file, with a value of ``DEBUG``, ``INFO``, ``WARNING``,
``ERROR`` or ``CRITICAL``. The default is ``WARNING``, which is pretty quiet,
``INFO`` will give more output, but also slow things down a bit because those
messages have to be sent to the manager.

The running script will redirect standard out and standard error for each
instance to a file, so you can find any output produced by the submodels there.


Reaction-diffusion in C++
-------------------------

This page assumes that you've at least read the Python tutorial; we'll do the
same thing again but now in C++.

The C++ version of libmuscle doesn't support running multiple compute elements
in a single program, so we're going to do the distributed version of the
reaction-diffusion example in C++. Here's the basic reaction model, without
MUSCLE support, in C++:

Reaction model
``````````````

.. code-block:: cpp
    :caption: A simple reaction model on a 1D grid, in C++.

    void reaction() {
        // F_INIT
        double t_max = 2.469136e-07;
        double dt = 2.469136e-08;
        double x_max = 1.0;
        double dx = 0.01;
        double k = -40500.0;

        std::vector<double> U(lrint(x_max / dx));
        U[25] = 2.0;
        U[50] = 2.0;
        U[75] = 2.0;

        double t_cur = 0.0;
        while (t_cur + dt < t_max) {
            // O_I

            // S
            for (double & u : U)
                u += k * u * dt;
            t_cur += dt;
        }

        // O_F
    }


This is one of the simplest possible computational models: we set some
parameters, create a state variable ``U``, initialise the state, and then update
the state in a loop until we reach the final simulation time.

The MUSCLE version in C++ looks quite similar to the Python version:

.. literalinclude:: examples/cpp/reaction.cpp
  :caption: ``docs/source/examples/cpp/reaction.cpp``
  :language: cpp


We'll go through it top to bottom, one piece at a time.

Headers
```````

.. code-block:: cpp

    #include <cstdlib>

    #include <libmuscle/libmuscle.hpp>
    #include <ymmsl/ymmsl.hpp>


    using libmuscle::Data;
    using libmuscle::DataConstRef;
    using libmuscle::Instance;
    using libmuscle::Message;
    using ymmsl::Operator;


Here we include some headers, and import the classes we'll need into our root
namespace. ``cstdlib`` is there for the ``EXIT_SUCCESS`` constant at the bottom,
and not needed for MUSCLE. The C++ API mirrors the Python API where applicable,
so it has ``libmuscle`` and ``ymmsl`` like in Python. However, in C++ there is
no separate yMMSL library. Instead the classes needed are included with
libmuscle. This means that there is no support for manipulating yMMSL files from
C++.

There are two classes here that don't have a Python equivalent, ``Data`` and
``DataConstRef``. More on that when we use them below.

Creating an Instance
````````````````````

.. code-block:: cpp

    void reaction(int argc, char * argv[]) {
        Instance instance(argc, argv, {
                {Operator::F_INIT, {"initial_state"}},  // list of double
                {Operator::O_F, {"final_state"}}});     // list of double


The ``reaction`` function has changed a bit: it now takes the command line
parameters as arguments. Like the Python version, the C++ libmuscle takes some
information from the command line, but in C++ this needs to be passed
explicitly to the ``Instance`` object. Otherwise, constructing the ``Instance``
is the same: it is passed a dictionary mapping operators to a list of port
descriptions (see ``PortsDescription`` in the API documentation). Like in the
Python version, we'll be passing a list of doubles between the models.

Reuse loop and settings
```````````````````````

.. code-block:: cpp

    while (instance.reuse_instance()) {
        // F_INIT
        double t_max = instance.get_setting_as<double>("t_max");
        double dt = instance.get_setting_as<double>("dt");
        double k = instance.get_setting_as<double>("k");


As in Python, we have a reuse loop, and except for the syntax differences
between the languages, the code is exactly the same. Getting settings works as
shown; with C++ being a statically typed language, we need to specify the type
we're expecting. As in Python, if the actual type is different, an exception
will be thrown.

Supported types for settings are ``std::string``, ``bool``, ``int64_t``,
``double``, ``std::vector<double>`` and ``std::vector<std::vector<double>>``.
There is also a ``get_setting()`` member function, which returns a
``SettingValue`` object. A ``SettingValue`` can contain a value of any of the
above types, and it can be queried to see what is in it.

Receiving messages and DataConstRef
```````````````````````````````````

Instead of initialising our state from a constant, we're going to receive a
message on our ``F_INIT`` port with the initial state:

.. code-block:: cpp

    auto msg = instance.receive("initial_state");
    DataConstRef data = msg.data();
    std::vector<double> U(data.size());
    for (int i = 0; i < data.size(); ++i)
        U[i] = data[i].as<double>();


Calling the ``receive`` method on an instance yields an object of type
``libmuscle::Message``. In Python, this is a very simple class with several
public members. In C++, these members are wrapped in accessors, so while the API
is conceptually the same, the syntax is slightly different. Here, we're
interested in the data that was sent to us, so we use ``msg.data()`` to access
it.

This returns an object of type ``libmuscle::DataConstRef``. This type is new in
the C++ version of the library, and it exists because C++ is a statically typed
language, while in a MUSCLE simulation the type of data that is sent in a
message can vary from message to message. So we need some kind of class that can
contain data of many different types, and that's what ``Data`` and
``DataConstRef`` are for. Here are some key properties of ``DataConstRef``:

- ``DataConstRef`` is like a reference in that it points to an actual data
  object of some type. If you copy it into a second ``DataConstRef``, both
  ``DataConstRef`` variables will point to the same object. Like in Python or in
  Java.

- ``DataConstRef`` is constant, you cannot change the data through a
  ``DataConstRef``.

- Memory management for ``DataConstRef`` is automatic, there's no need to
  ``delete`` or ``free`` anything. Objects will be deleted from memory when all
  ``Data`` and ``DataConstRef`` objects pointing to them are gone. Like in
  Python or in Java.

- ''DataConstRef'' variables can be inspected to see what type of data they
  contain, and the data can be extracted into a C++ variable of the correct
  type.

In the code here, we don't bother with a check. Instead, we blindly assume that
we've been sent a list of doubles. If that's not the case, an exception will be
thrown and our program will halt. That's okay, because it means that there's
something wrong somewhere that we need to fix. MUSCLE is designed to let you get
away with being a bit sloppy as long as things actually go right, but it will
check for problems and let you know if something goes wrong.

If a ``DataConstRef`` contains a list of some kind, then its ``size()`` member
function can be used to determine the length of that list. We use that to create
a ``std::vector`` of the correct length, and then extract each item in the
received list into the vector. Note that items in a list can be accessed through
``data[i]``, and that each item is itself a ``DataConstRef``, now (hopefully)
containing a ``double`` value that we can extract using ``as()``.


.. code-block:: cpp

        double t_cur = msg.timestamp();
        while (t_cur + dt < t_max) {
            // O_I

            // S
            for (double & u : U)
                u += k * u * dt;
            t_cur += dt;
        }

The main loop of the model is almost unchanged, we just get the starting time
from the received message's timestamp so as to synchronise with the overall
simulation time correctly.

Sending messages and Data
`````````````````````````

.. code-block:: cpp

        // O_F
        auto result = Data::nils(U.size());
        for (int i = 0; i < U.size(); ++i)
            result[i] = U[i];
        instance.send("final_state", Message(t_cur, result));


Having computed our final state, we will send it to the outside world on the
``final_state`` port. In this case, we need to send a list of doubles, which we
first need to wrap up into a ``Data`` object. A ``Data`` object works just like
a ``DataConstRef``, except that it isn't constant, and can thus be modified. (It
is in fact a reference, like ``DataConstRef``, despite the name, and it has
automatic memory management as well.)

Here, we start by creating a ``Data`` containing a list of `U.size()` nil (null,
None) values. This allocates enough space in the list for all of our doubles. We
can then simply use ``result[i]`` to assign our double values to each list item.
Note that there's no need to explicitly specify that this is a double, the
compiler knows and will do the right thing.

With our data item constructed, we can send a ``Message`` containing the current
timestamp and the data to the ``final_state`` port. Note that there are
different ways of creating a ``Message``, depending on whether you set the next
timestamp, or are using an explicit settings overlay. See the API documentation
for details.

.. code-block:: cpp

    int main(int argc, char * argv[]) {
        reaction(argc, argv);
        return EXIT_SUCCESS;
    }


We finish the example with a simple ``main()`` function that runs the model,
passing the command line arguments.

Diffusion model
```````````````

If you've studied the above carefully, and have seen the Python version of the
diffusion model, then you should now be able to understand the C++ diffusion
model below:

.. literalinclude:: examples/cpp/diffusion.cpp
  :caption: ``docs/source/examples/cpp/diffusion.cpp``
  :language: cpp


In the examples directory, you will find a handy script called
``reaction_diffusion.sh``, which runs the C++ reaction-diffusion model locally.
This script launches the MUSCLE Manager and an instance of each submodel, then
waits for the simulation to complete. At the top of this page there are
instructions on how to run the examples.

Also in this directory are C++ versions of a Monte Carlo sampler and a
round-robin load balancer, plus a script to launch this extended example. See
the `Uncertainty Quantification` section to learn what those are for.

