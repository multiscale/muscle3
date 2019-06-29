cmake_minimum_required(VERSION 3.5 FATAL_ERROR)

project(libmuscle LANGUAGES CXX)


# Configuration options
option(ENABLE_UNIT_TESTS "Enable unit tests" ON)
message(STATUS "Enable testing: ${ENABLE_UNIT_TESTS}")

# Layout of files within the install dir
set(DEF_INSTALL_CMAKEDIR share/cmake/${PROJECT_NAME})
set(INSTALL_CMAKEDIR ${DEF_INSTALL_CMAKEDIR} CACHE PATH "Installation directory for CMake files")

message(STATUS "MUSCLE3 will be installed in ${CMAKE_INSTALL_PREFIX}")

# Set release mode by default
if(NOT CMAKE_BUILD_TYPE)
    set(CMAKE_BUILD_TYPE Release CACHE STRING "Build type" FORCE)
endif()
message(STATUS "Build type set to ${CMAKE_BUILD_TYPE}")


# Tell CMake where to find custom modules
set(CMAKE_MODULE_PATH "${CMAKE_CURRENT_LIST_DIR}/scripts")

# Configure C++ features
set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_EXTENSIONS OFF)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Declare dependency versions
set(GoogleTest_MINIMUM_REQUIRED 1.8.1)
set(Protobuf_MINIMUM_REQUIRED 3.7.1)
set(gRPC_MINIMUM_REQUIRED 1.17.1)
set(ZLIB_MINIMUM_REQUIRED 1.2.8)
set(OPENSSL_MINIMUM_REQUIRED 1.0.2)


# Set up installation directories
include(GNUInstallDirs)

# Layout of built files within the build dir
set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY
      ${CMAKE_BINARY_DIR}/${CMAKE_INSTALL_LIBDIR})
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY
      ${CMAKE_BINARY_DIR}/${CMAKE_INSTALL_LIBDIR})
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY
      ${CMAKE_BINARY_DIR}/${CMAKE_INSTALL_BINDIR})


# Set up superbuild
set_property(DIRECTORY PROPERTY EP_BASE ${CMAKE_BINARY_DIR}/subprojects)
set(STAGED_INSTALL_PREFIX ${CMAKE_BINARY_DIR}/stage)
message(STATUS "${PROJECT_NAME} staged install: ${STAGED_INSTALL_PREFIX}")
set(TOOLS_INSTALL_PREFIX ${CMAKE_BINARY_DIR}/tools)
message(STATUS "${PROJECT_NAME} tools install: ${TOOLS_INSTALL_PREFIX}")

# Build dependencies, if necessary
add_subdirectory(external/upstream)

include(ExternalProject)

# Build libmuscle
ExternalProject_Add(${PROJECT_NAME}_core
  DEPENDS grpc protobuf
  SOURCE_DIR ${CMAKE_CURRENT_LIST_DIR}/src
  CMAKE_ARGS
    -DCMAKE_INSTALL_PREFIX=${STAGED_INSTALL_PREFIX}
    -DCMAKE_BUILD_TYPE=${CMAKE_BUILD_TYPE}
    -DCMAKE_CXX_COMPILER=${CMAKE_CXX_COMPILER}
    -DCMAKE_CXX_FLAGS=${CMKE_CXX_FLAGS}
    -DCMAKE_CXX_STANDARD=${CMAKE_CXX_STANDARD}
    -DCMAKE_CXX_EXTENSIONS=${CMAKE_CXX_EXTENSIONS}
    -DCMAKE_CXX_STANDARD_REQUIRED=${CMAKE_CXX_STANDARD_REQUIRED}
    -DCMAKE_MODULE_PATH=${CMAKE_MODULE_PATH}
    -DINSTALL_LIBDIR=${INSTALL_LIBDIR}
    -DINSTALL_BINDIR=${INSTALL_BINDIR}
    -DINSTALL_INCLUDEDIR=${INSTALL_INCLUDEDIR}
  CMAKE_CACHE_ARGS
    -DCMAKE_PREFIX_PATH:PATH=${CMAKE_PREFIX_PATH}
    -Dc-ares_DIR:PATH=${c-ares_DIR}
    -DProtobuf_DIR:PATH=${Protobuf_DIR}
    -DZLIB_ROOT:PATH=${ZLIB_ROOT}
    -DgRPC_DIR:PATH=${gRPC_DIR}
  BUILD_ALWAYS    1
  )

# Build test suite
if(ENABLE_UNIT_TESTS)
  ExternalProject_Add(${PROJECT_NAME}_tests
    DEPENDS
      ${PROJECT_NAME}_core
      googletest
    SOURCE_DIR ${CMAKE_CURRENT_LIST_DIR}/tests
    CMAKE_ARGS
      -DCMAKE_CXX_COMPILER=${CMAKE_CXX_COMPILER}
      -DCMAKE_CXX_STANDARD=${CMAKE_CXX_STANDARD}
      -DCMAKE_CXX_EXTENSIONS=${CMAKE_CXX_EXTENSIONS}
      -DCMAKE_CXX_STANDARD_REQUIRED=${CMAKE_CXX_STANDARD_REQUIRED}
      -DCMAKE_MODULE_PATH=${CMAKE_MODULE_PATH}
      -DGTEST_ROOT=${GTEST_ROOT}
      -DYMMSL_ROOT=${STAGED_INSTALL_PREFIX}
      -DMUSCLE3_ROOT=${STAGED_INSTALL_PREFIX}
    CMAKE_CACHE_ARGS
      -DCMAKE_CXX_FLAGS:STRING=${CMAKE_CXX_FLAGS}
    BUILD_ALWAYS    1
    LOG_CONFIGURE   1
    LOG_BUILD       1
    LOG_INSTALL     1
    INSTALL_COMMAND ""
  )

  # Add test target and tests
  enable_testing()
  add_test(
    NAME test_ymmsl
    COMMAND test_ymmsl
    WORKING_DIRECTORY "${CMAKE_CURRENT_BINARY_DIR}/subprojects/Build/libmuscle_tests"
    )
  add_test(
    NAME test_muscle3
    COMMAND test_muscle3
    WORKING_DIRECTORY "${CMAKE_CURRENT_BINARY_DIR}/subprojects/Build/libmuscle_tests"
    )
endif()

# Install
install(
  DIRECTORY
    ${STAGED_INSTALL_PREFIX}/
  DESTINATION
    .
  USE_SOURCE_PERMISSIONS
  )

