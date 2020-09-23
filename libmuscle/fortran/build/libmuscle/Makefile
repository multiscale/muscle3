# Get source paths
srcdir := $(CURDIR)/../../src/libmuscle

sources := $(srcdir)/libmuscle.f03
mpi_sources := $(srcdir)/libmuscle_mpi.f03
objects := $(sources:$(srcdir)/%.f03=%.o)
lobjects := $(sources:$(srcdir)/%.f03=%.lo)
mobjects := $(mpi_sources:$(srcdir)/%.f03=%.mo)
mlobjects := $(mpi_sources:$(srcdir)/%.f03=%.mlo)
libs := libmuscle_fortran.a libmuscle_fortran.so
mpi_libs := libmuscle_mpi_fortran.a libmuscle_mpi_fortran.so
modules := $(sources:$(srcdir)/%.f03=%.mod)
mpi_modules := $(mpi_sources:$(srcdir)/%.f03=%.mod)
pkg_config_files := libmuscle_fortran.pc

ifeq ($(if $(or $(MUSCLE_ENABLE_MPI),$(and $(findstring install,$(MAKECMDGOALS)),$(wildcard libmuscle_mpi_fortran.so))),1,0),1)
    libs += $(mpi_libs)
    sources += $(mpi_sources)
    modules += $(mpi_modules)
    pkg_config_files += libmuscle_mpi_fortran.pc
endif

installed_modules := $(modules:%=$(PREFIX)/include/%)
installed_sources := $(sources:$(srcdir)/%=$(PREFIX)/include/%)
installed_pkg_config_files := $(pkg_config_files:%=$(PREFIX)/lib/pkgconfig/%)


LDFLAGS := -L../ymmsl -lymmsl_fortran
LDFLAGS += -L../../../cpp/build/libmuscle -lmuscle
LDFLAGS += -L../../../cpp/build/ymmsl -lymmsl

LDFLAGS_MPI := -L../ymmsl -lymmsl_fortran
LDFLAGS_MPI += -L../../../cpp/build/libmuscle -lmuscle_mpi
LDFLAGS_MPI += -L../../../cpp/build/ymmsl -lymmsl

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
	rm -f *.o *.lo *.mo *.mlo *.mod *.a *.so
	rm -f mod_dump/*.mod
	rm -f libmuscle_fortran.pc libmuscle_mpi_fortran.pc
	make -C tests clean

.PHONY: distclean
distclean: clean
	rm -f $(objects) $(modules) $(libs)
	make -C tests distclean

.PHONY: install
install: $(installed_sources) $(installed_modules) $(installed_pkg_config_files)
	@echo
	@echo Installing libmuscle Fortran to $(PREFIX)
	@mkdir -p $(PREFIX)/lib
	cp libmuscle*.a $(PREFIX)/lib
	cp libmuscle*.so $(PREFIX)/lib

%.o: $(srcdir)/%.f03
	$(FC) -c $(FFLAGS) $^ -o $@ $(LDFLAGS)

%.lo: $(srcdir)/%.f03
	$(FC) -c -fPIC -Jmod_dump $(FFLAGS) $^ -o $@ $(LDFLAGS)

%.mo: $(srcdir)/%.f03
	$(MPIFC) -c $(FFLAGS) $^ -o $@ $(LDFLAGS_MPI)

%.mlo: $(srcdir)/%.f03
	$(MPIFC) -c -fPIC -Jmod_dump $(FFLAGS) $^ -o $@ $(LDFLAGS_MPI)

%.mod: %.o

libmuscle_fortran.a: $(objects)
	ar rcs $@ $^

libmuscle_fortran.so: $(lobjects)
	$(FC) -shared -o $@ $^ $(LDFLAGS)

libmuscle_mpi_fortran.a: $(mobjects)
	ar rcs $@ $^

libmuscle_mpi_fortran.so: $(mlobjects)
	$(MPIFC) -shared -o $@ $^ $(LDFLAGS_MPI)

$(PREFIX)/include/%.f03: $(srcdir)/%.f03
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

libmuscle_fortran.pc:
	@echo 'prefix=$(PREFIX)' >$@
	@echo 'exec_prefix=$${prefix}' >>$@
	@echo 'includedir=$${prefix}/include' >>$@
	@echo 'libdir=$${exec_prefix}/lib' >>$@
	@echo >>$@
	@echo 'Name: libmuscle for Fortran' >>$@
	@echo 'Description: Library for MUSCLE 3 - Fortran version' >>$@
	@echo 'URL: https://muscle3.readthedocs.io' >>$@
	@echo 'Version: $(muscle_version)' >>$@
	@echo 'Requires: ymmsl_fortran = $(muscle_version)' >>$@
	@echo 'Requires.private: libmuscle = $(muscle_version)' >>$@
	@echo 'Cflags: -I$${includedir}' >>$@
	@echo 'Libs: -L$${libdir} -lmuscle_fortran' >>$@

libmuscle_mpi_fortran.pc:
	@echo 'prefix=$(PREFIX)' >$@
	@echo 'exec_prefix=$${prefix}' >>$@
	@echo 'includedir=$${prefix}/include' >>$@
	@echo 'libdir=$${exec_prefix}/lib' >>$@
	@echo >>$@
	@echo 'Name: libmuscle for Fortran and MPI' >>$@
	@echo 'Description: Library for MUSCLE 3 - Fortran-MPI version' >>$@
	@echo 'URL: https://muscle3.readthedocs.io' >>$@
	@echo 'Version: $(muscle_version)' >>$@
	@echo 'Requires: ymmsl_fortran = $(muscle_version)' >>$@
	@echo 'Requires.private: libmuscle_mpi = $(muscle_version)' >>$@
	@echo 'Cflags: -I$${includedir}' >>$@
	@echo 'Libs: -L$${libdir} -lmuscle_mpi_fortran' >>$@

