Installing
==========

As described before, MUSCLE 3 consists of several components: libmuscle, the
YMMSL Python library, and the MUSCLE Manager. Furthermore, libmuscle currently
has a Python and a C++ version.

Python
------

Installing MUSCLE 3 on Python will install all the Python-based components of
the system, i.e. the Python version of libmuscle, the YMMSL Python library, and
the MUSCLE Manager. This requires Python 3.5, 3.6 or 3.7; 3.8 may work but is
untested.

MUSCLE 3 is on PyPI as an ordinary Python package, so it can be installed via
Pip in the usual way. It's normally a good idea to make a virtual environment
(virtualenv), if you don't yet have one:

.. code-block:: bash

  ~$ python3 -m venv muscle3_venv
  ~$ . muscle3_venv/bin/activate
  (muscle3_venv)~$ pip install muscle3


This will create a Python virtualenv in a directory named ``muscle3_venv`` in
your home directory, activate it, and then install MUSCLE 3 inside of it. You
can then use MUSCLE 3 whenever you have the virtualenv activated. This will also
install the Python YMMSL library, and any required dependencies.

You can also install MUSCLE 3 without a virtualenv if your system allows that.
The advantage of virtual environments is that you can keep different programs
separate, and reduce the chance of library version mismatches. On the other
hand, not having to activate the virtual environment saves you a step.

If you want to install the Python YMMSL library without installing MUSCLE 3,
then you can use

.. code-block:: bash

    ~$ pip3 install ymmsl


C++
---

To work with MUSCLE 3 from C++, you need to install the C++ version of
libmuscle. Currently, that means building it from source. This is a bit more
involved than installing the Python version, but comparable to (and maybe
slightly easier than) installing most C++ libraries.

Prerequisites
`````````````

To build libmuscle, we're going to need some tools. In particular, we need a C++
compiler and GNU make. MUSCLE 3 uses C++14, so you need at least g++ 4.9.3.
Clang is expected to work, but that's not been tested, nor has any other
compiler. If you want to try, go right ahead, we'd love to have feedback on
this. Building has been tested with gmake 3.82 and 4.1.

If you're doing C++ development on a reasonably modern Linux, then you probably
already have a suitable compiler installed. If not, on a Debian (or Ubuntu)
based system, ``sudo apt-get install build-essential`` should get you set up. On
a cluster, there is usually a ``module load g++`` or similar command available
that sets you up with g++ and associated tools. The exact command will vary from
machine to machine, so consult the documentation for your cluster and/or ask the
helpdesk.

If your submodels use MPI, then you'll need an MPI library. Libmuscle has been
tested with OpenMPI on Ubuntu, but should work with other MPI implementations
(this being the point of the MPI standard). On Debian/Ubuntu, ``sudo apt-get
install libopenmpi-dev`` will install the OpenMPI development files needed to
compile libmuscle C++ with MPI support. On a cluster, there is probably a
``module load openmpi`` or similar command to make MPI available.

(No) Dependencies
`````````````````

MUSCLE 3 uses several third-party libraries, which need to be available when it
is built. If you have them available, they should be detected automatically; if
not, MUSCLE 3 will **download and install them automatically**.

The dependencies are:

- c-ares 1.11.0 or later
- gRPC 1.17.1 or later
- MessagePack 3.2.0 or later
- OpenSSL 1.0.2 or later
- Protobuf 3.7.1 or later
- zlib 1.2.x


If your model uses any of these dependencies directly, then it's best to install
that dependency on your system, either via the package manager or from source,
and then link both your library and MUSCLE 3 to the dependency. This avoids
having two different versions around and active at the same time. Otherwise,
it's easier to rely on the automatic installation.

Downloading MUSCLE 3
````````````````````

With the tools available, we can download and install MUSCLE 3. First, we create
a working directory, download MUSCLE 3 into it, then unpack the downloaded
archive and enter the main directory:

.. code-block:: bash

  ~$ mkdir muscle3_source
  ~$ cd muscle3_source
  ~/muscle3_source$ wget https://github.com/multiscale/muscle3/archive/0.2.0/muscle3-0.2.0.tar.gz
  ~/muscle3_source$ tar xf muscle3-0.2.0.tar.gz
  ~/muscle3_source$ cd muscle3-0.2.0


