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

endif

