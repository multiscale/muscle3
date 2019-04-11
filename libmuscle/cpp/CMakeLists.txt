cmake_minimum_required(VERSION 3.5 FATAL_ERROR)

project(libmuscle
  LANGUAGES CXX
  VERSION 0.1.0
  )


# Configure C++ features
set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_EXTENSIONS OFF)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

message(STATUS "MUSCLE3 will be installed in ${CMAKE_INSTALL_PREFIX}")


# Set release mode by default
if(NOT CMAKE_BUILD_TYPE)
    set(CMAKE_BUILD_TYPE Release CACHE STRING "Build type" FORCE)
endif()
message(STATUS "Build type set to ${CMAKE_BUILD_TYPE}")


# Set up installation directories
include(GNUInstallDirs)

set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY
      ${CMAKE_BINARY_DIR}/${CMAKE_INSTALL_LIBDIR})
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY
      ${CMAKE_BINARY_DIR}/${CMAKE_INSTALL_LIBDIR})
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY
      ${CMAKE_BINARY_DIR}/${CMAKE_INSTALL_BINDIR})

set(INSTALL_LIBDIR ${CMAKE_INSTALL_LIBDIR} CACHE PATH "Installation directory for libraries")
set(INSTALL_BINDIR ${CMAKE_INSTALL_BINDIR} CACHE PATH "Installation directory for executables")
set(INSTALL_INCLUDEDIR ${CMAKE_INSTALL_INCLUDEDIR} CACHE PATH "Installation directory for header files")
if(WIN32 AND NOT CYGWIN)
  set(DEF_INSTALL_CMAKEDIR CMake)
else()
  set(DEF_INSTALL_CMAKEDIR share/cmake/${PROJECT_NAME})
endif()
set(INSTALL_CMAKEDIR ${DEF_INSTALL_CMAKEDIR} CACHE PATH "Installation directory for CMake files")

# Download GoogleTest
include(scripts/googletest.cmake)
download_googletest()

# Install other dependencies
find_program(BASH_EXECUTABLE bash)

execute_process(
    COMMAND
    ${BASH_EXECUTABLE} get_deps.sh ${CMAKE_CURRENT_BINARY_DIR}
    WORKING_DIRECTORY
        ${CMAKE_CURRENT_LIST_DIR}
    )


# Add source directories
add_subdirectory(src)

enable_testing()
add_subdirectory(tests)
