.PHONY: all
all: msgpack

.PHONY: install
install: msgpack
	mkdir -p $(PREFIX)/include
	cp -a msgpack/include/* $(PREFIX)/include/

.PHONY: clean
clean:

.PHONY: distclean
distclean: clean
	rm -f msgpack-*.tar.gz
	rm -rf $$(find . -type d -name 'msgpack-*')
	rm -rf msgpack

MSGPACK_HEADERS=$(CURDIR)/msgpack/include/msgpack.hpp
MSGPACK_SRC=$(CURDIR)/msgpack-cxx-$(msgpack_VERSION)/ChangeLog

msgpack-cxx-$(msgpack_VERSION).tar.gz:
	$(DOWNLOAD) https://github.com/msgpack/msgpack-c/releases/download/cpp-$(msgpack_VERSION)/msgpack-cxx-$(msgpack_VERSION).tar.gz

$(MSGPACK_SRC): msgpack-cxx-$(msgpack_VERSION).tar.gz
	$(TAR) xf msgpack-cxx-$(msgpack_VERSION).tar.gz -m

$(MSGPACK_HEADERS): $(MSGPACK_SRC)
	cd msgpack-cxx-$(msgpack_VERSION) && rm -rf build && mkdir -p build && cd build && \
		cmake -DCMAKE_POLICY_VERSION_MINIMUM=3.5 -DMSGPACK_USE_BOOST=OFF -DCMAKE_INSTALL_PREFIX=$(CURDIR)/msgpack -DMSGPACK_CXX11=ON -DMSGPACK_BUILD_EXAMPLES=OFF -DMSGPACK_BUILD_TESTS=OFF .. && \
		$(MAKE) -j $(NCORES) && make install && touch $@

msgpack: $(MSGPACK_HEADERS)

