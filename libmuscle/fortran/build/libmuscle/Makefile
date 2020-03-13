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


ifdef MUSCLE_ENABLE_MPI
libs += $(mpi_libs)
modules += $(mpi_modules)
endif

installed_modules := $(modules:%=$(PREFIX)/include/%)
installed_libs := $(libs:%=$(PREFIX)/lib/%)

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

%.mo: $(srcdir)/%.f03
	mpi$(FC) -c $(FFLAGS) $^ -o $@ $(LDFLAGS_MPI)

%.mlo: $(srcdir)/%.f03
	mpi$(FC) -c -fPIC -Jmod_dump $(FFLAGS) $^ -o $@ $(LDFLAGS_MPI)

%.mod: %.o

libmuscle_fortran.a: $(objects)
	ar rcs $@ $^

libmuscle_fortran.so: $(lobjects)
	$(FC) -shared -o $@ $^ $(LDFLAGS)

libmuscle_mpi_fortran.a: $(mobjects)
	ar rcs $@ $^

libmuscle_mpi_fortran.so: $(mlobjects)
	mpi$(FC) -shared -o $@ $^ $(LDFLAGS_MPI)

$(PREFIX)/include/%: %
	@mkdir -p $(@D)
	cp $< $@

$(PREFIX)/lib/%: %
	@mkdir -p $(@D)
	cp $< $@
