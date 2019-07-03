.PHONY: all
all: grpc
	@echo

.PHONY: install
ifdef grpc_VERSION
install: grpc
	$(MAKE) -C c-ares install
	$(MAKE) -C zlib install
	$(MAKE) -C openssl install
	mkdir -p $(PREFIX)/lib
	cp -ra grpc/lib/* $(PREFIX)/lib/
else
install:
endif

.PHONY: clean
clean:
	$(MAKE) -C c-ares clean
	$(MAKE) -C zlib clean
	$(MAKE) -C openssl clean

.PHONY: distclean
distclean: clean
	rm -rf v*.tar.gz
	rm -rf grpc-*
	rm -rf grpc
	$(MAKE) -C c-ares distclean
	$(MAKE) -C zlib distclean
	$(MAKE) -C openssl distclean


dep_name := c-ares
dep_min_version := 1.14
dep_version := 1.15.0
dep_pkgconfig_name := libcares
include ../make_available.make

dep_name := zlib
dep_min_version := 1.2.11
dep_version := 1.2.11
dep_pkgconfig_name := zlib
include ../make_available.make

dep_name := openssl
dep_min_version := 1.1.0
dep_version := 1.1.1c
dep_pkgconfig_name := openssl
include ../make_available.make

v$(grpc_VERSION).tar.gz:
	$(DOWNLOAD) https://github.com/grpc/grpc/archive/v$(grpc_VERSION).tar.gz

grpc-$(grpc_VERSION): v$(grpc_VERSION).tar.gz
	$(TAR) xf v$(grpc_VERSION).tar.gz

deps_path := $(c-ares_ROOT)/lib/pkgconfig:$(zlib_ROOT)/lib/pkgconfig:$(protobuf_ROOT)/lib/pkgconfig:$(openssl_ROOT)/lib/pkgconfig
protoc_path := $(protobuf_ROOT)/bin

grpc: | grpc-$(grpc_VERSION) c-ares zlib openssl
	@echo
	@echo 'Building grpc...'
	cd grpc-$(grpc_VERSION) && export prefix=$(CURDIR)/grpc && export PKG_CONFIG_PATH=$(deps_path) && export PATH=${PATH}:$(protoc_path) && export LDFLAGS=-L$(protobuf_ROOT)/lib && export LD_LIBRARY_PATH=${LD_LIBRARY_PATH}:$(protobuf_ROOT)/lib && make run_dep_checks && make -j $(NCORES) && make install
