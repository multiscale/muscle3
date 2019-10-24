.PHONY: all
all: openssl

.PHONY: install
ifdef openssl_VERSION
install: openssl
	mkdir -p $(PREFIX)/lib
	cp -ra openssl/lib/* $(PREFIX)/lib/
else
install:
endif

.PHONY: clean
clean:

.PHONY: distclean
distclean: clean
	rm -f openssl-*.tar.gz
	rm -rf $$(find -type d -name 'openssl-*')
	rm -rf openssl

openssl-$(openssl_VERSION).tar.gz:
	$(DOWNLOAD) https://www.openssl.org/source/openssl-$(openssl_VERSION).tar.gz

openssl-$(openssl_VERSION): openssl-$(openssl_VERSION).tar.gz
	$(TAR) xf openssl-$(openssl_VERSION).tar.gz

# OpenSSL keeps rebuilding, because the install seems to modify the source dir
# after creating the target. So we're doing an order-only dependency here,
# since we're not going to change OpenSSL.
openssl: | openssl-$(openssl_VERSION)
	cd openssl-$(openssl_VERSION) && ./config --prefix=$(CURDIR)/openssl && make -j $(NCORES) && make install

