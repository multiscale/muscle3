MUSCLE 3 Examples
=================

This directory contains examples for MUSCLE 3. Once you've `installed MUSCLE 3
<https://muscle3.readthedocs.io/en/latest/installing.html>`_, you can build them
by running Make from this directory, like this:

.. code-block: bash

    examples$ MUSCLE3_HOME=/path/to/muscle3 make


You can also export the ``MUSCLE3_HOME`` variable to avoid having to type it
all the time:

.. code-block: bash

    examples$ export MUSCLE3_HOME=/path/to/muscle3
    examples$ make

This will build the C++ and Fortran examples (if you have a compiler installed),
and create a virtualenv for running the Python examples and the manager. You can
also build for each language separately, using

.. code-block: bash

    examples$ MUSCLE3_HOME=/path/to/muscle3 make python
    examples$ MUSCLE3_HOME=/path/to/muscle3 make cpp
    examples$ MUSCLE3_HOME=/path/to/muscle3 make fortran


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

    examples$ LD_LIBRARY_PATH=${MUSCLE3_HOME}/lib muscle_manager --start-all rd_implementations.ymmsl rd_python.ymmsl rd_settings.ymmsl


Each run will produce a directory named ``run_<model name>_<date>_<time>`` in
which you can find log files showing what happened.
