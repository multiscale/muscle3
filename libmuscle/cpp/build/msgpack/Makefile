.PHONY: all
all: msgpack

.PHONY: install
ifdef msgpack_VERSION
install: msgpack
	mkdir -p $(PREFIX)/lib
	cp -ra msgpack/lib/* $(PREFIX)/lib/
	mkdir -p $(PREFIX)/include
	cp -ra msgpack/include/* $(PREFIX)/include/
else
install:
endif

.PHONY: clean
clean:

.PHONY: distclean
distclean: clean
	rm -f msgpack-*.tar.gz
	rm -rf $$(find . -type d -name 'msgpack-*')
	rm -rf msgpack

dep_name := zlib
dep_min_version := 1.2
dep_version := 1.2.11
dep_pkgconfig_name := zlib
include $(TOOLDIR)/make_available.make


msgpack-$(msgpack_VERSION).tar.gz:
	$(DOWNLOAD) https://github.com/msgpack/msgpack-c/releases/download/cpp-$(msgpack_VERSION)/msgpack-$(msgpack_VERSION).tar.gz

msgpack-$(msgpack_VERSION): msgpack-$(msgpack_VERSION).tar.gz
	$(TAR) xf msgpack-$(msgpack_VERSION).tar.gz

msgpack: msgpack-$(msgpack_VERSION)
	cd msgpack-$(msgpack_VERSION) && mkdir -p build && cd build && \
		export PKG_CONFIG_PATH=$(PKG_CONFIG_EXTRA_DIRS) && \
		cmake -DCMAKE_INSTALL_PREFIX=$(CURDIR)/msgpack -DMSGPACK_CXX11=ON -DMSGPACK_BUILD_EXAMPLES=OFF .. && \
		make -j $(NCORES) && make install

