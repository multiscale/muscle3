MUSCLE and MPI
==============

MPI, the Message Passing Interface, is the most widely used communications
middleware for High-Performance Computing. It's very low-level, but also usually
very well optimised, and perhaps more importantly, the standard. Many existing
HPC applications use MPI for communication, either directly or through a
library.

Chances are, therefore, that you will run into a submodel that uses MPI and that
you want to connect to MUSCLE 3. MUSCLE 3 supports this (only in C++ for now),
but as always with MPI, some extra care needs to be taken because things run in
parallel.

MPI follows the Single-Program Multiple Data paradigm, which means that there
are many copies of your program running simultaneously doing the same thing,
except that some of the data they're processing are different for each copy, and
every once in a while they communicate.

The MUSCLE parts of the simulation follow this: each process makes an Instance,
each process runs through the reuse loop, and each process calls the send and
receive functions at the same time. Two exceptions are that configuring ports
may only be done in the root process, and getting settings can be done anytime
and anywhere.

This section shows how to use MUSCLE 3 with MPI from C++, based on the same
reaction-diffusion model given in the C++ section, but now with a reaction
model that uses MPI. It will help if you've read the Python tutorial an the C++
section first, and you should have some experience with MPI.

`The source code for the example in this section is here
<https://github.com/multiscale/muscle3/tree/master/docs/source/examples/cpp>`_.
You can also go to ``docs/source/examples/cpp`` in the source directory (that's
easiest, and has some handy scripts and a Makefile), or copy-paste the code from
here.

Building and running the example
--------------------------------

If you've just built and installed the C++ version of libmuscle, then you're all
set to build the examples. Go into the ``docs/source/examples/cpp`` subdirectory
of the source directory, and type ``MUSCLE3_HOME=<PREFIX> MUSCLE_ENABLE_MPI=1
make`` and the examples will be compiled and linked against your new libmuscle.
In order to run them, you'll need the Python version of MUSCLE 3 installed,
because you need the MUSCLE Manager. The following (or something similar, if you
used different directories) should work:

.. code-block:: bash

  ~/muscle3_source$ cd docs/source/examples/cpp
  ~/muscle3_source/docs/source/examples/cpp$ MUSCLE3_HOME=~/muscle3 MUSCLE_ENABLE_MPI=1 make
  ~/muscle3_source/docs/source/examples/cpp$ . ~/muscle3_venv/bin/activate
  (muscle3_venv)~/muscle3_source/docs/source/examples/cpp$ MUSCLE3_HOME=~/muscle3 ./reaction_diffusion_mpi.sh


Note that this example is compiled with slightly different options compared to
the non-MPI C++ examples, and you should use those as well when compiling your
own MPI-based submodels. See the Installing section for details.


MPI Reaction model
------------------

Here is the C++-and-MPI version of the reaction model:

.. literalinclude:: examples/cpp/reaction_mpi.cpp
  :caption: ``docs/source/examples/cpp/reaction_mpi.cpp``
  :language: cpp


We'll go through it top to bottom, one piece at a time, focusing on the
differences with the plain C++ version.

Headers
```````

.. code-block:: cpp

    #include <mpi.h>

    #include <libmuscle/libmuscle.hpp>
    #include <ymmsl/ymmsl.hpp>


In order to use MPI, we need to include the MPI header. The headers for
libmuscle are unchanged. Remember that we're compiling with
``MUSCLE_ENABLE_MPI`` defined however, and this changes the API slightly as
shown below.


.. code-block:: cpp

    void reaction(int argc, char * argv[]) {
        const int root_rank = 0;
        int rank, num_ranks;
        MPI_Comm_rank(MPI_COMM_WORLD, &rank);
        MPI_Comm_size(MPI_COMM_WORLD, &num_ranks);


In MPI, all parallel processes are equal, but from time to time something must
be done from, to, or in only one of the processes, and so one process needs to
be declared special. This is called the root process, and it's usually the one
with rank zero. That's what we do here as well, and then we ask MPI for the rank
of the current process, and the total number of processes.

Creating an Instance
````````````````````

.. code-block:: cpp

    Instance instance(argc, argv, {
            {Operator::F_INIT, {"initial_state"}},  // list of double
            {Operator::O_F, {"final_state"}}},      // list of double
            MPI_COMM_WORLD, root_rank);


When MUSCLE 3 is used in MPI mode (with MUSCLE_ENABLE_MPI defined), the Instance
constructor takes two extra arguments: an MPI communicator, and the rank of the
root process. These default to MPI_COMM_WORLD and 0, respectively. MUSCLE 3 will
create a copy of the given communicator for internal use; the one you pass must
contain all processes in your submodel. MUSCLE 3 will do all communication with
other submodels from the process with the given root rank, and that process is
special when sending and receiving as described below.

Reuse loop and settings
```````````````````````

