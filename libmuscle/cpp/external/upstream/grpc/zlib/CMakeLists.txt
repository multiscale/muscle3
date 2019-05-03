cmake_minimum_required(VERSION 3.5 FATAL_ERROR)

message(STATUS "Configuring zlib...")


find_package(ZLIB ${ZLIB_MINIMUM_REQUIRED})

if(ZLIB_FOUND)
  message(STATUS "Found zlib version ${ZLIB_VERSION_STRING} at ${ZLIB_LIBRARIES}")
  add_library(zlib INTERFACE)
else()
  message(STATUS "zlib 1.2.8 was not found, will build custom zlib instead")

  include(ExternalProject)
  ExternalProject_Add(zlib
    URL               https://www.zlib.net/zlib-1.2.11.tar.gz
    URL_HASH          SHA256=c3e5e9fdd5004dcb542feda5ee4f0ff0744628baf8ed2dd5d66f8ca1197cb1a1
    DOWNLOAD_NO_PROGRESS 1
    LOG_CONFIGURE        1
    LOG_BUILD            1
    LOG_INSTALL          1
    CMAKE_CACHE_ARGS
      -DCMAKE_INSTALL_PREFIX:PATH=${TOOLS_INSTALL_PREFIX}/zlib
    )

  set(
    ZLIB_ROOT ${TOOLS_INSTALL_PREFIX}/zlib
    CACHE PATH "Path to internally built zlib installation root"
    FORCE
    )

endif()

