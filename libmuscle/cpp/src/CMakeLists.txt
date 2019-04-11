set(CMAKE_INCLUDE_CURRENT_DIR_IN_INTERFACE ON)

add_library(muscle3-static STATIC "")

set_target_properties(muscle3-static
  PROPERTIES
    POSITION_INDEPENDENT_CODE 1
    OUTPUT_NAME "muscle3"
    DEBUG_POSTFIX "_d"
    PUBLIC_HEADER "tooling.hpp"
    MACOSX_RPATH ON
    WINDOWS_EXPORT_ALL_SYMBOLS ON
  )

target_sources(muscle3-static
  PRIVATE
    ${CMAKE_CURRENT_LIST_DIR}/tooling.cpp
  )

add_library(muscle3-shared SHARED "")

set_target_properties(muscle3-shared
  PROPERTIES
    POSITION_INDEPENDENT_CODE 1
    SOVERSION ${PROJECT_VERSION_MAJOR}
    OUTPUT_NAME "muscle3"
    DEBUG_POSTFIX "_d"
    PUBLIC_HEADER "tooling.hpp"
    MACOSX_RPATH ON
    WINDOWS_EXPORT_ALL_SYMBOLS ON
  )

target_sources(muscle3-shared
  PRIVATE
    ${CMAKE_CURRENT_LIST_DIR}/tooling.cpp
  )


install(
  TARGETS
    muscle3-static
    muscle3-shared
  ARCHIVE
    DESTINATION ${INSTALL_LIBDIR}
    COMPONENT lib
  RUNTIME
    DESTINATION ${INSTALL_BINDIR}
    COMPONENT bin
  LIBRARY
    DESTINATION ${INSTALL_LIBDIR}
    COMPONENT lib
  PUBLIC_HEADER
    DESTINATION ${INSTALL_INCLUDEDIR}/muscle3
    COMPONENT dev
  )

