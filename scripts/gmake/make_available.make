# Make module for making dependencies available

# Define $(dep_name), $(dep_min_version) and $(dep_pkgconfig_name) and include
# this file. It will try to find the dependency in the system directories and
# in the directory set by $(dep_name)_ROOT, and it will define a target for it,
# which will do nothing if the dependency was found in the system, or it will
# build the dependency.

# You should also set $(dep_version), which controls the version that will be
# installed automatically if needed (and may be newer than dep_min_version).
# If the dependency needs to be built, then this will be used to set
# $(dep_name)_VERSION when calling the Makefile for the dependency.

# This file will define $(dep_name)_ROOT, if it wasn't set by the user already,
# which can be used to find the installation.

ifneq ($(MAKECMDGOALS),clean)

include $(TOOLDIR)/dep_detect.make

ifeq ($($(dep_name)_AVAILABLE), 1)
    include $(TOOLDIR)/dep_use.make
else
    include $(TOOLDIR)/dep_build.make
endif

endif

