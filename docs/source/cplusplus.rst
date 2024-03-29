MUSCLE and C++
==============

This section shows how to use MUSCLE3 from C++, based on the same
reaction-diffusion model as given in the Python-based distributed execution
tutorial. It will help to at least read that first.

`The source code for the examples in this section is here
<https://github.com/multiscale/muscle3/tree/master/docs/source/examples/cpp>`_.
You can also go to ``docs/source/examples/cpp`` in the source directory (that's
easiest, and has a handy Makefile), or copy-paste the code from here. If you are
cloning from GitHub, be sure to use the ``master`` branch, as ``develop`` may
have changes incompatible with the current release.

Building and running the examples
---------------------------------

If you've just built and installed the C++ version of libmuscle, then you're all
set to build the examples. To do that, go into the ``docs/source/examples``
subdirectory, make the new installation available, and then run Make:

.. code-block:: bash

  ~/muscle3_source$ cd docs/source/examples
  ~/muscle3_source/docs/source/examples$ . /path/to/muscle3/bin/muscle3.env
  ~/muscle3_source/docs/source/examples$ make cpp


We also need the Python version of MUSCLE3 installed, because the MUSCLE
Manager comes with that, and we need it to run the simulation. The above command
will create a Python virtual env with everything needed as well.

You can then run the examples in the same way as for python, but using a yMMSL
file that specifies the C++ implementation of one or both of the submodels:

.. code-block:: bash

  . python/build/venv/bin/activate
  muscle_manager --start-all rd_implementations.ymmsl rd_cpp.ymmsl rd_settings.ymmsl
  muscle_manager --start-all rd_implementations.ymmsl rd_python_cpp.ymmsl rd_settings.ymmsl


Note that activating the virtual environment is needed to make the
``muscle_manager`` command available.

Log output
----------

As for the Python model, the manager will make a run directory into which log
files and output are written. You can set ``muscle_remote_log_level`` and
``muscle_local_log_level`` for C++ models as you can for Python, but in C++ this
will only affect log messages generated by libmuscle, not anything written by
your model. Of course, you can read ``muscle_local_log_level`` or a custom
setting yourself in your F_INIT, and set your log library's level accordingly.

If the model code logs to standard output or standard error, then
the messages will end up in ``<rundir>/instances/<instance-id>/stdout.txt`` or
``stderr.txt``. If the model logs to a file in the working directory, then
you'll find it in ``<rundir>/instances/<instance-id>/workdir/``.

Describing C++ implementations
------------------------------

The only difference between this and the Python-only example is that the C++
implementations are used. These differ a bit from the Python versions:

.. code-block:: yaml

  reaction_cpp:
    env:
      +LD_LIBRARY_PATH: :<muscle3_prefix>/lib
    executable: <muscle3_src>/docs/source/examples/cpp/build/reaction

  diffusion_cpp:
    env:
      +LD_LIBRARY_PATH: :<muscle3_prefix>/lib
    executable: <muscle3_src>/docs/source/examples/cpp/build/diffusion


Note that ``<muscle3_prefix>`` and ``<muscle3_src>`` are not in there literally,
they are just a placeholder here. When you ran Make, it created this file and
substituted in your local paths. For a real model, you should put in the
absolute path to the installation yourself.

Since we have compiled binaries here which can be executed directly, we don't
need to run Python, we can just specify their location directly. We do need to
make sure that the MUSCLE3 libraries, which the executables are linked against,
can be found. We do that by setting the ``LD_LIBRARY_PATH`` to point to their
location. Since ``LD_LIBRARY_PATH`` is a list, and overwriting it may break
something, we append to it by adding a ``+`` in front of the variable name. Note
the initial colon in the value: this is the separator used in
``LD_LIBRARY_PATH``, and MUSCLE3 will not add it automatically, so it needs to
be there.


Reaction-diffusion in C++
-------------------------

As you can see, running simulations isn't much different regardless of which
languages the components are written in. Connecting models to ``libmuscle`` is
also quite similar, although of course there are some differences because the
languages are not the same. Here's the basic reaction model, without MUSCLE
support, in C++:

Reaction model
``````````````

.. code-block:: cpp
    :caption: A simple reaction model on a 1D grid, in C++.

    #include <cmath>
    #include <vector>

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
    #include <vector>

    #include <libmuscle/libmuscle.hpp>
    #include <ymmsl/ymmsl.hpp>


    using libmuscle::Data;
    using libmuscle::DataConstRef;
    using libmuscle::Instance;
    using libmuscle::Message;
    using ymmsl::Operator;


