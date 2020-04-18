# Make module that defines a dummy target for a dependency already on the
# system.

ifneq ($(MAKECMDGOALS),clean)

.PHONY: $(dep_name)
$(dep_name):
	@echo
	@echo Not building $@, it was already available.

endif

