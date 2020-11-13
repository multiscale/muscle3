MUSCLE and Fortran
==================

This section shows how to use MUSCLE 3 from Fortran, based on the same
reaction-diffusion model given in the Python tutorial.
`The source code for the examples in this section is here
<https://github.com/multiscale/muscle3/tree/master/docs/source/examples/fortran>`_.
You can also go to ``docs/source/examples/fortran`` in the source directory
(that's easiest, and has some handy scripts and a Makefile), or copy-paste the
code from here.

Building and running the examples
---------------------------------

If you've just built and installed the C++ version of libmuscle (which includes
the Fortran bindings), then you're all set to build the examples. To do that, go
into the ``docs/source/examples`` subdirectory, and run Make:

.. code-block:: bash

  ~/muscle3_source$ cd docs/source/examples
  ~/muscle3_source/docs/source/examples$ MUSCLE3_HOME=~/muscle3 make fortran


We also need the Python version of MUSCLE 3 installed, because the MUSCLE
Manager comes with that, and we need it to run the simulation. To set that up,
do:

.. code-block:: bash

  ~/muscle3_source/docs/source/examples$ make python


You can then run the examples using the provided scripts in
``docs/source/examples``:

.. code-block:: bash

  ~/muscle3_source/docs/source/examples$ MUSCLE3_HOME=~/muscle3 ./reaction_diffusion_fortran.sh


Log output
----------

When you run a MUSCLE 3 simulation, the manager will produce a
``muscle3_manager.log`` file with log messages collected from the submodels. You
can set the log level for Fortran instances by adding a
``muscle_remote_log_level`` setting to the yMMSL file, with a value of
``DEBUG``, ``INFO``, ``WARNING``, ``ERROR`` or ``CRITICAL``. The default is
``WARNING``, which is pretty quiet, ``INFO`` will give more output, but also
slow things down a bit because those messages have to be sent to the manager.

The running script will redirect standard out and standard error for each
instance to a file, so you can find any output produced by the submodels there.


Reaction-diffusion in Fortran
-----------------------------

This page assumes that you've at least read the Python tutorial; we'll do the
same thing again but now in Fortran.

The Fortran version of libmuscle doesn't support running multiple compute
elements in a single program, so we're going to do the distributed version of
the reaction-diffusion example in Fortran. Here's the basic reaction model,
without MUSCLE support, in Fortran:

Reaction model
``````````````

.. code-block:: fortran
    :caption: A simple reaction model on a 1D grid, in Fortran.

    program reaction
        implicit none

        real (selected_real_kind(15)) :: t_cur, t_max, dt, x_max, dx, k
        integer :: i, U_size
        real (selected_real_kind(15)), dimension(:), allocatable :: U


        ! F_INIT
        t_max = 2.469136e-07
        dt = 2.469136e-08
        x_max = 1.0
        dx = 0.01
        k = -40500.0

        U_size = int(x_max / dx)
        allocate (U(U_size))
        U = 1e-20
        U(26) = 2.0
        U(51) = 2.0
        U(76) = 2.0

        t_cur = 0.0
        do while (t_cur + dt < t_max)
            ! O_I

            ! S
            U = k * U * dt
            t_cur = t_cur + dt
        end do

        ! O_F

        deallocate (U)

    end program reaction


This is one of the simplest possible computational models: we set some
parameters, create a state variable ``U``, initialise the state, and then update
the state in a loop until we reach the final simulation time.

The MUSCLE version in Fortran looks quite similar to the Python version:

.. literalinclude:: examples/fortran/reaction.f03
  :caption: ``docs/source/examples/fortran/reaction.f03``
  :language: fortran


We'll go through it top to bottom, one piece at a time.

Modules
```````

.. code-block:: fortran

    use ymmsl
    use libmuscle
    implicit none


Here we tell Fortran that we'll be using the ymmsl and libmuscle modules. These
mirror the corresponding Python packages. Like in C++, yMMSL support is limited
to what is needed to implement compute elements. Loading, manipulating and
saving yMMSL documents is better done in Python.


Variables
`````````

