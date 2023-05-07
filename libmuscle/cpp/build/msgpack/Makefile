.PHONY: all
all: msgpack

.PHONY: install
install: msgpack
	mkdir -p $(PREFIX)/lib
	cp -a msgpack/lib/* $(PREFIX)/lib/
	mkdir -p $(PREFIX)/include
	cp -a msgpack/include/* $(PREFIX)/include/

.PHONY: clean
clean:

.PHONY: distclean
distclean: clean
	rm -f msgpack-*.tar.gz
	rm -rf $$(find . -type d -name 'msgpack-*')
	rm -rf msgpack

msgpack-$(msgpack_VERSION).tar.gz:
	$(DOWNLOAD) https://github.com/msgpack/msgpack-c/releases/download/cpp-$(msgpack_VERSION)/msgpack-$(msgpack_VERSION).tar.gz

msgpack-$(msgpack_VERSION): msgpack-$(msgpack_VERSION).tar.gz
	$(TAR) xf msgpack-$(msgpack_VERSION).tar.gz

.PHONY: msgpack-install
msgpack-install: msgpack-$(msgpack_VERSION)
	cd msgpack-$(msgpack_VERSION) && mkdir -p build && cd build && \
		export PKG_CONFIG_PATH=$(PKG_CONFIG_PATH):$(PKG_CONFIG_EXTRA_DIRS) && \
		cmake -DCMAKE_INSTALL_PREFIX=$(CURDIR)/msgpack -DMSGPACK_CXX11=ON -DMSGPACK_BUILD_EXAMPLES=OFF .. && \
		$(MAKE) -j $(NCORES) && make install

ifdef MUSCLE_LINUX

msgpack: msgpack-install

else ifdef MUSCLE_MACOS

msgpack: msgpack-install
	install_name_tool -id $(CURDIR)/msgpack/lib/libmsgpackc.dylib $(CURDIR)/msgpack/lib/libmsgpackc.dylib

endif

