.PHONY: all
all: googletest

.PHONY: clean
clean:
	rm -rf googletest-release-*
	rm -rf googletest

.PHONY: distclean
distclean: clean
	rm -f release-*.tar.gz


release-$(googletest_VERSION).tar.gz:
	$(DOWNLOAD) https://github.com/google/googletest/releases/download/v$(googletest_VERSION)/googletest-$(googletest_VERSION).tar.gz
	mv googletest-$(googletest_VERSION).tar.gz release-$(googletest_VERSION).tar.gz

googletest-release-$(googletest_VERSION): release-$(googletest_VERSION).tar.gz
	$(TAR) xf release-$(googletest_VERSION).tar.gz

googletest: release-$(googletest_VERSION).tar.gz
	tar xf release-$(googletest_VERSION).tar.gz
	cd googletest-$(googletest_VERSION) && mkdir -p build
	cd googletest-$(googletest_VERSION)/build && cmake -DCMAKE_INSTALL_PREFIX=$(CURDIR)/googletest ..
	cd googletest-$(googletest_VERSION)/build && $(MAKE) -j $(NCORES) && make install
