# Get source paths
hdrdir := $(CURDIR)/../../src
srcdir := $(CURDIR)/../../src/libmuscle
srcdirs := $(srcdir) $(srcdir)/mcp
objdir := $(CURDIR)/objs

VPATH := $(srcdir)
source_files := $(foreach dir,$(srcdirs),$(wildcard $(dir)/*.cpp))
source_files += $(srcdir)/bindings/cmdlineargs.cpp
mpi_source_files := $(source_files) $(srcdir)/bindings/libmuscle_mpi_fortran_c.cpp
source_files := $(source_files) $(srcdir)/bindings/libmuscle_fortran_c.cpp

objects := $(source_files:$(srcdir)%.cpp=$(objdir)%.o)
lobjects := $(source_files:$(srcdir)%.cpp=$(objdir)%.lo)
dobjects := $(source_files:$(srcdir)%.cpp=$(objdir)%.do)
dlobjects := $(source_files:$(srcdir)%.cpp=$(objdir)%.dlo)
mobjects := $(mpi_source_files:$(srcdir)%.cpp=$(objdir)%.mo)
mlobjects := $(mpi_source_files:$(srcdir)%.cpp=$(objdir)%.mlo)
mdobjects := $(mpi_source_files:$(srcdir)%.cpp=$(objdir)%.mdo)
mdlobjects := $(mpi_source_files:$(srcdir)%.cpp=$(objdir)%.mdlo)

deps := $(source_files:$(srcdir)%.cpp=$(objdir)%.d)

prod_libs := libmuscle.a libmuscle.so
debug_libs := libmuscle_d.a libmuscle_d.so

tests_deps := libmuscle_d.a version.h

ifeq ($(if $(or $(MUSCLE_ENABLE_MPI),$(and $(findstring install,$(MAKECMDGOALS)),$(wildcard libmuscle_mpi.so))),1,0),1)
prod_libs += libmuscle_mpi.a libmuscle_mpi.so
debug_libs += libmuscle_mpi_d.a libmuscle_mpi_d.so
tests_deps += libmuscle_mpi_d.a
endif

all_libs := $(prod_libs)

ifdef MUSCLE_ENABLE_DEBUG
all_libs += $(debug_libs)
endif

header_root := $(CURDIR)/../../src
CXXFLAGS += -I$(header_root)

public_headers := libmuscle/data.hpp libmuscle/data.tpp libmuscle/instance.hpp
public_headers += libmuscle/libmuscle.hpp libmuscle/message.hpp
public_headers += libmuscle/ports_description.hpp libmuscle/util.hpp libmuscle/util.tpp
installed_headers := $(public_headers:%=$(PREFIX)/include/%)

pkg_config_files := libmuscle.pc

ifeq ($(if $(or $(MUSCLE_ENABLE_MPI),$(and $(findstring install,$(MAKECMDGOALS)),$(wildcard libmuscle_mpi.so))),1,0),1)
    pkg_config_files += libmuscle_mpi.pc
endif

installed_pkg_config_files := $(pkg_config_files:%=$(PREFIX)/lib/pkgconfig/%)

CXXFLAGS += -Wall -pedantic -std=c++14 -pthread
export CXXFLAGS
MPIFLAGS := -DMUSCLE_ENABLE_MPI
export MPIFLAGS
DEBUGFLAGS := -g
export DEBUGFLAGS


.PHONY: all
all: $(all_libs) version.h

.PHONY: tests
tests: $(tests_deps)
	$(MAKE) -C tests tests

.PHONY: test
test: tests
	$(MAKE) -C tests test

.PHONY: clean
clean:
	rm -f libmuscle.a libmuscle.so libmuscle_d.a libmuscle_d.so version.h
	rm -f libmuscle_mpi.a libmuscle_mpi.so libmuscle_mpi_d.a libmuscle_mpi_d.so
	rm -f libmuscle.pc libmuscle_mpi.pc
	rm -rf $(objdir)
	$(MAKE) -C tests clean

.PHONY: distclean
distclean: clean
	$(MAKE) -C tests distclean

.PHONY: install
install: all $(installed_headers) $(installed_pkg_config_files)
	@echo
	@echo Installing libmuscle C++ to $(PREFIX)
	@mkdir -p $(PREFIX)/lib
	cp libmuscle*.a $(PREFIX)/lib
	cp libmuscle*.so $(PREFIX)/lib
	for pc in $(PREFIX)/lib/pkgconfig/* ; do sed -i -e 's@^prefix=.*$$@prefix=$(PREFIX)@' $$pc ; done



cleantargets := clean distclean
ifeq "$(filter $(MAKECMDGOALS),$(cleantargets))" ""

# Dependencies
$(info pcextra: $(PKG_CONFIG_EXTRA_DIRS))
CXXFLAGS += $(shell export PKG_CONFIG_PATH=$(PKG_CONFIG_EXTRA_DIRS) ; pkg-config --cflags protobuf)
CXXFLAGS += $(shell export PKG_CONFIG_PATH=$(PKG_CONFIG_EXTRA_DIRS) ; pkg-config --cflags grpc++)
CXXFLAGS += $(shell export PKG_CONFIG_PATH=$(PKG_CONFIG_EXTRA_DIRS) ; pkg-config --cflags msgpack)

LDFLAGS += -L$(CURDIR)/../muscle_manager_protocol -lmmp -L$(CURDIR)/../ymmsl -lymmsl
LDFLAGS += $(shell export PKG_CONFIG_PATH=$(PKG_CONFIG_EXTRA_DIRS) ; pkg-config --libs protobuf)
LDFLAGS += $(shell export PKG_CONFIG_PATH=$(PKG_CONFIG_EXTRA_DIRS) ; pkg-config --libs grpc++)
LDFLAGS += $(shell export PKG_CONFIG_PATH=$(PKG_CONFIG_EXTRA_DIRS) ; pkg-config --libs msgpack)

# Automatic header dependencies
-include $(deps)


endif


$(objdir)/%.d: %.cpp
	@mkdir -p $(@D)
	$(CXX) $(CPPFLAGS) $(CXXFLAGS) -E -MM -MT $(@:.d=.o) $< -o $@

$(objdir)/%.o: %.cpp
	@mkdir -p $(@D)
	$(CXX) $(CPPFLAGS) $(CXXFLAGS) -c $< -o $@

# depends on .o to daisy-chain automatic dependencies
$(objdir)/%.lo: %.cpp $(objdir)/%.o
	@mkdir -p $(@D)
	$(CXX) $(CPPFLAGS) $(CXXFLAGS) -fPIC -c $< -o $@

# depends on .o to daisy-chain automatic dependencies
$(objdir)/%.do: %.cpp $(objdir)/%.o
	@mkdir -p $(@D)
	$(CXX) $(CPPFLAGS) $(DEBUGFLAGS) $(CXXFLAGS) -c $< -o $@

# depends on .o to daisy-chain automatic dependencies
$(objdir)/%.dlo: %.cpp $(objdir)/%.o
	@mkdir -p $(@D)
	$(CXX) $(CPPFLAGS) $(DEBUGFLAGS) $(CXXFLAGS) -fPIC -c $< -o $@

$(objdir)/%.mo: %.cpp
	@mkdir -p $(@D)
	$(MPICXX) $(CPPFLAGS) $(CXXFLAGS) $(MPIFLAGS) -c $< -o $@

$(objdir)/%.mlo: %.cpp
	@mkdir -p $(@D)
	$(MPICXX) $(CPPFLAGS) $(CXXFLAGS) $(MPIFLAGS) -fPIC -c $< -o $@

$(objdir)/%.mdo: %.cpp
	@mkdir -p $(@D)
	$(MPICXX) $(CPPFLAGS) $(DEBUGFLAGS) $(CXXFLAGS) $(MPIFLAGS) -c $< -o $@

$(objdir)/%.mdlo: %.cpp
	@mkdir -p $(@D)
	$(MPICXX) $(CPPFLAGS) $(DEBUGFLAGS) $(CXXFLAGS) $(MPIFLAGS) -fPIC -c $< -o $@


version.h: version.h.in
	cp $< $@
	sed -i -e 's/@PROJECT_VERSION_MAJOR@/$(major_version)/' $@
	sed -i -e 's/@PROJECT_VERSION_MINOR@/$(minor_version)/' $@
	sed -i -e 's/@PROJECT_VERSION_PATCH@/$(patch_version)/' $@

libmuscle.a: $(objects)
	ar rcs $@ $^

libmuscle.so: $(lobjects)
	$(CXX) -shared -Wl,--version-script=libmuscle.version -o $@ $^ $(LDFLAGS)

libmuscle_d.a: $(dobjects)
	ar rcs $@ $^

libmuscle_d.so: $(dlobjects)
	$(CXX) -shared -Wl,--version-script=libmuscle.version -o $@ $^ $(LDFLAGS)

libmuscle_mpi.a: $(mobjects)
	ar rcs $@ $^

libmuscle_mpi.so: $(mlobjects)
	$(MPICXX) -shared -Wl,--version-script=libmuscle_mpi.version -o $@ $^ $(LDFLAGS)

libmuscle_mpi_d.a: $(mdobjects)
	ar rcs $@ $^

libmuscle_mpi_d.so: $(mdlobjects)
	$(MPICXX) -shared -Wl,--version-script=libmuscle_mpi.version -o $@ $^ $(LDFLAGS)

$(PREFIX)/include/%.hpp: $(hdrdir)/%.hpp
	@mkdir -p $(@D)
	cp $< $@

$(PREFIX)/include/%.tpp: $(hdrdir)/%.tpp
	@mkdir -p $(@D)
	cp $< $@

$(PREFIX)/lib/pkgconfig/%.pc: %.pc
	@mkdir -p $(@D)
	cp $< $@

libmuscle.pc:
	@echo 'prefix=$(PREFIX)' >$@
	@echo 'exec_prefix=$${prefix}' >>$@
	@echo 'includedir=$${prefix}/include' >>$@
	@echo 'libdir=$${exec_prefix}/lib' >>$@
	@echo >>$@
	@echo 'Name: libmuscle for C++' >>$@
	@echo 'Description: Library for MUSCLE 3' >>$@
	@echo 'URL: https://muscle3.readthedocs.io' >>$@
	@echo 'Version: $(muscle_version)' >>$@
	@echo 'Requires.private: grpc++ >= 1.24.3, protobuf >= 3.10.0, msgpack >= 3.1.0' >>$@
	@echo 'Cflags: -I$${includedir}' >>$@
	@echo 'Libs: -L$${libdir} -lymmsl -lmuscle' >>$@

libmuscle_mpi.pc:
	@echo 'prefix=$(PREFIX)' >$@
	@echo 'exec_prefix=$${prefix}' >>$@
	@echo 'includedir=$${prefix}/include' >>$@
	@echo 'libdir=$${exec_prefix}/lib' >>$@
	@echo >>$@
	@echo 'Name: libmuscle for C++ and MPI' >>$@
	@echo 'Description: Library for MUSCLE 3' >>$@
	@echo 'URL: https://muscle3.readthedocs.io' >>$@
	@echo 'Version: $(muscle_version)' >>$@
	@echo 'Requires.private: grpc++ >= 1.24.3, protobuf >= 3.10.0, msgpack >= 3.1.0' >>$@
	@echo 'Cflags: -I$${includedir} -DMUSCLE_ENABLE_MPI' >>$@
	@echo 'Libs: -L$${libdir} -lymmsl -lmuscle_mpi' >>$@

