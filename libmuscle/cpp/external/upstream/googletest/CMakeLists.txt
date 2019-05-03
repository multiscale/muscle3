cmake_minimum_required(VERSION 3.5 FATAL_ERROR)

if(ENABLE_UNIT_TESTS)
  find_package(GoogleTest ${GoogleTest_MINIMUM_REQUIRED} QUIET)

  if(GoogleTest_FOUND)
    message(STATUS "Found GoogleTest version ${GoogleTest_MAJOR_VERSION}.${GoogleTest_MINOR_VERSION}.${GoogleTest_SUBMINOR_VERSION}")
    add_library(googletest INTERFACE)
  else()
    message(STATUS "GoogleTest ${GoogleTest_MINIMUM_REQUIRED} was not found, will build it instead.")

    include(ExternalProject)
    ExternalProject_Add(googletest
      URL               https://github.com/google/googletest/archive/release-${GoogleTest_MINIMUM_REQUIRED}.tar.gz
      URL_HASH          SHA256=9bf1fe5182a604b4135edc1a425ae356c9ad15e9b23f9f12a02e80184c3a249c
      DOWNLOAD_NO_PROGRESS 1
      LOG_CONFIGURE        1
      LOG_BUILD            1
      LOG_INSTALL          1
      CMAKE_ARGS
        -DCMAKE_INSTALL_PREFIX=${TOOLS_INSTALL_PREFIX}/googletest
      BUILD_BYPRODUCTS
        ${TOOLS_INSTALL_PREFIX}/googletest/lib/libgtest.${CMAKE_STATIC_LIBRARY_SUFFIX}
        ${TOOLS_INSTALL_PREFIX}/googletest/lib/libgtest_main.${CMAKE_STATIC_LIBRARY_SUFFIX}
        ${TOOLS_INSTALL_PREFIX}/googletest/lib/libgmock.${CMAKE_STATIC_LIBRARY_SUFFIX}
        ${TOOLS_INSTALL_PREFIX}/googletest/lib/libgmock_main.${CMAKE_STATIC_LIBRARY_SUFFIX}
      )

    set(
      GTEST_ROOT ${TOOLS_INSTALL_PREFIX}/googletest
      CACHE PATH "Path to internally built GoogleTest installation root"
      FORCE
      )

  endif()
endif()