.. code-block:: fortran

    type(LIBMUSCLE_PortsDescription) :: ports
    type(LIBMUSCLE_Instance) :: instance

    type(LIBMUSCLE_Message) :: rmsg
    type(LIBMUSCLE_DataConstRef) :: rdata, item


    type(LIBMUSCLE_Message) :: smsg
    type(LIBMUSCLE_Data) :: sdata

    real (selected_real_kind(15)) :: t_cur, t_max, dt, k
    real (selected_real_kind(15)), dimension(:), allocatable :: U


Next, it's time to declare our variables. We have a few extra variables here
compared to the non-MUSCLE version. The :f:type:`LIBMUSCLE_PortsDescription` is
used to describe the ports we'll use to send and receive to MUSCLE 3. We need a
:f:type:`LIBMUSCLE_Instance` as the main interface to MUSCLE. We'll receive
messages into ``rmsg``, a :f:type:`LIBMUSCLE_Message` variable, and extract the
data from them into ``rdata`` and ``item``. Since received data cannot be
modified, this variable is of type :f:type:`LIBMUSCLE_DataConstRef`. For sending
messages we have ``smsg``, and we'll create a :f:type:`LIBMUSCLE_Data` object to
put our data into before sending. Note that the names are all prefixed with
``LIBMUSCLE``, to make sure that they don't collide with any other library you
may want to use.

Eagle-eyed readers will have noticed that ``dx`` and ``x_max`` are missing. That
is because we'll derive the size of the state vector of the model (``U``) from
the state we receive, rather than from the configuration.

Creating an Instance
````````````````````

.. code-block:: fortran

    ports = LIBMUSCLE_PortsDescription_create()
    call LIBMUSCLE_PortsDescription_add(ports, YMMSL_Operator_F_INIT, 'initial_state')
    call LIBMUSCLE_PortsDescription_add(ports, YMMSL_Operator_O_F, 'final_state')
    instance = LIBMUSCLE_Instance_create(ports)
    call LIBMUSCLE_PortsDescription_free(ports)


In order to talk to the rest of the MUSCLE simulation, we need a
:f:type:`LIBMUSCLE_Instance` object, and we need to pass a description of the
ports we'll use when we make that. So here, we first create a
:f:type:`LIBMUSCLE_PortsDescription`, and add some ports to the ``F_INIT`` and
``O_F`` operators. We can then create the Instance object, passing the ports.
Finally, we need to free the PortsDescription object. Since Fortran does not
have automatic memory management, you will have to be careful to always free any
object you create, or that is returned by a MUSCLE function, after you're done
using it. So we free the PortsDescription here, but we don't free the Instance,
since we need it in the following part of the code.


Reuse loop and settings
```````````````````````

.. code-block:: fortran

    do while (LIBMUSCLE_Instance_reuse_instance(instance))
        ! F_INIT
        t_max = LIBMUSCLE_Instance_get_setting_as_real8(instance, 't_max')
        dt = LIBMUSCLE_Instance_get_setting_as_real8(instance, 'dt')
        k = LIBMUSCLE_Instance_get_setting_as_real8(instance, 'k')


As in Python, we have a reuse loop, and except for the syntax differences
between the languages, the code is exactly the same. Getting settings works as
shown; with Fortran being a statically typed language, we need to specify the
type we're expecting by calling a different function. If the actual type is
different, an error will be printed and the program will be halted. It is
possible to detect and handle errors instead, see below for that.

Getting settings is done via the ``LIBMUSCLE_Instance_get_setting_as_<type>()``
functions. Supported types are ``character``, ``logical``, ``int8`` (a 64-bit
integer), ``real8`` (a 64-bit double precision real number), ``real8array`` (a
1D array of double precision reals) and ``real8array2`` (a 2D array of double
precision reals). See the :f:func:`API documentation
<LIBMUSCLE_Instance_get_setting_as_character>` for details.


Receiving messages and DataConstRef
```````````````````````````````````

