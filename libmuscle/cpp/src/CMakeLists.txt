cmake_minimum_required(VERSION 3.5 FATAL_ERROR)

project(muscle3_core
  LANGUAGES CXX
  VERSION 0.1.0
  )

include(GNUInstallDirs)
set(CMAKE_INCLUDE_CURRENT_DIR_IN_INTERFACE ON)

set(_MUSCLE3_PUBLIC_HEADERS
  muscle3.hpp
  tooling.hpp
  )

set(_MUSCLE3_SOURCES
  ${CMAKE_CURRENT_LIST_DIR}/tooling.cpp
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


# Install the library
# The superbuild root script will have us do this inside the build dir, and take care of final installation
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

