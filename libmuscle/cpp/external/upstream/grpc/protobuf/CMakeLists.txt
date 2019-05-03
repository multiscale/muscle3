cmake_minimum_required(VERSION 3.5 FATAL_ERROR)

message(STATUS "Configuring protobuf...")

find_program(Patch_EXECUTABLE NAME patch PATHS ENV PATH DOC "Patch command line executable")
message(STATUS "Found patch at ${Patch_EXECUTABLE}")

include(ExternalProject)
ExternalProject_Add(protobuf
    URL               https://github.com/protocolbuffers/protobuf/releases/download/v${Protobuf_MINIMUM_REQUIRED}/protobuf-cpp-${Protobuf_MINIMUM_REQUIRED}.tar.gz
  URL_HASH          SHA256=97f6cdaa0724d5a8cd3375d5f5cf4bd253d5ad5291154f533ed0d94a9d501ef3
  DOWNLOAD_NO_PROGRESS 1
  LOG_CONFIGURE        1
  LOG_BUILD            1
  LOG_INSTALL          1
  PATCH_COMMAND
    ${Patch_EXECUTABLE} <SOURCE_DIR>/cmake/libprotobuf.cmake ${CMAKE_CURRENT_LIST_DIR}/../../../../scripts/libprotobuf_pic.patch
  CONFIGURE_COMMAND
    ${CMAKE_COMMAND} -DCMAKE_CXX_FLAGS=-fPIC -DCMAKE_C_FLAGS=-fPIC -DCMAKE_INSTALL_PREFIX=${TOOLS_INSTALL_PREFIX}/protobuf -Dprotobuf_BUILD_TESTS=OFF -Dprotobuf_WITH_ZLIB=OFF <SOURCE_DIR>/cmake
  )

set(
    Protobuf_DIR ${TOOLS_INSTALL_PREFIX}/protobuf/lib/cmake/protobuf
  CACHE PATH "Path to internally built protobuf installation"
  FORCE
  )

