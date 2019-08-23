.PHONY: all
all: nng

.PHONY: install
ifdef nng_VERSION
install: nng
	mkdir -p $(PREFIX)/lib
	cp -ra nng/lib/* $(PREFIX)/lib/
else
install:
endif

.PHONY: clean
clean:

.PHONY: distclean
distclean: clean
	rm -f v*.tar.gz
	rm -rf $$(find . -type d -name 'nng-*')
	rm -rf nng

v$(nng_VERSION).tar.gz:
	$(DOWNLOAD) https://github.com/nanomsg/nng/archive/v$(nng_VERSION).tar.gz

nng-$(nng_VERSION): v$(nng_VERSION).tar.gz
	$(TAR) xf v$(nng_VERSION).tar.gz

nng: nng-$(nng_VERSION)
	cd nng-$(nng_VERSION) && mkdir build && cd build && cmake -DCMAKE_INSTALL_PREFIX:PATH=$(CURDIR)/nng -DBUILD_SHARED_LIBS=ON -DNNG_TESTS=OFF -DNNG_TOOLS=OFF -DNNG_ENABLE_NNGCAT=OFF -DNNG_ENABLE_COVERAGE=OFF .. && make -j $(NCORES) && make install
