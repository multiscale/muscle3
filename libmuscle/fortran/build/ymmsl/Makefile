# Get source paths
srcdir := $(CURDIR)/../../src/ymmsl

sources := $(srcdir)/ymmsl.f90
objects := $(sources:$(srcdir)/%.f90=%.o)
lobjects := $(sources:$(srcdir)/%.f90=%.lo)
libs := libymmsl_fortran.a libymmsl_fortran.so
modules := $(sources:$(srcdir)/%.f90=%.mod)
pkg_config_files := ymmsl_fortran.pc

installed_sources := $(sources:$(srcdir)/%=$(PREFIX)/include/%)
installed_modules := $(modules:%=$(PREFIX)/include/%)
installed_libs := $(libs:%=$(PREFIX)/lib/%)
installed_pkg_config_files := $(pkg_config_files:%=$(PREFIX)/lib/pkgconfig/%)

LDFLAGS := -L../../../cpp/build/ymmsl -lymmsl
FFLAGS := -std=f2003 -O3

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
	rm -f $(objects) $(modules) $(libs) $(pkg_config_files)
	rm -f mod_dump/*.mod

.PHONY: distclean
distclean: clean

.PHONY: install
install: $(installed_sources) $(installed_modules) $(installed_libs) $(installed_pkg_config_files)

%.o: $(srcdir)/%.f90
	$(FC) -c $(FFLAGS) $^ -o $@ $(LDFLAGS)

%.lo: $(srcdir)/%.f90
	$(FC) -c -fPIC -Jmod_dump $(FFLAGS) $< -o $@ $(LDFLAGS)

%.mod: %.o

lib%_fortran.a: %.o
	ar rcs $@ $^

lib%_fortran.so: %.lo
	$(FC) -shared -o $@ $^ $(LDFLAGS)

$(PREFIX)/include/%.f90: $(srcdir)/%.f90
	@mkdir -p $(@D)
	cp $< $@

$(PREFIX)/include/%: %
	@mkdir -p $(@D)
	cp $< $@

$(PREFIX)/lib/%: %
	@mkdir -p $(@D)
	cp $< $@

$(PREFIX)/lib/pkgconfig/%: %
	@mkdir -p $(@D)
	cp $< $@

ymmsl_fortran.pc:
	@echo 'prefix=$(PREFIX)' >$@
	@echo 'exec_prefix=$${prefix}' >>$@
	@echo 'includedir=$${prefix}/include' >>$@
	@echo 'libdir=$${exec_prefix}/lib' >>$@
	@echo >>$@
	@echo 'Name: yMMSL for Fortran' >>$@
	@echo 'Description: Partial yMMSL support library for MUSCLE 3' >>$@
	@echo 'URL: https://muscle3.readthedocs.io' >>$@
	@echo 'Version: $(muscle_version)' >>$@
	@echo 'Requires.private: ymmsl = $(muscle_version)' >>$@
	@echo 'Cflags: -I$${includedir}' >>$@
	@echo 'Libs: -L$${libdir} -lymmsl_fortran' >>$@

