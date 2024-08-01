# Change Log

All notable changes to this project will be documented in this file.
This project adheres to [Semantic Versioning](http://semver.org/).

## 0.7.1

### Added

- Support for Python 3.11 (working already, now official)
- Enabled type checking support for the libmuscle Python API

### Improved

- Easier crash debugging due to improved root cause detection
- Fixed crash in profiling timeline plot
- Better performance of timeline plot
- Better visual quality of timeline plot
- Improved profiling of shutdown process
- Fixed crash in profiler for large simulations
- Fixed several (harmless) compiler warnings
- Small documentation rendering improvements

### Thanks

- David for reporting many of these and submitting a fix too!


## 0.7.0

### Added

- Checkpointing is now supported in C++ and Fortran as well
- Added built-in profiling feature
- New object-oriented Fortran API (existing API also still available)
- New `Instance.list_settings()` function
- Build support for macOS with CLang and G++/GFortran
- Build support for Cray machines and compilers

### Improved

- Compiling with MPI and linking without or vice versa is now impossible
- Fixed MessagePack build failure on old OSes
- Fixed resource allocation for instance sets
- Planner now detects `F_INIT` -> `O_F` loops and gives an error
- Manager correctly handles instances that never register
- Last lines of log now printer to screen on error for smoother problem solving
- Various small fixes and improvements

### Backwards Incompatible changes

- `Instance.reuse_instance` no longer accepts `apply_overlay` argument. Use
  `InstanceFlags.DONT_APPLY_OVERLAY` when creating the instance instead.
- `LIBMUSCLE_Instance_create` signature has changed, this might lead to errors like:

  .. code-block:: text

       30 |     instance = LIBMUSCLE_Instance_create(ports, MPI_COMM_WORLD, root_rank)
          |               1
    Error: Type mismatch in argument ‘flags’ at (1); passed INTEGER(4) to TYPE(libmuscle_instanceflags)

  You may provide an explicit `InstanceFlags()` argument, or use named arguments:

  .. code-block:: fortran

    instance = LIBMUSCLE_Instance_create(ports, LIBMUSCLE_InstanceFlags(), MPI_COMM_WORLD, root_rank)
    instance = LIBMUSCLE_Instance_create(ports, communicator=MPI_COMM_WORLD, root=root_rank)

- ``DataConstRef`` items can no longer be added to a ``Data`` containing a list or dict.
  The newly added ``DataConstRef::list`` and ``DataConstRef::dict`` should be used
  instead.

### Thanks

- Maarten at Ignition Computing for implementing much of the above
- Peter for debugging the MessagePack build issue
- Peter, Jon and Gavin for ARCHER2 access and support
- Koen for testing macOS build support
- Everyone who reported issues and contributed feature ideas!


## 0.6.0

### Added

- Connecting multiple conduits to outgoing ports
- Checkpointing (preview, not fully reliable and open to change)
- Clang support
- Intel® compiler support
- Error in case different versions of MUSCLE3 are used

### Improved

- TCP latency (performance)
- More helpful messages for configuration errors
- Small documentation improvements

### Removed

- Python 3.6 support

### Thanks

- Maarten at Ignition Computing for implementing much of the above
- The ITER Organisation for funding much of this work


## 0.5.0

### Added

- MUSCLE3 now starts submodels and other components (using QCG-PilotJob)
- Automatic resource management for components on HPC

### Improved

- Build and installation process now even easier
- Improved error messages and reliability
- Cleaner and more informative logging output
- TCP performance and scalability improvements

### Fixed

- Various issues when building and running on HPC clusters
- Many small fixes

### Removed

- Python 3.5 support
- Removed gRPC for faster and more reliable builds
- Pipe-based networking, as it had no benefits and some issues

### Thanks

- Stefan, Merijn and Maarten for reporting issues
- Piotr and Bartek for creating and supporting QCG-PilotJob


## 0.4.0

### Incompatible changes

- `compute_elements` are now called `components` in .ymmsl files

### Improved

- Use latest OpenSSL library when installing it automatically

### Fixed

- Handling of non-contiguous and F-order numpy arrays
- C++ memory usage for large dicts/lists now more reasonable
- Improved shutdown when Python submodel crashes
- Logging warning message


## 0.3.2

### Improved

- Accessing settings from C++ now more flexible
- Python produces more detailed logs to aid in debugging
- Improved pkg-config set-up
- Improved build system output to help find problems
- Documentation on logging in Python
- Protobuf dependency build now more compatible

### Fixed

- C++ list/dict building functions
- C++ use-after-free when receiving grids

### Thanks

- Pavel for testing and reporting issues
- Dongwei for testing and reporting issues


## 0.3.1

### Added

- Support for sending and receiving multidimensional grids/arrays
- Support for Python 3.8

### Improved

- Python 3.5.1 support
- Build compatibility on more operating systems

### Thanks

- Olivier for testing, reporting and fixing build issues
- Pavel for testing and reporting build issues
- Hamid for testing and reporting build issues
- Ben for testing and reporting build issues


## 0.3.0

### Incompatible changes

- Data::key() now returns std::string instead of DataConstRef.
- Data::value() now return Data rather than DataConstRef

### Added

- Support for Fortran, including MPI

### Improved

- Fixes to examples
- Small documentation improvements
- Improved compatibility with other packages using gRPC


### Thanks

- Pavel for reporting documentation/examples issues
- Derek for testing on Eagle
- Dongwei for reporting the gRPC issue


## 0.2.0

### Added

- Support for C++
- Support for MPI in C++

### Improved

- Cluster/HPC networking

### Incompatible Changes

- Fatal logic errors now throw instead of exiting, so that you have a chance
  to shut down the model cleanly before exiting.
- `Instance.exit_error()` was replaced by `Instance.error_shutdown()`, which no
  longer exits the process, it just shuts down the Instance.
- Central MUSCLE 3-managed settings are called settings everywhere now, not
  parameters. As a result, the API has changed in several places.


## 0.1.0

Initial release of MUSCLE 3.

### Added

- Coupling different submodel instances
- Spatial and temporal scale separation and overlap
- Settings management
- Combining features
- Python support
- Initial distributed execution capability
