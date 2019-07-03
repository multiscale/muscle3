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

$(info )
$(info Checking for $(dep_name) >= $(dep_min_version)...)

_pkg_config := export PKG_CONFIG_PATH=$($(dep_name)_ROOT) && pkg-config
_pkg = '$(dep_pkgconfig_name) >= $(dep_min_version)'

_exists != $(_pkg_config) --exists $(_pkg) || echo NOTFOUND

ifneq ($(_exists), NOTFOUND)
    $(info - $(dep_name) found at $(shell $(_pkg_config) --variable=prefix $(_pkg)))
    $(dep_name)_ROOT := $(shell $(_pkg_config) --variable=prefix $(_pkg))

.PHONY: $(dep_name)
$(dep_name):
	@echo Not building $@, it was already available.

else
    $(info - $(dep_name) not found, will build it.)
    $(dep_name)_ROOT := $(CURDIR)/$(dep_name)/$(dep_name)
    export $(dep_name)_VERSION := $(dep_version)

.PHONY: $(dep_name)
$(dep_name):
	@echo
	@echo Building local $@...
	$(MAKE) -C $@
endif

endif

