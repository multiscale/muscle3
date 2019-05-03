cmake_minimum_required(VERSION 3.5 FATAL_ERROR)

message(STATUS "Configuring OpenSSL...")


find_package(OpenSSL ${OPENSSL_MINIMUM_REQUIRED})

if(OPENSSL_FOUND)
  message(STATUS "Found OpensSL version ${OPENSSL_VERSION} at ${OPENSSL_SSL_LIBRARY}")
  add_library(openssl INTERFACE)
else()
  message(STATUS "OpenSSL 1.0.2 was not found, will build custom OpenSSL instead")

  include(ExternalProject)
  ExternalProject_Add(openssl
    URL               https://www.openssl.org/source/openssl-1.1.1b.tar.gz
    URL_HASH          SHA256=5c557b023230413dfb0756f3137a13e6d726838ccd1430888ad15bfb2b43ea4b
    DOWNLOAD_NO_PROGRESS 1
    LOG_CONFIGURE        1
    LOG_BUILD            1
    LOG_INSTALL          1
    CONFIGURE_COMMAND    <SOURCE_DIR>/config --prefix=${TOOLS_INSTALL_PREFIX}/openssl
    BUILD_COMMAND        make
    INSTALL_COMMAND      make install
    )

  set(
    OPENSSL_ROOT_DIR ${TOOLS_INSTALL_PREFIX}/openssl
    CACHE PATH "Path to internally built OpenSSL installation root"
    FORCE
    )

endif()

