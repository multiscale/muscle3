.PHONY: all
all: ymmsl libmuscle

.PHONY: test
test: tests
	$(MAKE) -C ymmsl test
	$(MAKE) -C libmuscle test

.PHONY: install
install: all msgpack_install
	$(MAKE) -C ymmsl install
	$(MAKE) -C libmuscle install

.PHONY: clean
clean:
	$(MAKE) -C msgpack clean
	$(MAKE) -C googletest clean
	$(MAKE) -C ymmsl clean
	$(MAKE) -C libmuscle clean

.PHONY: distclean
distclean:
	$(MAKE) -C msgpack distclean
	$(MAKE) -C googletest distclean
	$(MAKE) -C ymmsl distclean
	$(MAKE) -C libmuscle distclean

# Find dependencies or set up build

dep_name := msgpack
dep_version_constraint := >= 3.1.0
dep_version := 3.2.0
dep_pkgconfig_name := msgpack
dep_install := 1
include $(TOOLDIR)/make_available.make

dep_name := googletest
dep_version_constraint := >= 1.8.1
dep_version := 1.12.1
dep_pkgconfig_name := gtest
dep_install := 0
include $(TOOLDIR)/make_available.make

# Directories where local builds will be available

DEP_DIRS += $(CURDIR)/msgpack/msgpack
export DEP_DIRS

PKG_CONFIG_EXTRA_DIRS := $(PKG_CONFIG_EXTRA_DIRS):$(CURDIR)/msgpack/msgpack/lib/pkgconfig
export PKG_CONFIG_EXTRA_DIRS


.PHONY: ymmsl
ymmsl:
	@echo
	@echo 'Building ymmsl...'
	$(MAKE) -j $(NCORES) -C ymmsl


.PHONY: libmuscle
libmuscle: ymmsl msgpack
	@echo
	@echo 'Building libmuscle...'
	$(MAKE) -j $(NCORES) -C libmuscle


.PHONY: tests
tests: ymmsl libmuscle msgpack googletest
	$(MAKE) -j $(NCORES) -C ymmsl tests
	$(MAKE) -j $(NCORES) -C libmuscle tests

cpp_test_files := ymmsl/tests/test_* libmuscle/tests/test_*
