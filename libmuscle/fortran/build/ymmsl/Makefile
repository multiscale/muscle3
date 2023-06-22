# Get source paths
srcdir := $(CURDIR)/../../src/ymmsl

sources := $(srcdir)/ymmsl.f90
objects := $(sources:$(srcdir)/%.f90=%.o)
lobjects := $(sources:$(srcdir)/%.f90=%.lo)

ifdef MUSCLE_LINUX

libs := libymmsl_fortran.a libymmsl_fortran.so

else ifdef MUSCLE_MACOS

libs := libymmsl_fortran.a libymmsl_fortran.dylib

endif

modules := $(sources:$(srcdir)/%.f90=%.mod)
pkg_config_files := ymmsl_fortran.pc

installed_sources := $(sources:$(srcdir)/%=$(PREFIX)/include/%)
installed_modules := $(modules:%=$(PREFIX)/include/%)
installed_libs := $(libs:%=$(PREFIX)/lib/%)
installed_pkg_config_files := $(pkg_config_files:%=$(PREFIX)/lib/pkgconfig/%)

LDFLAGS := -L../../../cpp/build/ymmsl -lymmsl

FFLAGS := -O3
ifdef MUSCLE_FC_INTEL
    FFLAGS += -e03
    MOD_DUMP := -module mod_dump
else ifdef MUSCLE_FC_GNU
    FFLAGS += -std=f2003
    MOD_DUMP := -Jmod_dump
else ifdef MUSCLE_FC_CRAY
    FFLAGS += -em -ef
    MOD_DUMP := -Jmod_dump
endif


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

ifdef MUSCLE_LINUX

.PHONY: install
install: $(installed_sources) $(installed_modules) $(installed_libs) $(installed_pkg_config_files)

else ifdef MUSCLE_MACOS

.PHONY: install
install: $(installed_sources) $(installed_modules) $(installed_libs) $(installed_pkg_config_files)
	install_name_tool -id $(PREFIX)/lib/libymmsl_fortran.dylib $(PREFIX)/lib/libymmsl_fortran.dylib
	install_name_tool -change libymmsl.dylib @loader_path/libymmsl.dylib $(PREFIX)/lib/libymmsl_fortran.dylib

endif

%.o: $(srcdir)/%.f90
	$(FC) -c $(FFLAGS) $^ -o $@

%.lo: $(srcdir)/%.f90
	$(FC) -c -fPIC $(MOD_DUMP) $(FFLAGS) $< -o $@

%.mod: %.o

lib%_fortran.a: %.o
	ar rcs $@ $^

lib%_fortran.so: %.lo
	$(FC) -shared -o $@ $^ $(LDFLAGS)

lib%_fortran.dylib: %.lo
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
	@echo 'Description: Partial yMMSL support library for MUSCLE3' >>$@
	@echo 'URL: https://muscle3.readthedocs.io' >>$@
	@echo 'Version: $(muscle_version)' >>$@
	@echo 'Requires.private: ymmsl = $(muscle_version)' >>$@
	@echo 'Cflags: -I$${includedir}' >>$@
	@echo 'Cflags.private: -pthread' >>$@
	@echo 'Libs: -L$${libdir} -lymmsl_fortran' >>$@
	@echo 'Libs.private: -pthread' >>$@

