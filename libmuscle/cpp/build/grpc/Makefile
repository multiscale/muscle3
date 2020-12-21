.PHONY: all
all: grpc
	@echo

.PHONY: install
install: all c-ares_install zlib_install openssl_install
	@echo 'Installing grpc...'
	mkdir -p $(PREFIX)
	cp -ra grpc/* $(PREFIX)/

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
dep_version_constraint := >= 1.11.0
dep_version := 1.15.0
dep_pkgconfig_name := libcares
dep_install := 1
include $(TOOLDIR)/make_available.make

dep_name := zlib
dep_version_constraint := >= 1.2
dep_version := 1.2.11
dep_pkgconfig_name := zlib
dep_install := 1
include $(TOOLDIR)/make_available.make

dep_name := openssl
dep_version_constraint := >= 1.0.2
dep_version := 1.1.1i
dep_pkgconfig_name := openssl
dep_install := 1
include $(TOOLDIR)/make_available.make

v$(grpc_VERSION).tar.gz:
	$(DOWNLOAD) https://github.com/grpc/grpc/archive/v$(grpc_VERSION).tar.gz

grpc-$(grpc_VERSION): v$(grpc_VERSION).tar.gz
	$(TAR) xf v$(grpc_VERSION).tar.gz
	patch -p0 <grpc_issue_14844.patch

protoc_path := $(protobuf_ROOT)/bin

grpc: | grpc-$(grpc_VERSION) c-ares zlib openssl
	@echo
	@echo 'Building grpc...'
	cd grpc-$(grpc_VERSION) && export prefix=$(CURDIR)/grpc && export PKG_CONFIG_PATH=$(PKG_CONFIG_EXTRA_DIRS) && export PATH=$(protoc_path):${PATH} && export LDFLAGS=-L$(protobuf_ROOT)/lib && export LD_LIBRARY_PATH=${LD_LIBRARY_PATH}:$(protobuf_ROOT)/lib:$(c-ares_ROOT)/lib:$(zlib_ROOT)/lib:$(openssl_ROOT)/lib && export CXXFLAGS='-Wno-error' && make -j $(NCORES) && make install
