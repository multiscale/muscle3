cmake_minimum_required(VERSION 3.5 FATAL_ERROR)

# Get version from global VERSION file
file(STRINGS "${CMAKE_CURRENT_LIST_DIR}/../../../VERSION" _VERSION_IN)
string(REGEX REPLACE "^([0-9]+\.[0-9+]+\.[0-9]+).*" "\\1" _VERSION "${_VERSION_IN}")
message(STATUS "Building version ${_VERSION} of libmuscle")

project(muscle3_core
  LANGUAGES CXX
  VERSION ${_VERSION}
  )

# Put the version into version.h
configure_file(version.h.in generated/version.h @ONLY)

include(GNUInstallDirs)
set(CMAKE_INCLUDE_CURRENT_DIR_IN_INTERFACE ON)

set(_YMMSL_PUBLIC_HEADERS
  ymmsl/compute_element.hpp
  ymmsl/version.h
  )

set(_YMMSL_SOURCES
  ${CMAKE_CURRENT_LIST_DIR}/ymmsl/compute_element.cpp
  )

set(_MUSCLE3_PUBLIC_HEADERS
  muscle3.hpp
  tooling.hpp
  ${CMAKE_CURRENT_BINARY_DIR}/generated/version.h
  )

set(_MUSCLE3_SOURCES
  ${CMAKE_CURRENT_LIST_DIR}/tooling.cpp
  ${CMAKE_CURRENT_LIST_DIR}/muscle_manager_protocol/muscle_manager_protocol.pb.cc
  )

# Find dependencies
find_package(Protobuf ${Protobuf_MINIMUM_REQUIRED} CONFIG)
find_package(gRPC ${gRPC_MINIMUM_REQUIRED} CONFIG)

# Set up the ymmsl static build

add_library(ymmsl-static STATIC "")

set_target_properties(ymmsl-static
  PROPERTIES
    POSITION_INDEPENDENT_CODE 1
    OUTPUT_NAME "ymmsl"
    DEBUG_POSTFIX "_d"
    PUBLIC_HEADER "${_YMMSL_PUBLIC_HEADERS}"
    MACOSX_RPATH ON
    WINDOWS_EXPORT_ALL_SYMBOLS ON
  )

target_sources(ymmsl-static
  PRIVATE
    ${_YMMSL_SOURCES}
  )

target_include_directories(ymmsl-static
  PRIVATE
    ${CMAKE_CURRENT_LIST_DIR}
  )


# Set up the ymmsl dynamic build

add_library(ymmsl-shared SHARED "")

# Set up RPATH for when we have dependencies later
file(RELATIVE_PATH _rel ${CMAKE_INSTALL_PREFIX}/${CMAKE_INSTALL_BINDIR} ${CMAKE_INSTALL_PREFIX})
if(APPLE)
  set(_rpath "@loader_path/${_rel}")
else()
  set(_rpath "\$ORIGIN/${_rel}")
endif()
file(TO_NATIVE_PATH "${_rpath}/${CMAKE_INSTALL_LIBDIR}" YMMSL_RPATH)

set_target_properties(ymmsl-shared
  PROPERTIES
    POSITION_INDEPENDENT_CODE 1
    VERSION "${PROJECT_VERSION_MAJOR}.${PROJECT_VERSION_MINOR}.${PROJECT_VERSION_PATCH}"
    SOVERSION ${PROJECT_VERSION_MAJOR}
    OUTPUT_NAME "ymmsl"
    DEBUG_POSTFIX "_d"
    PUBLIC_HEADER "${_YMMSL_PUBLIC_HEADERS}"
    MACOSX_RPATH ON
    SKIP_BUILD_RPATH OFF
    BUILD_WITH_INSTALL_RPATH OFF
    INSTALL_RPATH "${YMMSL_RPATH}"
    INSTALL_RPATH_USE_LINK_PATH ON
  )

target_sources(ymmsl-shared
  PRIVATE
    ${_YMMSL_SOURCES}
  )

target_include_directories(ymmsl-shared
  PRIVATE
    ${CMAKE_CURRENT_LIST_DIR}
  )


# Set up the static build

add_library(muscle3-static STATIC "")

set_target_properties(muscle3-static
  PROPERTIES
    POSITION_INDEPENDENT_CODE 1
    OUTPUT_NAME "muscle3"
    DEBUG_POSTFIX "_d"
    PUBLIC_HEADER "${_MUSCLE3_PUBLIC_HEADERS}"
    MACOSX_RPATH ON
    WINDOWS_EXPORT_ALL_SYMBOLS ON
  )

target_sources(muscle3-static
  PRIVATE
    ${_MUSCLE3_SOURCES}
  )

target_include_directories(muscle3-static
  PRIVATE
    ${CMAKE_CURRENT_LIST_DIR}
  )

target_link_libraries(muscle3-static
  PRIVATE
    protobuf::libprotobuf
    gRPC::grpc++
  )

# Set up the dynamic build

add_library(muscle3-shared SHARED "")

# Set up RPATH for when we have dependencies later
file(RELATIVE_PATH _rel ${CMAKE_INSTALL_PREFIX}/${CMAKE_INSTALL_BINDIR} ${CMAKE_INSTALL_PREFIX})
if(APPLE)
  set(_rpath "@loader_path/${_rel}")
else()
  set(_rpath "\$ORIGIN/${_rel}")
endif()
file(TO_NATIVE_PATH "${_rpath}/${CMAKE_INSTALL_LIBDIR}" LIBMUSCLE_RPATH)

set_target_properties(muscle3-shared
  PROPERTIES
    POSITION_INDEPENDENT_CODE 1
    VERSION "${PROJECT_VERSION_MAJOR}.${PROJECT_VERSION_MINOR}.${PROJECT_VERSION_PATCH}"
    SOVERSION ${PROJECT_VERSION_MAJOR}
    OUTPUT_NAME "muscle3"
    DEBUG_POSTFIX "_d"
    PUBLIC_HEADER "${_MUSCLE3_PUBLIC_HEADERS}"
    MACOSX_RPATH ON
    SKIP_BUILD_RPATH OFF
    BUILD_WITH_INSTALL_RPATH OFF
    INSTALL_RPATH "${LIBMUSCLE_RPATH}"
    INSTALL_RPATH_USE_LINK_PATH ON
  )

target_sources(muscle3-shared
  PRIVATE
    ${_MUSCLE3_SOURCES}
  )

target_include_directories(muscle3-shared
  PRIVATE
    ${CMAKE_CURRENT_LIST_DIR}
  )

target_link_libraries(muscle3-shared
  PRIVATE
    protobuf::libprotobuf
    gRPC::grpc++
  )


# Install the libraries
# The superbuild root script will have us do this inside the build dir, and take care of final installation
install(
  TARGETS
    ymmsl-static
  ARCHIVE
    DESTINATION ${CMAKE_INSTALL_LIBDIR}
    COMPONENT lib
  PUBLIC_HEADER
    DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}/ymmsl
    COMPONENT dev
  )

install(
  TARGETS
    muscle3-static
    muscle3-shared
  ARCHIVE
    DESTINATION ${CMAKE_INSTALL_LIBDIR}
    COMPONENT lib
  LIBRARY
    DESTINATION ${CMAKE_INSTALL_LIBDIR}
    COMPONENT lib
  PUBLIC_HEADER
    DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}/muscle3
    COMPONENT dev
  )

