MUSCLE 3 Examples
=================

This directory contains examples for MUSCLE 3. Once you've `installed MUSCLE 3
<https://muscle3.readthedocs.io/en/latest/installing.html>`_, you can build them
by running Make from this directory, like this:

.. code-block: bash

    examples$ MUSCLE3_HOME=/path/to/muscle3 make


This will build the C++ and Fortran examples, and create a virtualenv for
running the Python examples and the manager. You can also build for each
language separately, using

.. code-block: bash

    examples$ MUSCLE3_HOME=/path/to/muscle3 make python
    examples$ MUSCLE3_HOME=/path/to/muscle3 make cpp
    examples$ MUSCLE3_HOME=/path/to/muscle3 make fortran


Note that you need to run the Python build in order to be able to run the C++ or
Fortran examples, as it does the set-up required to run the manager, which you
always need to run a MUSCLE simulation.

Once you've built the examples, you can run them using the shell scripts in this
directory, e.g.

.. code-block: bash

    examples$ MUSCLE3_HOME=/path/to/muscle3 ./reaction_diffusion_cpp.sh


You can also export the ``MUSCLE3_HOME`` variable to avoid having to type it all
the time:

.. code-block: bash

    examples$ export MUSCLE3_HOME=/path/to/muscle3
    examples$ ./reaction_diffusion_cpp.sh
