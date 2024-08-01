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

MSGPACK_LIB=$(CURDIR)/msgpack/lib/libmsgpackc.a
MSGPACK_SRC=$(CURDIR)/msgpack-$(msgpack_VERSION)/ChangeLog

msgpack-$(msgpack_VERSION).tar.gz:
	$(DOWNLOAD) https://github.com/msgpack/msgpack-c/releases/download/cpp-$(msgpack_VERSION)/msgpack-$(msgpack_VERSION).tar.gz

$(MSGPACK_SRC): msgpack-$(msgpack_VERSION).tar.gz
	$(TAR) xf msgpack-$(msgpack_VERSION).tar.gz -m

$(MSGPACK_LIB): $(MSGPACK_SRC)
	cd msgpack-$(msgpack_VERSION) && rm -rf build && mkdir -p build && cd build && \
		export PKG_CONFIG_PATH=$(PKG_CONFIG_PATH):$(PKG_CONFIG_EXTRA_DIRS) && \
		cmake -DCMAKE_INSTALL_PREFIX=$(CURDIR)/msgpack -DMSGPACK_CXX11=ON -DMSGPACK_BUILD_EXAMPLES=OFF -DMSGPACK_BUILD_TESTS=OFF .. && \
		$(MAKE) -j $(NCORES) && make install

ifdef MUSCLE_LINUX

msgpack: $(MSGPACK_LIB)

else ifdef MUSCLE_MACOS

msgpack: $(MSGPACK_LIB)
	install_name_tool -id $(CURDIR)/msgpack/lib/libmsgpackc.dylib $(CURDIR)/msgpack/lib/libmsgpackc.dylib

endif

