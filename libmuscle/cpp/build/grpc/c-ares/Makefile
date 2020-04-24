.PHONY: all
all: c-ares

.PHONY: install
install: c-ares
	mkdir -p $(PREFIX)/lib
	cp -ra c-ares/lib/* $(PREFIX)/lib/

.PHONY: clean
clean:

.PHONY: distclean
distclean: clean
	rm -f c-ares-*.tar.gz
	rm -rf $$(find . -type d -name 'c-ares-*')
	rm -rf c-ares


c-ares-$(c-ares_VERSION).tar.gz:
	$(DOWNLOAD) https://c-ares.haxx.se/download/c-ares-$(c-ares_VERSION).tar.gz

c-ares-$(c-ares_VERSION): c-ares-$(c-ares_VERSION).tar.gz
	$(TAR) xf c-ares-$(c-ares_VERSION).tar.gz

c-ares: c-ares-$(c-ares_VERSION)
	cd c-ares-$(c-ares_VERSION) && ./configure --prefix=$(CURDIR)/c-ares && make -j $(NCORES) && make install