Instead of initialising our state from a constant, we're going to receive a
message on our ``F_INIT`` port with the initial state:

.. code-block:: fortran

        rmsg = LIBMUSCLE_Instance_receive(instance, 'initial_state')
        rdata = LIBMUSCLE_Message_get_data(rmsg)
        allocate (U(LIBMUSCLE_DataConstRef_size(rdata)))
        call LIBMUSCLE_DataConstRef_elements(rdata, U)
        call LIBMUSCLE_DataConstRef_free(rdata)


Calling the :f:func:`LIBMUSCLE_Instance_receive` function with an instance and a
port name yields an object of type :f:type:`LIBMUSCLE_Message` containing the
received message. As always when using MUSCLE from Fortran, we have to remember
to free the returned Message object when we are done with it. That's not yet
the case though, because we still need to get the received data out. In Python,
Message is a very simple class with several public members. In Fortran, objects
are always accessed and manipulated through LIBMUSCLE functions, in this case
:f:func:`LIBMUSCLE_Message_get_data`, which we use to get a ``DataConstRef``
object. Again, since MUSCLE gave us an object, we have to remember to free it
when we're done.

First though, we'll use the data to initialise our state. We are going to assume
that we'll receive a 1D grid of numbers, just like in the equivalent examples in
the other supported languages. :f:func:`LIBMUSCLE_DataConstRef_size` will return
the size of the array that we received (or print an error and stop if we
received something else that doesn't have a size, see below for handling errors
differently). We use that to allocate the ``U`` array to the same size as the
received state, and then we copy the elements of the array into ``U`` using
:f:func:`LIBMUSCLE_DataConstRef_elements`. We can then free the ``rdata``
object, since we don't need it any longer. We'll hold on to the ``rmsg`` a bit
longer, since we'll need it later.

If all this freeing objects is starting to sound tedious, that's because it is,
and it's why more modern languages like Python and C++ do this for you.
Unfortunately, for Fortran, it has to be done manually.

Note that indices for the received array start at 1, as usual in Fortran. MUSCLE
3 follows the language in which you're using it and automatically translates, so
if this grid was sent from Python or C++, then received item 1 corresponds to
sent item 0.

If you have a DataConstRef object, then you can check which kind of value it
contains, e.g. using :f:func:`LIBMUSCLE_DataConstRef_is_a_grid_of_real8`. Here,
we don't bother with a check. Instead, we blindly assume that we've been sent a
1D grid of doubles. If that's not the case, an error will be printed and our
program will halt. That's okay, because it means that there's something wrong
somewhere that we need to fix. MUSCLE is designed to let you get away with being
a bit sloppy as long as things actually go right, but it will check for problems
and let you know if something goes wrong. If you want to make a submodel or
component that can handle different kinds of messages, then these inspection
functions will help you do so however.


.. code-block:: fortran

        t_cur = LIBMUSCLE_Message_timestamp(rmsg)
        t_max = LIBMUSCLE_Message_timestamp(rmsg) + t_max
        call LIBMUSCLE_Message_free(rmsg)

        do while (t_cur + dt < t_max)
            ! O_I

            ! S
            U = k * U * dt
            t_cur = t_cur + dt
        end do


The main loop of the model is almost unchanged, we just get the starting time
from the received message's timestamp so as to synchronise with the overall
simulation time correctly. The stopping time is adjusted accordingly as
well. Note that ``t_cur`` and ``t_max`` are numbers, not objects, so they do not
have to be freed. ``rmsg`` however does, and since we have all the information
we need from the received message, we free it here.


