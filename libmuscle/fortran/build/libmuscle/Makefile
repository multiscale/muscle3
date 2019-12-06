# Get source paths
hdrdir := $(CURDIR)/../../src
public_modules := libmuscle/libmuscle.f03
installed_modules := $(public_modules:%=$(PREFIX)/include/%)

.PHONY: all
all:

.PHONY: tests
tests:
	$(MAKE) -C tests tests

.PHONY: test
test: tests
	$(MAKE) -C tests test

.PHONY: clean
clean:
	$(MAKE) -C tests clean

.PHONY: distclean
distclean: clean
	$(MAKE) -C tests distclean

.PHONY: install
install: $(installed_modules)

$(PREFIX)/include/%.f03: $(hdrdir)/%.f03
	@mkdir -p $(@D)
	cp $< $@
