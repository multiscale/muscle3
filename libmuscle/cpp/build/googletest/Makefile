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
	$(DOWNLOAD) https://github.com/google/googletest/archive/release-$(googletest_VERSION).tar.gz

googletest-release-$(googletest_VERSION): release-$(googletest_VERSION).tar.gz
	$(TAR) xf release-$(googletest_VERSION).tar.gz

googletest: googletest-release-$(googletest_VERSION)
	cd googletest-release-$(googletest_VERSION) && mkdir -p build
	cd googletest-release-$(googletest_VERSION)/build && cmake -DCMAKE_INSTALL_PREFIX=$(CURDIR)/googletest ..
	cd googletest-release-$(googletest_VERSION)/build && $(MAKE) -j $(NCORES) && make install