Sending messages and Data
`````````````````````````

.. code-block:: fortran

        ! O_F
        sdata = LIBMUSCLE_Data_create_grid(U, 'x')
        smsg = LIBMUSCLE_Message_create(t_cur, sdata)
        call LIBMUSCLE_Instance_send(instance, 'final_state', smsg)
        call LIBMUSCLE_Message_free(smsg)
        call LIBMUSCLE_Data_free(sdata)
        deallocate (U)
    end do

    call LIBMUSCLE_Instance_free(instance)


Having computed our final state, we will send it to the outside world on the
``final_state`` port. In this case, we need to send a vector of doubles, which
we first need to wrap up into a ``Data`` object. A ``Data`` object works just
like a ``DataConstRef``, except that it isn't constant, and can thus be
modified. We do this by creating a ``Data`` object containing a grid value, with
the array ``U`` and the index name ``x``.

Having put our data into the ``Data`` object is a grid, we can then put the grid
into a new :f:type:`LIBMUSCLE_Message` object, and call the
:f:func:`LIBMUSCLE_Instance_send` function to send it. Finally, we free the
Message and Data objects that we created, and deallocate the state as in the
original non-MUSCLE version.

That concludes the reuse loop. When we're done running the model, the reuse loop
will finish, and we can free our Instance object before we quit.

:f:type:`LIBMUSCLE_Data` is quite versatile, and makes it easier to send data of
various types between submodels. Here are some other examples of creating
:f:type:`LIBMUSCLE_Data` objects containing different kinds of data (note that
freeing objects is omitted here for brevity, of course you have to do that in
your model!):

.. code-block:: fortran

    type(LIBMUSCLE_Data) :: d1, d2, d3, d4, d5, d6, d7, d8, d9, d10, d11, d12
    integer (LIBMUSCLE_int8), dimension(2, 3) :: ar
    character(len=1), dimension(1024) :: bytes

    ! create a Data containing a nil value (None in Python)
    d1 = LIBMUSCLE_Data_create()

    ! character strings, logicals
    d2 = LIBMUSCLE_Data_create('String data')
    d3 = LIBMUSCLE_Data_create(.true.)

    ! various kinds of numbers
    d4 = LIBMUSCLE_Data_create(0)                   ! integer
    d5 = LIBMUSCLE_Data_create(100_LIBMUSCLE_int8)  ! 64-bit integer
    d6 = LIBMUSCLE_Data_create(3.141592_LIBMUSCLE_real4)    ! 32-bit real
    d7 = LIBMUSCLE_Data_create(1.4142_LIBMUSCLE_real8)      ! 64-bit real

    ! constant list
    d8 = LIBMUSCLE_Data_create_list()                   ! empty list
    d9 = LIBMUSCLE_Data_create_nils(4_LIBMUSCLE_size)   ! list of length 4
    call LIBMUSCLE_Data_set_item(d9, 1, 'String data')
    call LIBMUSCLE_Data_set_item(d9, 2, .true.)
    call LIBMUSCLE_Data_set_item(d9, 3, 0)
    call LIBMUSCLE_Data_set_item(d9, 4, 1.4142d0)

    ! dictionary
    d10 = LIBMUSCLE_Data_create_dict()
    call LIBMUSCLE_Data_set_item(d10, 'x', x)
    call LIBMUSCLE_Data_set_item(d10, 'y', y)
    call LIBMUSCLE_Data_set_item(d10, 'note', 'Keys must be strings')
    call LIBMUSCLE_Data_set_item(d10, 'nest all you want', d9)

    ! grid
    ar = reshape(spread((/1_LIBMUSCLE_int8/), 1, 6), (/2, 3/))
    d12 = LIBMUSCLE_Data_create_grid(ar)

    ! byte array
    d12 = LIBMUSCLE_Data_create_byte_array(bytes)


As you can see, sending complex data types with MUSCLE is a bit more difficult
in Fortran than in Python, but it is not too burdensome.

If you want to send large amounts of data, then use grids (arrays) as much as
possible. Lists and dicts are more flexible, but they are also slower and take
up much more memory. In particular, a set of objects (agents for example) is
better sent as a dict of arrays (with one 1D array for each attribute) than as a
list of dicts. (The latter will probably work up to 1 million objects or so, but
it will still be slower.)

Handling errors
```````````````

