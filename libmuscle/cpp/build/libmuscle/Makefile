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

ifdef MUSCLE_MACOS
    prod_libs := libmuscle.a libmuscle.dylib
    debug_libs := libmuscle_d.a libmuscle_d.dylib
else
    prod_libs := libmuscle.a libmuscle.so
    debug_libs := libmuscle_d.a libmuscle_d.so
endif

tests_deps := libmuscle_d.a version.h

# if we're compiling with MPI, or we are installing and have MPI libs
ifeq ($(if $(or $(MUSCLE_ENABLE_CPP_MPI),$(and $(findstring install,$(MAKECMDGOALS)),$(wildcard libmuscle_mpi.so))),1,0),1)
    ifdef MUSCLE_MACOS
        prod_libs += libmuscle_mpi.a libmuscle_mpi.dylib
        debug_libs += libmuscle_mpi_d.a libmuscle_mpi_d.dylib
        tests_deps += libmuscle_mpi_d.a
    else
        prod_libs += libmuscle_mpi.a libmuscle_mpi.so
        debug_libs += libmuscle_mpi_d.a libmuscle_mpi_d.so
        tests_deps += libmuscle_mpi_d.a
    endif
endif

all_libs := $(prod_libs)

ifdef MUSCLE_ENABLE_DEBUG
all_libs += $(debug_libs)
endif

header_root := $(CURDIR)/../../src
CXXFLAGS += -I$(header_root)

public_headers := libmuscle/data.hpp libmuscle/data.tpp libmuscle/instance.hpp
public_headers += libmuscle/libmuscle.hpp libmuscle/mcp/data_pack.hpp
public_headers += libmuscle/mcp/data_pack.tpp libmuscle/message.hpp
public_headers += libmuscle/ports_description.hpp libmuscle/util.hpp libmuscle/util.tpp
public_headers += libmuscle/version.h libmuscle/namespace.hpp
installed_headers := $(public_headers:%=$(PREFIX)/include/%)

pkg_config_files := libmuscle.pc

ifeq ($(if $(or $(MUSCLE_ENABLE_CPP_MPI),$(and $(findstring install,$(MAKECMDGOALS)),$(wildcard libmuscle_mpi.so))),1,0),1)
    pkg_config_files += libmuscle_mpi.pc
endif

installed_pkg_config_files := $(pkg_config_files:%=$(PREFIX)/lib/pkgconfig/%)

CXXFLAGS += -Wall -pedantic -std=c++14 -pthread -O3
export CXXFLAGS

MPIFLAGS := -DMUSCLE_ENABLE_MPI
export MPIFLAGS

DEBUGFLAGS += -g -O0
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
	rm -f libmuscle.a libmuscle.so libmuscle_d.a libmuscle_d.so $(srcdir)/version.h
	rm -f libmuscle_mpi.a libmuscle_mpi.so libmuscle_mpi_d.a libmuscle_mpi_d.so
	rm -f libmuscle.pc libmuscle_mpi.pc
	rm -rf $(objdir)
	$(MAKE) -C tests clean

.PHONY: distclean
distclean: clean
	$(MAKE) -C tests distclean

ifdef MUSCLE_LINUX

