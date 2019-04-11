#!/bin/bash

# This script downloads sources for dependencies. It is called by CMake at
# configure time.

# We're not using CMake's FetchContent, because it requires a fairly new
# version of CMake, and most clusters have something ancient that does not
# support it.


BUILD_DIR="$1"

# Use wget, of if that's not installed, curl, for downloading
if [ -n $(which wget) ] ; then
    DOWNLOAD='wget'
elif [ -n $(which curl) ] ; then
    DOWNLOAD='curl'
else:
    echo 'We need either wget or curl to be able to download dependencies.'
    echo 'Please install either of those.'
    exit 1
fi

# Check that we have tar to extract archives
if [ -z $(which tar) ] ; then
    echo 'Could not find tar in the path, which is needed for extracting'
    echo 'archives. Please install it.'
    exit 1
fi


# Make directory in build tree
DEPS_DIR=${BUILD_DIR}/third_party_deps
mkdir -p ${DEPS_DIR}

# Download dependencies
# None yet
