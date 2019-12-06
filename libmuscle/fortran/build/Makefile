.PHONY: all
all: ymmsl libmuscle

.PHONY: test
test: tests
	# $(MAKE) -C ymmsl test
	$(MAKE) -C libmuscle test

.PHONY: install
install: all
	# $(MAKE) -C ymmsl install
	$(MAKE) -C libmuscle install

.PHONY: clean
clean:
	# $(MAKE) -C ymmsl clean
	$(MAKE) -C libmuscle clean

.PHONY: distclean
distclean:
	# $(MAKE) -C ymmsl distclean
	$(MAKE) -C libmuscle distclean


.PHONY: ymmsl
ymmsl:
	# $(MAKE) -j $(NCORES) -C ymmsl


.PHONY: libmuscle
libmuscle:
	$(MAKE) -j $(NCORES) -C libmuscle


.PHONY: tests
tests: ymmsl libmuscle
	$(MAKE) -j $(NCORES) -C ymmsl tests
	$(MAKE) -j $(NCORES) -C libmuscle tests
