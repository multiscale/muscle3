# Make module that defines dummy targets for a dependency already on the
# system.

ifneq ($(MAKECMDGOALS),clean)

.PHONY: $(dep_name)
$(dep_name):
	@echo
	@echo Not building $@, it was already available.

.PHONY: $(dep_name)_install
$(dep_name)_install:

endif

