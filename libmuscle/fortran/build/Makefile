include check_tools.make

CPP_BUILD_DIR := $(CURDIR)/../../cpp/build

DEP_DIRS := $(CPP_BUILD_DIR)/protobuf/protobuf
DEP_DIRS += $(CPP_BUILD_DIR)/grpc/c-ares/c-ares
DEP_DIRS += $(CPP_BUILD_DIR)/grpc/openssl/openssl
DEP_DIRS += $(CPP_BUILD_DIR)/grpc/zlib/zlib
DEP_DIRS += $(CPP_BUILD_DIR)/grpc/grpc
DEP_DIRS += $(CPP_BUILD_DIR)/msgpack/msgpack
export DEP_DIRS

PKG_CONFIG_EXTRA_DIRS := $(CPP_BUILD_DIR)/protobuf/protobuf/lib/pkgconfig
PKG_CONFIG_EXTRA_DIRS := $(PKG_CONFIG_EXTRA_DIRS):$(CPP_BUILD_DIR)/grpc/c-ares/c-ares/lib/pkgconfig
PKG_CONFIG_EXTRA_DIRS := $(PKG_CONFIG_EXTRA_DIRS):$(CPP_BUILD_DIR)/grpc/openssl/openssl/lib/pkgconfig
PKG_CONFIG_EXTRA_DIRS := $(PKG_CONFIG_EXTRA_DIRS):$(CPP_BUILD_DIR)/grpc/zlib/zlib/lib/pkgconfig
PKG_CONFIG_EXTRA_DIRS := $(PKG_CONFIG_EXTRA_DIRS):$(CPP_BUILD_DIR)/grpc/grpc/lib/pkgconfig
PKG_CONFIG_EXTRA_DIRS := $(PKG_CONFIG_EXTRA_DIRS):$(CPP_BUILD_DIR)/msgpack/msgpack/lib/pkgconfig
export PKG_CONFIG_EXTRA_DIRS

ifndef MUSCLE_DISABLE_FORTRAN

.PHONY: all
all: ymmsl libmuscle

.PHONY: test
test: tests
	$(MAKE) -C ymmsl test
	$(MAKE) -C libmuscle test

.PHONY: install
install: all
	$(MAKE) -C ymmsl install
	$(MAKE) -C libmuscle install

.PHONY: ymmsl
ymmsl:
	$(MAKE) -j $(NCORES) -C ymmsl

.PHONY: libmuscle
libmuscle: ymmsl
	$(MAKE) -j $(NCORES) -C libmuscle


.PHONY: tests
tests: ymmsl libmuscle
	$(MAKE) -j $(NCORES) -C ymmsl tests
	$(MAKE) -j $(NCORES) -C libmuscle tests

else        # MUSCLE_DISABLE_FORTRAN

.PHONY: all
all:

.PHONY: test
test:

.PHONY: install
install:

.PHONY: ymmsl
ymmsl:

.PHONY: libmuscle
libmuscle:

.PHONY: tests
tests:

endif       # MUSCLE_DISABLE_FORTRAN


.PHONY: clean
clean:
	$(MAKE) -C ymmsl clean
	$(MAKE) -C libmuscle clean

.PHONY: distclean
distclean:
	$(MAKE) -C ymmsl distclean
	$(MAKE) -C libmuscle distclean

