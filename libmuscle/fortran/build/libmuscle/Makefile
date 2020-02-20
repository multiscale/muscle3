# Get source paths
srcdir := $(CURDIR)/../../src/libmuscle

sources := $(srcdir)/libmuscle.f03
objects := $(sources:$(srcdir)/%.f03=%.o)
lobjects := $(sources:$(srcdir)/%.f03=%.lo)
libs := libmuscle_fortran.a libmuscle_fortran.so
modules := $(sources:$(srcdir)/%.f03=%.mod)

installed_modules := $(modules:%=$(PREFIX)/include/%)
installed_libs := $(libs:%=$(PREFIX)/lib/%)

LDFLAGS := -L../ymmsl -lymmsl_fortran
LDFLAGS += -L ../../../cpp/build/libmuscle -lmuscle
LDFLAGS += -L../../../cpp/build/ymmsl -lymmsl

FFLAGS := -std=f2003 -I../ymmsl

.PHONY: all
all: libmuscle

.PHONY: libmuscle
libmuscle: $(libs)

.PHONY: tests
tests:
	make -C tests tests

.PHONY: test
test: tests
	make -C tests test

.PHONY: clean
clean:
	rm -f $(objects) $(modules) $(libs)
	rm -f mod_dump/*.mod
	make -C tests clean

.PHONY: distclean
distclean: clean
	rm -f $(objects) $(modules) $(libs)
	make -C tests distclean

.PHONY: install
install: $(installed_modules) $(installed_libs)

%.o: $(srcdir)/%.f03
	$(FC) -c $(FFLAGS) $^ -o $@ $(LDFLAGS)

%.lo: $(srcdir)/%.f03
	$(FC) -c -fPIC -Jmod_dump $(FFLAGS) $^ -o $@ $(LDFLAGS)

%.mod: %.o

libmuscle_fortran.a: $(objects)
	ar rcs $@ $^

libmuscle_fortran.so: $(lobjects)
	$(FC) -shared -o $@ $^ $(LDFLAGS)

$(PREFIX)/include/%: %
	@mkdir -p $(@D)
	cp $< $@

$(PREFIX)/lib/%: %
	@mkdir -p $(@D)
	cp $< $@
