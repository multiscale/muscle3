.PHONY: all
all: zlib

.PHONY: install
install: zlib
	mkdir -p $(PREFIX)/lib
	cp -ra zlib/lib/* $(PREFIX)/lib/

.PHONY: clean
clean:

.PHONY: distclean
distclean: clean
	rm -f zlib-*.tar.gz
	rm -rf $$(find -type d -name 'zlib-*')
	rm -rf zlib

zlib-$(zlib_VERSION).tar.gz:
	$(DOWNLOAD) https://www.zlib.net/zlib-$(zlib_VERSION).tar.gz

zlib-$(zlib_VERSION): zlib-$(zlib_VERSION).tar.gz
	$(TAR) xf zlib-$(zlib_VERSION).tar.gz

zlib: zlib-$(zlib_VERSION)
	cd zlib-$(zlib_VERSION) && ./configure --prefix=$(CURDIR)/zlib && make -j $(NCORES) && make install

