# Get source paths
srcdir := $(CURDIR)/../../src/ymmsl

sources := $(srcdir)/ymmsl.f03
objects := $(sources:$(srcdir)/%.f03=%.o)
libs := libymmsl_fortran.a libymmsl_fortran.so
modules := $(sources:$(srcdir)/%.f03=%.mod)

installed_modules := $(modules:%=$(PREFIX)/include/%)
installed_libs := $(libs:%=$(PREFIX)/lib/%)

LDFLAGS := -L../../../cpp/build/ymmsl -lymmsl
FFLAGS := -std=f2003

.PHONY: all
all: ymmsl

.PHONY: ymmsl
ymmsl: $(libs)

.PHONY: tests
tests:

.PHONY: test
test: tests

.PHONY: clean
clean:
	rm -f $(objects) $(modules) $(libs)

.PHONY: distclean
distclean: clean
	rm -f $(objects) $(modules) $(libs)

.PHONY: install
install: $(installed_modules) $(installed_libs)

%.o: $(srcdir)/%.f03
	$(FC) -c $(FFLAGS) $^ -o $@ $(LDFLAGS)

%.mod: %.o

lib%_fortran.a: %.o
	ar rcs $@ $^

lib%_fortran.so: %.o
	$(FC) -shared -o $@ $^ $(LDFLAGS)

$(PREFIX)/include/%: %
	@mkdir -p $(@D)
	cp $< $@

$(PREFIX)/lib/%: %
	@mkdir -p $(@D)
	cp $< $@