Here we include some headers, and import the classes we'll need into our root
namespace. ``cstdlib`` is there for the ``EXIT_SUCCESS`` constant at the bottom,
and not needed for MUSCLE. ``vector`` is included because we use ``std::vector``
in the model code. The C++ API mirrors the Python API where applicable, so it
has ``libmuscle`` and ``ymmsl`` like in Python. However, in C++ there is no
separate yMMSL library. Instead the classes needed are included with libmuscle.
This means that there is no support for manipulating yMMSL files from C++.

There are two classes here that don't have a Python equivalent, ``Data`` and
``DataConstRef``. More on that when we use them below.

Creating an Instance
````````````````````

.. code-block:: cpp

    void reaction(int argc, char * argv[]) {
        Instance instance(argc, argv, {
                {Operator::F_INIT, {"initial_state"}},  // array of double
                {Operator::O_F, {"final_state"}}});     // array of double


The ``reaction`` function has changed a bit: it now takes the command line
parameters as arguments. Like the Python version, the C++ libmuscle takes some
information from the command line, but in C++ this needs to be passed
explicitly to the ``Instance`` object. Otherwise, constructing the ``Instance``
is the same: it is passed a dictionary mapping operators to a list of port
descriptions (see ``PortsDescription`` in the API documentation). Like in the
Python version, we'll be passing a 1D array of doubles between the models.

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
    auto data_ptr = msg.data().elements<double>();
    std::vector<double> U(data_ptr, data_ptr + msg.data().size());


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
we've been sent a 1D grid of doubles. If there is no grid, an exception will
be thrown and our program will halt. That's okay, because it means that there's
something wrong somewhere that we need to fix. MUSCLE is designed to let you get
away with being a bit sloppy as long as things actually go right, but it will
check for problems and let you know if something goes wrong.

A grid in MUSCLE3 is an n-dimensional array of numbers or booleans. It has a
shape (size in each dimension), a size (total number of elements), a storage
order which says in which order the elements are arranged in memory, and
optionally names for the indexes.

Here, we expect a 1D grid of doubles, which is just a vector of numbers. Storage
order is irrelevant then. We'll use the standard C++ ``std::vector`` class to
contain our state. It has a constructor that takes a pointer to an array of
objects of the appropriate type and the number of them, and copies those objects
into itself. We use the :cpp:func:`DataConstRef::elements` to get a pointer to
the elements, and :cpp:func:`DataConstRef::size` to get the number of elements,
and that's all we need to create our state vector ``U``.

Note that MUSCLE3 will in this case check that we have the right type of
elements (doubles), but it cannot know and therefore will not check that we're
expecting a 1D grid. We could check that by hand by checking the length of
``msg.data().shape()`` to see if it's 1. See the diffusion model below for an
example.


.. code-block:: cpp

        double t_cur = msg.timestamp();
        while (t_cur + dt < msg.timestamp() + t_max) {
            // O_I

            // S
            for (double & u : U)
                u += k * u * dt;
            t_cur += dt;
        }

The main loop of the model is almost unchanged, we just get the starting time
from the received message's timestamp so as to synchronise with the overall
simulation time correctly, and the stopping time is adjusted accordingly as
well.

Sending messages and Data
`````````````````````````

.. code-block:: cpp

        // O_F
        auto result = Data::grid(U.data(), {U.size()}, {"x"});
        instance.send("final_state", Message(t_cur, result));


Having computed our final state, we will send it to the outside world on the
``final_state`` port. In this case, we need to send a 1D grid of doubles, which
we first need to wrap up into a ``Data`` object. A ``Data`` object works just
like a ``DataConstRef``, except that it isn't constant, and can thus be
modified. (It is in fact a reference, like ``DataConstRef``, despite the name,
and it has automatic memory management as well.)

Here, we create a ``Data`` containing a grid. We pass it a pointer to the
numbers in ``U``, and the shape of our grid, which is a 1-element array because
the grid is 1-dimensional. The third argument contains the names of the indexes,
which helps to avoid confusion over which index is x and which is y (or
row/column, or latitude/longitude, or... you get the idea). You are not
required to add these (and MUSCLE3 doesn't use them), but you or someone else
using your code will be very grateful you did at some point in the future.

With our data item constructed, we can send a ``Message`` to the ``final_state``
port containing the current timestamp and the data. Note that there are
different ways of creating a ``Message``, depending on whether you set the next
timestamp, or are using an explicit settings overlay. See the API documentation
for details.

``Data`` is quite versatile, and makes it easier to send data of various
types between submodels. Here are some other examples of creating ``Data``
objects containing different kinds of data:

.. code-block:: cpp

    // create a Data containing a nil value (None in Python)
    Data d1;

    // strings, booleans
    Data d2("String data");
    Data d3(true);

    // various kinds of numbers
    Data d4(0);         // int
    Data d5(10u);       // unsigned int
    Data d6(100l);      // long int
    Data d7(3.141592f); // float
    Data d8(1.4142);    // double

    // constant list
    auto d9 = Data::list("String data", true, 0, 10u, 1.4142);

    // dictionary
    auto d10 = Data::dict(
            "x", x,
            "y", y,
            "note", "Keys must be strings",
            "why_not", Data::list(10, 3.141592, "that's fine"),
            "existing_object", d4
            );

    // grid
    // +-----------------+
    // | 1.0 | 2.0 | 3.0 |
    // +-----------------+
    // | 4.0 | 5.0 | 6.0 |
    // +-----------------+
    std::vector<double> array = {1.0, 2.0, 3.0, 4.0, 5.0, 6.0};
    auto d11 = Data::grid(array.data(), {2, 3}, {"row", "col"});

    // byte array
    std::vector<char> bytes;
    auto d12 = Data::byte_array(bytes.data(), bytes.size());

    // simple types are created automatically when making a Message
    instance.send("output_port", Message(t_cur, 1.0));

    std::string text("A text message");
    instance.send("output_port", Message(t_cur, text));

    // but you have to name dicts, lists, grids and byte arrays
    instance.send("output_port", Message(t_cur, Data::list("a", 10)));


For completeness and as an easy-to-use reference, here's how to unpack those
types:

.. code-block:: cpp

    // check whether a DataConstRef contains a nil value (None in Python)
    if (d1.is_nil()) ...

    // strings, booleans
    std::string s = d2.as<std::string>();
    bool b = d3.as<bool>();

    // various kinds of numbers
    int i = d4.as<int>();
    unsigned int u = d5.as<unsigned int>();
    long int l = d6.as<long int>();
    float f = d7.as<float>();
    double d = d8.as<double>();

    // accessing a heterogeneous list
    if (!d9.is_a_list())
        std::cerr << "Expected a list" << std::endl;

    for (std::size_t j = 0u; j < d9.size(); ++j) {
        if (d9[j].is_a<std::string>())
            std::string s = d9[j].as<std::string>();
        else if (d9[j].is_a<bool>())
            bool b = d9[j].as<bool>();
        else if (d9[j].is_a<int>())
            int i = d[9].as<int>();
        else if (d9[j].is_a<unsigned int>())
            unsigned int u = d9[j].as<unsigned int>();
        else if (d9[j].is_a<double>())
            double d = d9[j].as<double>();
    }

    // accessing a dictionary value
    if (!d10.is_a_dict())
        std::cerr << "Expected a dict" << std::endl;

    std::string s = d10["note"].as<std::string>();

    // iterating through a dictionary
    for (std::size_t j = 0u; j < d10.size(); ++j) {
        std::string k = d10.key(j);
        DataConstRef v = d10.value(j);
        // check what's in it and process, see list above
    }

    // grid
    if (d11.is_a_grid_of<double>()) {
        std::vector<std::size_t> shape = d11.shape();
        std::size_t num_dims = shape.size();
        if (num_dims == 2u) {
            double const * data_ptr = d11.elements<double>();
            for (std::size_t i = 0u; i < shape[0]; ++i) {
                std::vector<double> v(
                        data_ptr + shape[1] * i,
                        data_ptr + shape[1] * (i + 1));
                std::cout << d11.indexes()[0] << " " << i << ": ";
                // print v
            }
        }
    }

    // byte array
    if (d12.is_a_byte_array()) {
        char * data_ptr = d12.as_byte_array()
        std::vector<char> data(data_ptr, data_ptr + d12.size());
    }


As you can see, sending complex data types with MUSCLE is almost as easy in C++
as it is in Python, while receiving is almost as easy (except for grids, because
C++ doesn't have a built-in multidimensional array type).

There is however a bit of a cost to this ease-of-use in the form of extra memory
usage. If you're sending large amounts of data, then it is best to use as many
grids as you can, as those are much more efficient than dictionaries and lists.
In particular, a set of objects (agents for example) is much more efficiently
sent as a dictionary-of-grids (with one 1D-grid for each attribute) than as a
list of dictionaries. (The latter will work up to a million objects or so, but
it will be slower.)

Back to the reaction model. We still have one bit left, a simple ``main()``
function that runs the model, passing the command line arguments:

.. code-block:: cpp

    int main(int argc, char * argv[]) {
        reaction(argc, argv);
        return EXIT_SUCCESS;
    }


Diffusion model
```````````````

If you've studied the above carefully, and have seen the Python version of the
diffusion model, then you should now be able to understand the C++ diffusion
model below:

.. literalinclude:: examples/cpp/diffusion.cpp
  :caption: ``docs/source/examples/cpp/diffusion.cpp``
  :language: cpp

