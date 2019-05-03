cmake_minimum_required(VERSION 3.5 FATAL_ERROR)

find_package(GRPC ${gRPC_MINIMUM_REQUIRED})

if(gRPC_FOUND)
  message(STATUS "Found gRPC version ${gRPC_MAJOR_VERSION}.${gRPC_MINOR_VERSION}.${gRPC_SUBMINOR_VERSION}")
  add_library(grpc INTERFACE)
else()
  message(STATUS "gRPC ${gRPC_MINIMUM_REQUIRED} was not found, will build it instead.")

  add_subdirectory(cares)
  add_subdirectory(zlib)
  add_subdirectory(openssl)
  add_subdirectory(protobuf)

  set(_gRPC_SETTINGS
      -DCMAKE_INSTALL_PREFIX:PATH=${TOOLS_INSTALL_PREFIX}/grpc
      -DgRPC_INSTALL:BOOL=ON
      -DgRPC_BUILD_TEST:BOOL=OFF
      -DgRPC_PROTOBUF_PROVIDER:STRING=package
      -DgRPC_PROTOBUF_PACKAGE_TYPE:STRING=CONFIG
      -DProtobuf_DIR:PATH=${TOOLS_INSTALL_PREFIX}/protobuf/lib/cmake/protobuf
      -DgRPC_ZLIB_PROVIDER:STRING=package
      -DgRPC_CARES_PROVIDER:STRING=package
      -Dc-ares_DIR:PATH=${TOOLS_INSTALL_PREFIX}/cares/lib/cmake/c-ares
      -DgRPC_SSL_PROVIDER:STRING=package
      )

  find_package(ZLIB ${ZLIB_MINIMUM_REQUIRED})
  if(ZLIB_FOUND)
    message(STATUS "Configuring gRPC with system zlib.")
  else()
    message(STATUS "Configuring gRPC with built zlib.")
    list(APPEND _gRPC_SETTINGS -DZLIB_ROOT:STRING=${ZLIB_ROOT})
  endif()

  find_package(OpenSSL ${OPENSSL_MINIMUM_REQUIRED})
  if(OPENSSL_FOUND)
    message(STATUS "Configuring gRPC with system OpenSSL.")
  else()
    message(STATUS "Configuring gRPC with built OpenSSL.")
    list(APPEND _gRPC_SETTINGS -DOPENSSL_ROOT_DIR:STRING=${OPENSSL_ROOT_DIR})
  endif()

  message(STATUS "gRPC build settings: ${_gRPC_SETTINGS}")

  include(ExternalProject)
  ExternalProject_Add(grpc
    URL               https://github.com/grpc/grpc/archive/v1.17.1.tar.gz
    URL_HASH          SHA256=48430f34e99016d4561144d134eb225e28edb7a828aa66b501306480edb00b90
    DOWNLOAD_NO_PROGRESS 1
    LOG_CONFIGURE        1
    LOG_BUILD            1
    LOG_INSTALL          1
    CMAKE_CACHE_ARGS ${_gRPC_SETTINGS}
    DEPENDS
      c_ares
      openssl
      protobuf
      zlib
    )

  set(
    gRPC_DIR ${TOOLS_INSTALL_PREFIX}/grpc/lib/cmake/grpc
    CACHE PATH "Path to internally built gRPC installation root"
    FORCE
    )

endif()

