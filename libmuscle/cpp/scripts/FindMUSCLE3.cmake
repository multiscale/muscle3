# Allow user to override the root install directory
if(NOT MUSCLE3_ROOT)
  set(MUSCLE3_ROOT "$ENV{MUSCLE3_ROOT}")
endif()

# Find the root of the MUSCLE3 installation if not set
if(NOT MUSCLE3_ROOT)
  find_path(_MUSCLE3_ROOT NAMES include/muscle3/version.hpp)
else()
  set(_MUSCLE3_ROOT "${MUSCLE3_ROOT}")
endif()

# Find the include directory
find_path(MUSCLE3_INCLUDE_DIRS NAMES muscle3/muscle3.hpp HINTS ${_MUSCLE3_ROOT}/include)

# Figure out which version this is
set(_MUSCLE3_HPP ${MUSCLE3_INCLUDE_DIRS}/muscle3/muscle3.hpp)

function(_muscle3ver_EXTRACT _MUSCLE3_VER_COMPONENT _MUSCLE3_VER_OUTPUT)
  set(CMAKE_MATCH_1 "0")
  set(_MUSCLE3_expr "^[ \\t]*#define[ \\t]*${_MUSCLE3_VER_COMPONENT}[ \\t]+([0-9]+)$")
  file(STRINGS "${_MUSCLE3_HPP}" _MUSCLE3_ver REGEX "${_MUSCLE3_expr}")
  string(REGEX MATCH "${_MUSCLE3_expr}" MUSCLE3_ver "${_MUSCLE3_ver}")
  set(${_MUSCLE3_VER_OUTPUT} "${CMAKE_MATCH_1}" PARENT_SCOPE)
endfunction()

_muscle3ver_EXTRACT("MUSCLE3_VERSION_MAJOR" MUSCLE3_VERSION_MAJOR)
_muscle3ver_EXTRACT("MUSCLE3_VERSION_MINOR" MUSCLE3_VERSION_MINOR)
_muscle3ver_EXTRACT("MUSCLE3_VERSION_PATCH" MUSCLE3_VERSION_PATCH)

if (MUSCLE3_FIND_VERSION_COUNT GREATER 2)
  set(MUSCLE3_VERSION "${MUSCLE3_VERSION_MAJOR}.${MUSCLE3_VERSION_MINOR}.${MUSCLE3_VERSION_PATCH}")
else()
  set(MUSCLE3_VERSION "${MUSCLE3_VERSION_MAJOR}.${MUSCLE3_VERSION_MINOR}")
endif()

# Find the libraries
find_library(MUSCLE3_LIBRARIES
  NAMES
    muscle3
    "muscle3-${MUSCLE3_VERSION_MAJOR}_${MUSCLE3_VERSION_MINOR}_${MUSCLE3_VERSION_PATCH}"
  HINTS
    ${_MUSCLE3_ROOT}/lib
  )

include(FindPackageHandleStandardArgs)

find_package_handle_standard_args(MUSCLE3
  FOUND_VAR
    MUSCLE3_FOUND
  REQUIRED_VARS
    MUSCLE3_INCLUDE_DIRS
    MUSCLE3_LIBRARIES
  VERSION_VAR
    MUSCLE3_VERSION
  )

