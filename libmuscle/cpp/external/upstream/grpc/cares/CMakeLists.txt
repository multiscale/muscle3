cmake_minimum_required(VERSION 3.5 FATAL_ERROR)

message(STATUS "Configuring c-ares...")

include(ExternalProject)
ExternalProject_Add(c_ares
  URL               https://c-ares.haxx.se/download/c-ares-1.15.0.tar.gz
  URL_HASH          SHA256=6cdb97871f2930530c97deb7cf5c8fa4be5a0b02c7cea6e7c7667672a39d6852
  DOWNLOAD_NO_PROGRESS 1
  LOG_CONFIGURE        1
  LOG_BUILD            1
  LOG_INSTALL          1
  CMAKE_CACHE_ARGS
    -DCMAKE_INSTALL_PREFIX:PATH=${TOOLS_INSTALL_PREFIX}/cares
    -DCARES_SHARED:BOOL=OFF
    -DCARES_STATIC:BOOL=ON
    -DCARES_STATIC_PIC:BOOL=ON
  )

set(
  c-ares_DIR ${TOOLS_INSTALL_PREFIX}/cares/lib/cmake/c-ares
  CACHE PATH "Path to internally built libcares installation root"
  FORCE
  )

