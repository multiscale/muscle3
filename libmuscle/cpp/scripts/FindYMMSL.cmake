# Allow user to override the root install directory
if(NOT YMMSL_ROOT)
  set(YMMSL_ROOT "$ENV{YMMSL_ROOT}")
endif()

# Find the root of the YMMSL installation if not set
if(NOT YMMSL_ROOT)
  find_path(_YMMSL_ROOT NAMES include/ymmsl/version.h)
else()
  set(_YMMSL_ROOT "${YMMSL_ROOT}")
endif()

# Find the include directory
find_path(YMMSL_INCLUDE_DIRS NAMES ymmsl/version.h HINTS ${_YMMSL_ROOT}/include)

# Figure out which version this is
set(_YMMSL_HPP ${YMMSL_INCLUDE_DIRS}/ymmsl/version.h)

function(_ymmslver_EXTRACT _YMMSL_VER_COMPONENT _YMMSL_VER_OUTPUT)
  set(CMAKE_MATCH_1 "0")
  set(_YMMSL_expr "^[ \\t]*#define[ \\t]*${_YMMSL_VER_COMPONENT}[ \\t]+([0-9]+)$")
  file(STRINGS "${_YMMSL_HPP}" _YMMSL_ver REGEX "${_YMMSL_expr}")
  string(REGEX MATCH "${_YMMSL_expr}" YMMSL_ver "${_YMMSL_ver}")
  set(${_YMMSL_VER_OUTPUT} "${CMAKE_MATCH_1}" PARENT_SCOPE)
endfunction()

_ymmslver_EXTRACT("YMMSL_VERSION_MAJOR" YMMSL_VERSION_MAJOR)
_ymmslver_EXTRACT("YMMSL_VERSION_MINOR" YMMSL_VERSION_MINOR)
_ymmslver_EXTRACT("YMMSL_VERSION_PATCH" YMMSL_VERSION_PATCH)

if (YMMSL_FIND_VERSION_COUNT GREATER 2)
  set(YMMSL_VERSION "${YMMSL_VERSION_MAJOR}.${YMMSL_VERSION_MINOR}.${YMMSL_VERSION_PATCH}")
else()
  set(YMMSL_VERSION "${YMMSL_VERSION_MAJOR}.${YMMSL_VERSION_MINOR}")
endif()

# Find the libraries
find_library(YMMSL_LIBRARIES
  NAMES
    ymmsl
    "ymmsl-${YMMSL_VERSION_MAJOR}_${YMMSL_VERSION_MINOR}_${YMMSL_VERSION_PATCH}"
  HINTS
    ${_YMMSL_ROOT}/lib
  )

include(FindPackageHandleStandardArgs)

find_package_handle_standard_args(YMMSL
  FOUND_VAR
    YMMSL_FOUND
  REQUIRED_VARS
    YMMSL_INCLUDE_DIRS
    YMMSL_LIBRARIES
  VERSION_VAR
    YMMSL_VERSION
  )

