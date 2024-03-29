PREFIX ?= /usr/local

# Get source paths
hdrdir := $(CURDIR)/../../src
srcdir := $(CURDIR)/../../src/ymmsl
srcdirs := $(srcdir) $(srcdir)/bindings
objdir := $(CURDIR)/objs

VPATH := $(srcdir)
source_files := $(foreach dir,$(srcdirs),$(wildcard $(dir)/*.cpp))
objects := $(source_files:$(srcdir)%.cpp=$(objdir)%.o)
lobjects := $(source_files:$(srcdir)%.cpp=$(objdir)%.lo)
dobjects := $(source_files:$(srcdir)%.cpp=$(objdir)%.do)
dlobjects := $(source_files:$(srcdir)%.cpp=$(objdir)%.dlo)
deps := $(source_files:$(srcdir)%.cpp=$(objdir)%.d)

public_headers := ymmsl/component.hpp ymmsl/identity.hpp ymmsl/model.hpp
public_headers += ymmsl/settings.hpp ymmsl/settings.tpp ymmsl/ymmsl.hpp
installed_headers := $(public_headers:%=$(PREFIX)/include/%)

libs := libymmsl.a libymmsl_d.a
ifdef MUSCLE_LINUX
    libs += libymmsl.so libymmsl_d.so
else ifdef MUSCLE_MACOS
    libs += libymmsl.dylib libymmsl_d.dylib
endif

pkg_config_files := ymmsl.pc
installed_pkg_config_files := $(pkg_config_files:%=$(PREFIX)/lib/pkgconfig/%)

CXXFLAGS += -Wall -pedantic -std=c++14 -O3 -I$(hdrdir)
export CXXFLAGS
DEBUGFLAGS += -g -O0
export DEBUGFLAGS


.PHONY: all
all: $(libs)

.PHONY: tests
tests: libymmsl.a
	$(MAKE) -C tests tests

.PHONY: test
test:
	$(MAKE) -C tests test

.PHONY: clean
clean:
	rm -f $(libs)
	rm -f $(pkg_config_files)
	rm -rf objs
	$(MAKE) -C tests clean

.PHONY: distclean
distclean: clean
	$(MAKE) -C tests distclean

ifdef MUSCLE_LINUX

.PHONY: install
install: all $(installed_headers) $(installed_pkg_config_files)
	@echo
	@echo Installing libymmsl to $(PREFIX)
	@mkdir -p $(PREFIX)/lib
	cp $(libs) $(PREFIX)/lib
	for pc in $(PREFIX)/lib/pkgconfig/* ; do sed -i -e 's@^prefix=.*$$@prefix=$(PREFIX)@' $$pc ; done

else ifdef MUSCLE_MACOS

.PHONY: install
install: all $(installed_headers) $(installed_pkg_config_files)
	@echo
	@echo Installing libymmsl to $(PREFIX)
	@mkdir -p $(PREFIX)/lib
	cp $(libs) $(PREFIX)/lib
	for lib in $(PREFIX)/lib/*.dylib ; do install_name_tool -id $$lib $$lib ; done
	for pc in $(PREFIX)/lib/pkgconfig/* ; do sed -i -e 's@^prefix=.*$$@prefix=$(PREFIX)@' $$pc ; done

endif


cleantargets := clean distclean
ifeq "$(filter $(MAKECMDGOALS),$(cleantargets))" ""

-include $(deps)

endif

$(objdir)/%.d: %.cpp
	@mkdir -p $(@D)
	$(CXX) $(CPPFLAGS) $(CXXFLAGS) -E -MM -MT $(@:.d=.o) $< -o $@

$(objdir)/%.o: %.cpp
	@mkdir -p $(@D)
	$(CXX) $(CPPFLAGS) $(CXXFLAGS) -c $< -o $@

$(objdir)/%.lo: %.cpp
	@mkdir -p $(@D)
	$(CXX) $(CPPFLAGS) $(CXXFLAGS) -fPIC -c $< -o $@

$(objdir)/%.do: %.cpp
	@mkdir -p $(@D)
	$(CXX) $(CPPFLAGS) $(CXXFLAGS) $(DEBUGFLAGS) -c $< -o $@

$(objdir)/%.dlo: %.cpp
	@mkdir -p $(@D)
	$(CXX) $(CPPFLAGS) $(CXXFLAGS) $(DEBUGFLAGS) -fPIC -c $< -o $@

libymmsl.a: $(objects)
	ar rcs $@ $^

libymmsl.so: $(lobjects)
	$(CXX) -shared -o $@ $^ $(LDFLAGS)

libymmsl.dylib: $(lobjects)
	$(CXX) -shared -o $@ $^ $(LDFLAGS)

libymmsl_d.a: $(dobjects)
	ar rcs $@ $^

libymmsl_d.so: $(dlobjects)
	$(CXX) -shared -o $@ $^ $(LDFLAGS)

libymmsl_d.dylib: $(dlobjects)
	$(CXX) -shared -o $@ $^ $(LDFLAGS)

$(PREFIX)/include/%.hpp: $(hdrdir)/%.hpp
	@mkdir -p $(@D)
	cp $< $@

$(PREFIX)/include/%.tpp: $(hdrdir)/%.tpp
	@mkdir -p $(@D)
	cp $< $@

$(PREFIX)/lib/pkgconfig/%.pc: %.pc
	@mkdir -p $(@D)
	cp $< $@

ymmsl.pc:
	@echo 'prefix=$(PREFIX)' >$@
	@echo 'exec_prefix=$${prefix}' >>$@
	@echo 'includedir=$${prefix}/include' >>$@
	@echo 'libdir=$${exec_prefix}/lib' >>$@
	@echo >>$@
	@echo 'Name: yMMSL for C++' >>$@
	@echo 'Description: Partial yMMSL support library for MUSCLE3' >>$@
	@echo 'URL: https://muscle3.readthedocs.io' >>$@
	@echo 'Version: $(muscle_version)' >>$@
	@echo 'Cflags: -I$${includedir}' >>$@
	@echo 'Cflags.private: -pthread' >>$@
	@echo 'Libs: -L$${libdir} -lymmsl' >>$@
	@echo 'Libs.private: -pthread' >>$@
