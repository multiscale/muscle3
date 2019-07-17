include check_tools.make


.PHONY: all
all: muscle_manager_protocol ymmsl libmuscle

.PHONY: test
test: tests
	$(MAKE) -C ymmsl test
	$(MAKE) -C libmuscle test

.PHONY: install
install: all
	$(MAKE) -C ymmsl install
	$(MAKE) -C libmuscle install
	$(MAKE) -C protobuf install
	$(MAKE) -C grpc install
	$(MAKE) -C msgpack install

.PHONY: clean
clean:
	$(MAKE) -C msgpack clean
	$(MAKE) -C protobuf clean
	$(MAKE) -C grpc clean
	$(MAKE) -C googletest clean
	$(MAKE) -C muscle_manager_protocol clean
	$(MAKE) -C ymmsl clean
	$(MAKE) -C libmuscle clean

.PHONY: distclean
distclean:
	$(MAKE) -C msgpack distclean
	$(MAKE) -C protobuf distclean
	$(MAKE) -C grpc distclean
	$(MAKE) -C googletest distclean
	$(MAKE) -C muscle_manager_protocol distclean
	$(MAKE) -C ymmsl distclean
	$(MAKE) -C libmuscle distclean


dep_name := protobuf
dep_min_version := 3.7.1
dep_version := 3.7.1
dep_pkgconfig_name := protobuf
include make_available.make

export protobuf_ROOT                   # make available to grpc as well

dep_name := grpc
dep_min_version := 1.17.1
dep_version := 1.17.1
dep_pkgconfig_name := grpc
include make_available.make

grpc: protobuf

dep_name := msgpack
dep_min_version := 3.2.0
dep_version := 3.0.0
dep_pkgconfig_name := msgpack
include make_available.make

dep_name := googletest
dep_min_version := 1.8.1
dep_version := 1.8.1
dep_pkgconfig_name := gtest
include make_available.make

export googletest_ROOT


DEP_DIRS := $(CURDIR)/protobuf/protobuf
DEP_DIRS += $(CURDIR)/grpc/c-ares/c-ares
DEP_DIRS += $(CURDIR)/grpc/openssl/openssl
DEP_DIRS += $(CURDIR)/grpc/zlib/zlib
DEP_DIRS += $(CURDIR)/grpc/grpc
DEP_DIRS += $(CURDIR)/msgpack/msgpack
export DEP_DIRS

PKG_CONFIG_EXTRA_DIRS := $(CURDIR)/protobuf/protobuf/lib/pkgconfig
PKG_CONFIG_EXTRA_DIRS := $(PKG_CONFIG_EXTRA_DIRS):$(CURDIR)/grpc/c-ares/c-ares/lib/pkgconfig
PKG_CONFIG_EXTRA_DIRS := $(PKG_CONFIG_EXTRA_DIRS):$(CURDIR)/grpc/openssl/openssl/lib/pkgconfig
PKG_CONFIG_EXTRA_DIRS := $(PKG_CONFIG_EXTRA_DIRS):$(CURDIR)/grpc/zlib/zlib/lib/pkgconfig
PKG_CONFIG_EXTRA_DIRS := $(PKG_CONFIG_EXTRA_DIRS):$(CURDIR)/grpc/grpc/lib/pkgconfig
PKG_CONFIG_EXTRA_DIRS := $(PKG_CONFIG_EXTRA_DIRS):$(CURDIR)/msgpack/msgpack/lib/pkgconfig
export PKG_CONFIG_EXTRA_DIRS


.PHONY: muscle_manager_protocol
muscle_manager_protocol: grpc protobuf
	@echo
	@echo 'Building muscle manager protocol...'
	$(MAKE) -j $(NCORES) -C muscle_manager_protocol

.PHONY: ymmsl
ymmsl:
	@echo
	@echo 'Building ymmsl...'
	$(MAKE) -j $(NCORES) -C ymmsl


.PHONY: libmuscle
libmuscle: grpc ymmsl msgpack muscle_manager_protocol
	@echo
	@echo 'Building libmuscle...'
	$(MAKE) -j $(NCORES) -C libmuscle


.PHONY: tests
tests: ymmsl libmuscle msgpack muscle_manager_protocol googletest
	$(MAKE) -C ymmsl tests
	$(MAKE) -C libmuscle tests

cpp_test_files := ymmsl/tests/test_* libmuscle/tests/test_*