.. code-block:: cpp

    while (instance.reuse_instance()) {
        // F_INIT
        double t_max = instance.get_setting_as<double>("t_max");
        double dt = instance.get_setting_as<double>("dt");
        double k = instance.get_setting_as<double>("k");


This part is unchanged from the C++ version. This means that all processes enter
the reuse loop together. With MPI enabled, ``reuse_instance()`` is effectively a
collective operation, so it must be called in all processes simultaneously.

Settings may be obtained at any point and in any MPI process. Getting a setting
value does not require any MPI activity, so it can be done in any way you like
as long as it's within the reuse loop.

Distributed state
`````````````````

.. code-block:: cpp

    std::vector<double> U, U_all;
    int U_size;
    double t_cur, t_end;


The state of the reaction model is a vector of doubles. In this MPI version,
we'll be dividing that state among the processes, so that they can each process
a part of it. The ``U`` variable exists in each process and contains its piece
of the total state. ``U_all`` contains the complete state in the root process,
and it's empty in the rest of the processes. ``U_size`` is the size of ``U``,
and then we have ``t_cur`` and ``t_end`` in all processes, containing
respectively the current simulation time, and the time at which to end the
current run.

Receiving messages
``````````````````

Next, it's time time to receive the initial state:

.. code-block:: cpp

    auto msg = instance.receive("initial_state");


The ``receive()`` function is another collective operation, so it must be called
in all processes. All processes will block until a message is received. The
message will be returned in the root process (as designated when creating the
Instance), in all other processes, an empty dummy message is returned.

This may seem a bit odd (why not just receive only in the root process, or
return the received message in all processes), but it has a good reason. When
MPI needs to wait for something, it goes into a loop that continuously checks
whether the event has occurred (a spinloop). This keeps the CPU core it's
running on fully loaded. If you received only in the root process, and then
used a broadcast operation to distribute data, the root process would block
(without using CPU) on the network receive call until the other model was done,
while all other processes would spin frantically, keeping almost all your cores
occupied.

Since macro-micro models alternate execution, it's often nice if you can put
them on the same cores, but that only works if the waiting model doesn't
load them when it's not running. MUSCLE solves this problem using a TCP-based
barrier. You call ``receive()`` in all processes, and they will all block on a
network receive call, without using CPU, until a message is received and they
can continue.

The message is then sent only to the root, because MUSCLE does not know whether
it needs to be broadcast to all processes, or distributed somehow. You'll have
to do that part yourself.


.. code-block:: cpp

    if (rank == root_rank) {
        DataConstRef data(msg.data());
        U_all.resize(data.size());
        for (int i = 0; i < data.size(); ++i)
            U_all[i] = data[i].as<double>();

        t_cur = msg.timestamp();
        t_end = t_cur + t_max;

        U_size = U_all.size() / num_ranks;
        if (U_size * num_ranks != U_all.size()) {
            instance.error_shutdown("State does not divide evenly");
            throw std::runtime_error("State does not divide evenly");
        }
    }


Here, we start in the root process only by unpacking the received list into
``U_all``, and by setting the current and final times. We also calculate the
size of the per-process portion of the state, and check that it divides evenly.
If it doesn't, we tell MUSCLE that we've encountered an error (you can do this
either from the root process, or from all processes simultaneously), and raise
an exception. This example comples configured with a 100-cell long grid and two
MPI processes, so it'll work well.

Next, we distribute the received information among the processes:

.. code-block:: cpp

    MPI_Bcast(&U_size, 1, MPI_INT, root_rank, MPI_COMM_WORLD);
    U.resize(U_size);
    MPI_Scatter(U_all.data(), U_size, MPI_DOUBLE,
                U.data(), U_size, MPI_DOUBLE,
                root_rank, MPI_COMM_WORLD);

    MPI_Bcast(&t_cur, 1, MPI_DOUBLE, root_rank, MPI_COMM_WORLD);
    MPI_Bcast(&t_end, 1, MPI_DOUBLE, root_rank, MPI_COMM_WORLD);


This is fairly standard MPI code. First, we broadcast the size of the
per-process state. This is necessary, because it's derived from the received
message, and we only received it in the root process. Next, we make some space
in ``U`` for the new state information, and then we scatter ``U_all`` to the
``U`` vectors in the processes. The current time and end time are also derived
from the received message, so they need to be broadcast as well.

Next is the state update loop, which is completely unchanged. Each process
processes its part of the state, and since the reaction in a grid cell is not
affected by anything outside of that grid cell, we don't need to do any
communication. We could of course if this were e.g. the diffusion model, and we
needed to send data to the neighbours. That's not MUSCLE-related though, so we
refer to an MPI tutorial for more information on how to do that.

Finally, once we're done iterating, we need to send out the final state:

.. code-block:: cpp

    // O_F
    MPI_Gather(U.data(), U_size, MPI_DOUBLE,
               U_all.data(), U_size, MPI_DOUBLE,
               root_rank, MPI_COMM_WORLD);

    if (rank == 0) {
        auto result = Data::nils(U_all.size());
        for (int i = 0; i < U_all.size(); ++i)
            result[i] = U_all[i];
        instance.send("final_state", Message(t_cur, result));
    }


The ``send()`` function can be called either from the root process only, or from
all processes. In the latter case, it will simply do something only in the root
process, and return immediately in all other processes. This sometimes gives
cleaner code though, which is why it's an option.

In this case, we're going to do the sending only in the root process. We first
use a gather operation in all processes to collect the data from the local ``U``
variables into the root's ``U_all``. Then, we convert it into a ``Data`` object
and send it as before, but only in the root process.


MPI requires initialisation and finalisation, which we do in the main function:

.. code-block:: cpp

    int main(int argc, char * argv[]) {
        MPI_Init(&argc, &argv);
        reaction(argc, argv);
        MPI_Finalize();
        return EXIT_SUCCESS;
    }


Note that ``MPI_Init()`` must have been called before a MUSCLE ``Instance`` is
created, since the ``Instance`` constructor will make MPI calls.

