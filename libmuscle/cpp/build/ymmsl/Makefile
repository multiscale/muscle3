PREFIX ?= /usr/local

# Get source paths
hdrdir := $(CURDIR)/../../src
srcdir := $(CURDIR)/../../src/ymmsl
srcdirs := $(srcdir)
objdir := $(CURDIR)/objs

VPATH := $(srcdir)
source_files := $(foreach dir,$(srcdirs),$(wildcard $(dir)/*.cpp))
objects := $(source_files:$(srcdir)%.cpp=$(objdir)%.o)
lobjects := $(source_files:$(srcdir)%.cpp=$(objdir)%.lo)
deps := $(source_files:$(srcdir)%.cpp=$(objdir)%.d)

public_headers := ymmsl/compute_element.hpp
installed_headers := $(public_headers:%=$(PREFIX)/include/%)

CXXFLAGS += -Wall -pedantic -std=c++14 -I$(hdrdir)
export CXXFLAGS


.PHONY: all
all: libymmsl.a libymmsl.so

.PHONY: tests
tests: libymmsl.a
	$(MAKE) -C tests

.PHONY: clean
clean:
	rm -f libymmsl.a libymmsl.so
	rm -rf objs
	$(MAKE) -C tests clean

.PHONY: distclean
distclean: clean
	$(MAKE) -C tests distclean

.PHONY: install
install: all $(installed_headers)
	@echo
	@echo Installing libymmsl to $(PREFIX)
	@mkdir -p $(PREFIX)/lib
	cp libymmsl.a $(PREFIX)/lib/
	cp libymmsl.so $(PREFIX)/lib



-include $(deps)

$(objdir)/%.d: %.cpp
	@mkdir -p $(@D)
	$(CXX) $(CPPFLAGS) $(CXXFLAGS) -E -MM -MT $(@:.d=.o) $< -o $@

$(objdir)/%.o: %.cpp
	@mkdir -p $(@D)
	$(CXX) $(CPPFLAGS) $(CXXFLAGS) -c $< -o $@

$(objdir)/%.lo: %.cpp
	@mkdir -p $(@D)
	$(CXX) $(CPPFLAGS) $(CXXFLAGS) -fPIC -c $< -o $@

libymmsl.a: $(objects)
	ar rcs $@ $^

libymmsl.so: $(lobjects)
	$(CXX) -shared -o $@ $^

$(PREFIX)/include/%.hpp: $(hdrdir)/%.hpp
	@mkdir -p $(@D)
	cp $< $@

