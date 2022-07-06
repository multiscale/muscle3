MUSCLE 3 Examples
=================

This directory contains examples for MUSCLE 3. Once you've `installed MUSCLE 3
<https://muscle3.readthedocs.io/en/latest/installing.html>`_, you can build them
by activating the installation and running Make from this directory, like this:

.. code-block: bash

    examples$ . /path/to/muscle3/bin/muscle3.env
    examples$ make


If this gives an error saying that the ``make`` command could not be found,
then you need to install GNU make using ``apt-get install make`` and try again.

This will build the C++ and Fortran examples (if you have a compiler installed),
and create a virtualenv for running the Python examples and the manager. If you
have MPI available, then those examples will be built as well.

You can also build for each language separately, using

.. code-block: bash

    examples$ make python
    examples$ make cpp
    examples$ make fortran


Note that the C++ and Fortran builds will run the Python one as well, because
it does the set-up required to run the manager, which you always need to run a
MUSCLE3 simulation.

Once you've built the examples, you can run them via the MUSCLE manager. By
specifying different yMMSL files, different scenarios can be run. The various
implementations are all listed in the ``rd_implementations.ymmsl`` file. Then
there are various ``rd_python.ymmsl`` and ``rd_cpp.ymmsl`` and so on files
which specify different combinations of implementations for the different
submodels. Finally, you'll want to apply the settings, which are in
``rd_settings.ymmsl``.

For example, to run the all-Python version of the reaction-diffusion model, you
can use:

.. code-block: bash

    examples$ muscle_manager --start-all rd_implementations.ymmsl rd_python.ymmsl rd_settings.ymmsl


Each run will produce a directory named ``run_<model name>_<date>_<time>`` in
which you can find log files showing what happened.
