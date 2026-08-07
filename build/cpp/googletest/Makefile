.PHONY: all
all: googletest

.PHONY: clean
clean:
	rm -rf googletest-*
	rm -rf googletest

.PHONY: distclean
distclean: clean
	rm -f googletest-*.tar.gz


googletest-$(googletest_VERSION).tar.gz:
	$(DOWNLOAD) https://github.com/google/googletest/releases/download/v$(googletest_VERSION)/googletest-$(googletest_VERSION).tar.gz

googletest-release-$(googletest_VERSION): googletest-$(googletest_VERSION).tar.gz
	$(TAR) xf googletest-$(googletest_VERSION).tar.gz

googletest: googletest-release-$(googletest_VERSION)
	cd googletest-$(googletest_VERSION) && mkdir -p build
	cd googletest-$(googletest_VERSION)/build && cmake -DCMAKE_INSTALL_PREFIX=$(CURDIR)/googletest ..
	cd googletest-$(googletest_VERSION)/build && $(MAKE) -j $(NCORES) && make install