.PHONY: install
install: all $(installed_headers) $(installed_pkg_config_files)
	@echo
	@echo Installing libmuscle C++ to $(PREFIX)
	@mkdir -p $(PREFIX)/lib
	cp libmuscle*.a $(PREFIX)/lib
	cp libmuscle*.so $(PREFIX)/lib
	@mkdir -p $(PREFIX)/bin
	sed -e 's@%PREFIX%@$(PREFIX)@g' muscle3.env.in >$(PREFIX)/bin/muscle3.env
	for pc in $(PREFIX)/lib/pkgconfig/* ; do sed -i -e 's@^prefix=.*$$@prefix=$(PREFIX)@' $$pc ; done

else ifdef MUSCLE_MACOS

.PHONY: install
install: all $(installed_headers) $(installed_pkg_config_files)
	@echo
	echo Installing libmuscle C++ to $(PREFIX)
	mkdir -p $(PREFIX)/lib
	cp libmuscle*.a $(PREFIX)/lib
	cp libmuscle*.dylib $(PREFIX)/lib
	for lib in $(PREFIX)/lib/*.dylib ; do install_name_tool -id $$lib $$lib ; done
	install_name_tool -change libymmsl.dylib @loader_path/libymmsl.dylib $(PREFIX)/lib/libmuscle.dylib
	-install_name_tool -change libymmsl.dylib @loader_path/libymmsl.dylib $(PREFIX)/lib/libmuscle_d.dylib
	-install_name_tool -change libymmsl.dylib @loader_path/libymmsl.dylib $(PREFIX)/lib/libmuscle_mpi.dylib
	-install_name_tool -change libymmsl.dylib @loader_path/libymmsl.dylib $(PREFIX)/lib/libmuscle_mpi_d.dylib
	install_name_tool -change @rpath/libmsgpackc.2.dylib @loader_path/libmsgpackc.2.dylib $(PREFIX)/lib/libmuscle.dylib
	-install_name_tool -change @rpath/libmsgpackc.2.dylib @loader_path/libmsgpackc.2.dylib $(PREFIX)/lib/libmuscle_d.dylib
	-install_name_tool -change @rpath/libmsgpackc.2.dylib @loader_path/libmsgpackc.2.dylib $(PREFIX)/lib/libmuscle_mpi.dylib
	-install_name_tool -change @rpath/libmsgpackc.2.dylib @loader_path/libmsgpackc.2.dylib $(PREFIX)/lib/libmuscle_mpi_d.dylib
	@mkdir -p $(PREFIX)/bin
	sed -e 's@%PREFIX%@$(PREFIX)@g' muscle3.env.in >$(PREFIX)/bin/muscle3.env
	for pc in $(PREFIX)/lib/pkgconfig/* ; do sed -i -e 's@^prefix=.*$$@prefix=$(PREFIX)@' $$pc ; done

endif


cleantargets := clean distclean
ifeq "$(filter $(MAKECMDGOALS),$(cleantargets))" ""

# Dependencies
$(info pcextra: $(PKG_CONFIG_EXTRA_DIRS))
CXXFLAGS += $(shell export PKG_CONFIG_PATH=$(PKG_CONFIG_PATH):$(PKG_CONFIG_EXTRA_DIRS) ; pkg-config --cflags msgpack)

LDFLAGS += -pthread -L$(CURDIR)/../ymmsl -lymmsl
LDFLAGS += $(shell export PKG_CONFIG_PATH=$(PKG_CONFIG_PATH):$(PKG_CONFIG_EXTRA_DIRS) ; pkg-config --libs msgpack)

# Automatic header dependencies
-include $(deps)


endif


$(objdir)/%.d: %.cpp $(srcdir)/version.h
	@mkdir -p $(@D)
	$(CXX) $(CPPFLAGS) $(CXXFLAGS) -E -MM -MT $(@:.d=.o) $< -o $@

$(objdir)/%.o: %.cpp $(srcdir)/version.h
	@mkdir -p $(@D)
	$(CXX) $(CPPFLAGS) $(CXXFLAGS) -c $< -o $@

# depends on .o to daisy-chain automatic dependencies
$(objdir)/%.lo: %.cpp $(objdir)/%.o
	@mkdir -p $(@D)
	$(CXX) $(CPPFLAGS) $(CXXFLAGS) -fPIC -c $< -o $@

# depends on .o to daisy-chain automatic dependencies
$(objdir)/%.do: %.cpp $(objdir)/%.o
	@mkdir -p $(@D)
	$(CXX) $(CPPFLAGS) $(CXXFLAGS) $(DEBUGFLAGS) -c $< -o $@

# depends on .o to daisy-chain automatic dependencies
$(objdir)/%.dlo: %.cpp $(objdir)/%.o
	@mkdir -p $(@D)
	$(CXX) $(CPPFLAGS) $(CXXFLAGS) $(DEBUGFLAGS) -fPIC -c $< -o $@

$(objdir)/%.mo: %.cpp $(srcdir)/version.h
	@mkdir -p $(@D)
	$(MPICXX) $(CPPFLAGS) $(CXXFLAGS) $(MPIFLAGS) -c $< -o $@

$(objdir)/%.mlo: %.cpp $(srcdir)/version.h
	@mkdir -p $(@D)
	$(MPICXX) $(CPPFLAGS) $(CXXFLAGS) $(MPIFLAGS) -fPIC -c $< -o $@

$(objdir)/%.mdo: %.cpp $(srcdir)/version.h
	@mkdir -p $(@D)
	$(MPICXX) $(CPPFLAGS) $(CXXFLAGS) $(DEBUGFLAGS) $(MPIFLAGS) -c $< -o $@

$(objdir)/%.mdlo: %.cpp $(srcdir)/version.h
	@mkdir -p $(@D)
	$(MPICXX) $(CPPFLAGS) $(CXXFLAGS) $(DEBUGFLAGS) $(MPIFLAGS) -fPIC -c $< -o $@


$(srcdir)/version.h: version.h.in
	cp $< $@
	sed -i -e 's/@PROJECT_VERSION_MAJOR@/$(major_version)/' $@
	sed -i -e 's/@PROJECT_VERSION_MINOR@/$(minor_version)/' $@
	sed -i -e 's/@PROJECT_VERSION_PATCH@/$(patch_version)/' $@
	sed -i -e 's/@PROJECT_VERSION@/$(muscle_version)/' $@

libmuscle.a: $(objects)
	ar rcs $@ $^

libmuscle.so: $(lobjects)
	$(CXX) -shared -Wl,--version-script=libmuscle.version -o $@ $^ $(LDFLAGS)

libmuscle.dylib: $(lobjects)
	$(CXX) -shared -o $@ $^ $(LDFLAGS)

libmuscle_d.a: $(dobjects)
	ar rcs $@ $^

libmuscle_d.so: $(dlobjects)
	$(CXX) -shared -Wl,--version-script=libmuscle.version -o $@ $^ $(LDFLAGS)

libmuscle_d.dylib: $(dlobjects)
	$(CXX) -shared -o $@ $^ $(LDFLAGS)

libmuscle_mpi.a: $(mobjects)
	ar rcs $@ $^

libmuscle_mpi.so: $(mlobjects)
	$(MPICXX) -shared -Wl,--version-script=libmuscle_mpi.version -o $@ $^ $(LDFLAGS)

libmuscle_mpi.dylib: $(mlobjects)
	$(MPICXX) -shared -o $@ $^ $(LDFLAGS)

libmuscle_mpi_d.a: $(mdobjects)
	ar rcs $@ $^

libmuscle_mpi_d.so: $(mdlobjects)
	$(MPICXX) -shared -Wl,--version-script=libmuscle_mpi.version -o $@ $^ $(LDFLAGS)

libmuscle_mpi_d.dylib: $(mdlobjects)
	$(MPICXX) -shared -o $@ $^ $(LDFLAGS)

$(PREFIX)/include/libmuscle/version.h: $(srcdir)/version.h
	@mkdir -p $(@D)
	cp $< $@

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
	@echo 'Description: Library for MUSCLE3' >>$@
	@echo 'URL: https://muscle3.readthedocs.io' >>$@
	@echo 'Version: $(muscle_version)' >>$@
	@echo 'Requires: ymmsl = $(muscle_version)' >>$@
	@echo 'Requires.private: msgpack >= 3.1.0' >>$@
	@echo 'Cflags: -I$${includedir} -pthread' >>$@
	@echo 'Cflags.private: -pthread' >>$@
	@echo 'Libs: -L$${libdir} -lmuscle' >>$@
	@echo 'Libs.private: -pthread' >>$@

libmuscle_mpi.pc:
	@echo 'prefix=$(PREFIX)' >$@
	@echo 'exec_prefix=$${prefix}' >>$@
	@echo 'includedir=$${prefix}/include' >>$@
	@echo 'libdir=$${exec_prefix}/lib' >>$@
	@echo >>$@
	@echo 'Name: libmuscle for C++ and MPI' >>$@
	@echo 'Description: Library for MUSCLE3' >>$@
	@echo 'URL: https://muscle3.readthedocs.io' >>$@
	@echo 'Version: $(muscle_version)' >>$@
	@echo 'Requires: ymmsl = $(muscle_version)' >>$@
	@echo 'Requires.private: msgpack >= 3.1.0' >>$@
	@echo 'Cflags: -I$${includedir} -pthread -DMUSCLE_ENABLE_MPI' >>$@
	@echo 'Cflags.private: -pthread' >>$@
	@echo 'Libs: -L$${libdir} -lmuscle_mpi' >>$@
	@echo 'Libs.private: -pthread' >>$@
