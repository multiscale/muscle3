# Make module for detecting dependencies

# Define $(dep_name), $(dep_min_version) and $(dep_pkgconfig_name) and include
# this file. It will try to find the dependency in the system directories and
# in the directory set by $(dep_name)_ROOT, and it will set
# $(dep_name)_AVAILABLE to 1, $(dep_name)_ROOT to the prefix and
# $(dep_name)_VERSION to the version if the dependency is found on the system

ifneq ($(MAKECMDGOALS),clean)

$(info )
$(info Checking for $(dep_name) >= $(dep_min_version)...)
$(info - $(dep_name)_ROOT set to $($(dep_name)_ROOT))

_pkg_config := export PKG_CONFIG_PATH=$($(dep_name)_ROOT)/lib/pkgconfig:$(PKG_CONFIG_PATH) && pkg-config
_pkg = '$(dep_pkgconfig_name) >= $(dep_min_version)'

_exists_new_enough := $(shell $(_pkg_config) --exists $(_pkg) || echo NOTFOUND)

ifneq ($(_exists_new_enough), NOTFOUND)
    _modversion = $(shell $(_pkg_config) --modversion $(dep_pkgconfig_name))
    _prefix = $(shell $(_pkg_config) --variable=prefix $(_pkg))
    $(info - $(dep_name) $(_modversion) found at $(_prefix))
    export $(dep_name)_AVAILABLE := 1
    export $(dep_name)_VERSION := $(_modversion)
    export $(dep_name)_ROOT := $(shell $(_pkg_config) --variable=prefix $(_pkg))
else
    _exists := $(shell $(_pkg_config) --exists $(dep_pkgconfig_name) || echo NOTFOUND)
    ifneq ($(_exists), NOTFOUND)
        _modversion = $(shell $(_pkg_config) --modversion $(dep_pkgconfig_name))
        $(info - $(dep_name) $(_modversion) found, but that is too old.)
    else
        $(info - $(dep_name) not found on the system.)
    endif
endif

endif

