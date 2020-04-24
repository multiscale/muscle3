# Make module for building a dependency locally

# This will set $(dep_name)_ROOT to the local installation root dir, and
# $(dep_name)_VERSION to the version we'll build. It also defines a target for
# the dependency that will build it.

ifneq ($(MAKECMDGOALS),clean)

$(info - Will build $(dep_name) automatically.)
export $(dep_name)_ROOT := $(CURDIR)/$(dep_name)/$(dep_name)
export $(dep_name)_VERSION := $(dep_version)

.PHONY: $(dep_name)
$(dep_name):
	@echo
	@echo Building local $@...
	$(MAKE) -C $@

ifeq ($(dep_install), 1)

$(info - Installing, dep_install = $(dep_install))

.PHONY: $(dep_name)_install
$(dep_name)_install: $(dep_name)
	@echo
	@echo Installing local $<...
	$(MAKE) -C $< install

else

.PHONY: $(dep_name)_install
$(dep_name)_install:

endif

endif