Of course, you can put the source anywhere you like.


Building MUSCLE 3
`````````````````

The basic command for building MUSCLE 3 is:

.. code-block:: bash

  ~/muscle3_source/muscle3-0.2.0$ make


There are a few options that can be added by setting them as environment
variables. These are as follows:

MUSCLE_ENABLE_MPI=1
    Compile the MPI version of libmuscle as well as the non-MPI version. This
    requires an MPI library (including development files) to be available, as
    described above.

NCORES=<n>
    Use the given number of cores to compile MUSCLE 3. By default, MUSCLE 3 will
    use as many cores (threads) as you have. If you want to use fewer, you can
    set the number here. Using more will not make it go faster, and is not
    recommended.

CXX=<compiler command>
    By default, MUSCLE 3 will try to compile itself using ``g++``. If you want
    to use a different compiler, then you can set CXX to something else. The
    MPI version will always be compiled with ``mpic++``.

DOWNLOAD=<download command>
    MUSCLE 3 will try to use either ``wget`` or ``curl`` to download
    dependencies. This lets you override the command to use, or select one
    explicitly.

TAR=<tar command>
    This overrides the command used to unpack dependencies, which by default is
    ``tar``.


As an example, to build libmuscle with MPI support, and using 2 cores, you would
do:

.. code-block:: bash

  ~/muscle3_source/muscle3-0.2.0$ MUSCLE_ENABLE_MPI=1 NCORES=2 make


This will take a few minutes, depending on the speed of your machine; cluster
nodes may be much faster.

Installing libmuscle C++
````````````````````````

Finally, we need to install MUSCLE 3. We recommend installing it into a
subdirectory of your home directory for now, as opposed to ``/usr/local/bin`` or
something similar (although ``/opt/muscle3`` would be okay), since there is no
uninstall command yet that will cleanly remove it. That goes like this:

.. code-block:: bash

  ~/muscle3_source/muscle3-0.2.0$ PREFIX=~/muscle3 make install


This command will install the C++ version of MUSCLE 3 into the directory
specified by ``PREFIX``, in this case the ``muscle3`` directory in your home
directory.

From this point on, the source directory is no longer needed. If you don't want
to play with the examples (in ``docs/source/examples/cpp``) then you can remove
it if you want.

Compiling and linking with libmuscle C++
````````````````````````````````````````

Once libmuscle is installed, you will have to add some code to your model to
talk to libmuscle, or you can write a compute element from scratch. Examples of
how to do that are in the C++ section of this manual. In order to compile and
link your code with libmuscle, you have to adjust the compilation and linking
commands a bit though.

When compiling, the compiler needs to be able to find the MUSCLE 3 headers. You
can point it to them by adding

.. code-block::

  -I<PREFIX>/include


to your compiler command line, where `<PREFIX>` is where you installed it. If
your submodel uses MPI, then you must add

.. code-block::

  -DMUSCLE_ENABLE_MPI


as well to make the MPI-specific parts of the libmuscle API available, and of
course remember to use ``mpic++`` or ``mpicxx`` to compile.

When linking, the linker needs to be told where to find the ``ymmsl`` and
``libmuscle`` libraries, and that it should link with them. That's done by
adding

.. code-block::

  -L<PREFIX>/lib -lymmsl -lmuscle


to the command line, or for MPI compute elements:

.. code-block::

  -L<PREFIX>/lib -lymmsl -lmuscle_mpi


There's one more thing: the directory that you've install MUSCLE into is
probably not in your system's library search path, and as a result the dynamic
linker won't be able to find the libraries when you run your program. In order
to fix this, ``LD_LIBRARY_PATH`` must be set, which you can do with the
following command:

.. code-block:: bash

       ~$ export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:<PREFIX>/lib


If you have just installed MUSCLE 3, then the above bits are currently on your
screen, with ``<PREFIX>`` filled out already, so you can just copy-paste them
from there.