In some cases when you're asking MUSCLE 3 to do something, things can go wrong.
For example, receiving a message from a port does not work if the port is not
connected (unless you passed a default message, see
:f:func:`LIBMUSCLE_Instance_receive`). You cannot extract a real number from a
:f:type:`LIBMUSCLE_DataConstRef` which contains an integer, or obtain a setting
as a character string if the user set it to a logical value. There are two ways
of dealing with these situations: checking in advance if it's going to work and
acting accordingly, or just trying and checking whether you were successful. If
you do neither (which is easiest), MUSCLE 3 will print an error message and stop
your program if an error occurs (which is actually usually what you want).

How to check in advance whether an operation can work depends on what you want
to do. If you want to receive a message, you could use
:f:func:`LIBMUSCLE_Instance_is_connected` to check that the port is connected
before trying to receive. For settings that can be of different types, you can
use ``LIBMUSCLE_Instance_is_setting_a_<type>``, and for data there is
``LIBMUSCLE_DataConstRef_is_a_<type>``.

This does not work in all cases however, for example if you have received a
dictionary that may or may not have a particular key. In that case, (and
anywhere else you think it's more convenient) it's better to just try, and
handle any errors if they occur. This is done by adding one or two extra
arguments to the function call that you expect may fail, like this:

.. code-block:: fortran

    type(LIBMUSCLE_DataConstRef) :: rdata, item
    integer :: err_code
    character(len=:), allocatable :: err_msg

    logical :: value

    ! Receiving rdata omitted

    ! If there is a key 'key' and its value is a logical, set variable
    ! value to that, otherwise set it to .true..
    item = LIBMUSCLE_DataConstRef_get_item(rdata, 'key', err_code, err_msg)
    if (err_code /= LIBMUSCLE_success) then
        print *, err_msg
        ! Need to deallocate the message
        deallocate(err_msg)
        value = .true.
    else
        value = LIBMUSCLE_DataConstRef_as_logical(item, err_code)
        if (err_code /= LIBMUSCLE_success) then
            value = .true.
        end if
    end if


Note that if an error occurs, an error message will be set and the variable
must be deallocated after you're done using it. If no error occurs, the variable
will remain unset, and no deallocation is needed. Passing a variable for an
error message is optional, you can also only request the error code, as shown.
You cannot get only a message, and no code.

Valid error code values are ``LIBMUSCLE_success`` (no error),
``LIBMUSCLE_domain_error`` (incorrect input to a function),
``LIBMUSCLE_out_of_range`` (invalid index), ``LIBMUSCLE_logic_error`` (you tried
to do something that doesn't make sense), ``LIBMUSCLE_runtime_error`` (general
error, e.g.  you're trying to get the length of a scalar port, which does not
make sense), ``LIBMUSCLE_bad_cast`` (value doesn't have the type you're trying
to retrieve it as). See the :ref:`api-docs-fortran` for the function you are
calling to see which error code it will return when exactly.

(Implementation note: which error is returned when is a bit messy still, and
will be cleaned up in a future version.)


Diffusion model
```````````````

If you've studied the above carefully, and have seen the Python version of the
diffusion model, then you should now be able to understand the Fortran diffusion
model below:

.. literalinclude:: examples/fortran/diffusion.f03
  :caption: ``docs/source/examples/fortran/diffusion.f03``
  :language: fortran


In the examples directory, you will find a handy script called
``reaction_diffusion_fortran.sh``, which runs the Fortran reaction-diffusion
model locally. This script launches the MUSCLE Manager and an instance of each
submodel, then waits for the simulation to complete. At the top of this page
there are instructions on how to run the examples.

Also in this directory are Fortran versions of a Monte Carlo sampler and a
round-robin load balancer, plus a script to launch this extended example. See
the `Uncertainty Quantification` section to learn what those are for.

