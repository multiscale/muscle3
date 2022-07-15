###########
Change Log
###########

All notable changes to this project will be documented in this file.
This project adheres to `Semantic Versioning <http://semver.org/>`_.

0.5.0
*****

Added
-----

* MUSCLE3 now starts submodels and other components (using QCG-PilotJob)
* Automatic resource management for components on HPC

Improved
--------

* Build and installation process now even easier
* Improved error messages and reliability
* Cleaner and more informative logging output
* TCP performance and scalability improvements

Fixed
-----

* Various issues when building and running on HPC clusters
* Many small fixes

Removed
-------

* Python 3.5 support
* Removed gRPC for faster and more reliable builds
* Pipe-based networking, as it had no benefits and some issues

Thanks
------

* Stefan, Merijn and Maarten for reporting issues
* Piotr and Bartek for creating and supporting QCG-PilotJob


0.4.0
*****

Incompatible changes
--------------------

* `compute_elements` are now called `components` in .ymmsl files

Improved
--------

* Use latest OpenSSL library when installing it automatically

Fixed
-----

* Handling of non-contiguous and F-order numpy arrays
* C++ memory usage for large dicts/lists now more reasonable
* Improved shutdown when Python submodel crashes
* Logging warning message


0.3.2
*****

Improved
--------

* Accessing settings from C++ now more flexible
* Python produces more detailed logs to aid in debugging
* Improved pkg-config set-up
* Improved build system output to help find problems
* Documentation on logging in Python
* Protobuf dependency build now more compatible

Fixed
-----

* C++ list/dict building functions
* C++ use-after-free when receiving grids

Thanks
------

* Pavel for testing and reporting issues
* Dongwei for testing and reporting issues


0.3.1
*****

Added
-----

* Support for sending and receiving multidimensional grids/arrays
* Support for Python 3.8

Improved
--------

* Python 3.5.1 support
* Build compatibility on more operating systems

Thanks
------

* Olivier for testing, reporting and fixing build issues
* Pavel for testing and reporting build issues
* Hamid for testing and reporting build issues
* Ben for testing and reporting build issues


0.3.0
*****

Incompatible changes
--------------------

* Data::key() now returns std::string instead of DataConstRef.
* Data::value() now return Data rather than DataConstRef

Added
-----

* Support for Fortran, including MPI

Improved
--------

* Fixes to examples
* Small documentation improvements
* Improved compatibility with other packages using gRPC


Thanks
------

* Pavel for reporting documentation/examples issues
* Derek for testing on Eagle
* Dongwei for reporting the gRPC issue


0.2.0
*****

Added
-----

* Support for C++
* Support for MPI in C++

Improved
--------

* Cluster/HPC networking

Incompatible Changes
-------

* Fatal logic errors now throw instead of exiting, so that you have a chance
  to shut down the model cleanly before exiting.
* Instance.exit_error() was replaced by Instance.error_shutdown(), which no
  longer exits the process, it just shuts down the Instance.
* Central MUSCLE 3-managed settings are called settings everywhere now, not
  parameters. As a result, the API has changed in several places.


0.1.0
*****

Initial release of MUSCLE 3.

Added
-----
* Coupling different submodel instances
* Spatial and temporal scale separation and overlap
* Settings management
* Combining features
* Python support
* Initial distributed execution capability
