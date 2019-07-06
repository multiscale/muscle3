# Get source paths
hdrdir := $(CURDIR)/../../src
srcdir := $(CURDIR)/../../src/libmuscle
srcdirs := $(srcdir) $(srcdir)/mcp
objdir := $(CURDIR)/objs

VPATH := $(srcdir)
source_files := $(foreach dir,$(srcdirs),$(wildcard $(dir)/*.cpp))
objects := $(source_files:$(srcdir)%.cpp=$(objdir)%.o)
lobjects := $(source_files:$(srcdir)%.cpp=$(objdir)%.lo)
deps := $(source_files:$(srcdir)%.cpp=$(objdir)%.d)

header_root := $(CURDIR)/../../src
CXXFLAGS += -I$(header_root)

public_headers := libmuscle/operator.hpp
installed_headers := $(public_headers:%=$(PREFIX)/include/%)

CXXFLAGS += -Wall -pedantic -std=c++14
export CXXFLAGS


.PHONY: all
all: libmuscle.a libmuscle.so version.h

.PHONY: tests
tests: libmuscle.a version.h
	$(MAKE) -C tests

.PHONY: clean
clean:
	rm -f libmuscle.a libmuscle.so version.h
	rm -rf $(objdir)
	$(MAKE) -C tests clean

.PHONY: install
install: all $(installed_headers)
	@echo
	@echo Installing libmuscle to $(PREFIX)
	@mkdir -p $(PREFIX)/lib
	cp libmuscle.a $(PREFIX)/lib/
	cp libmuscle.so $(PREFIX)/lib


ifneq ($(MAKECMDGOALS),clean)

# Dependencies
CXXFLAGS += $(shell export PKG_CONFIG_PATH=$(PKG_CONFIG_EXTRA_DIRS) ; pkg-config --cflags protobuf)
CXXFLAGS += $(shell export PKG_CONFIG_PATH=$(PKG_CONFIG_EXTRA_DIRS) ; pkg-config --cflags grpc grpc++)
LDFLAGS += -L$(CURDIR)/../muscle_manager_protocol -lmmp -L$(CURDIR)/../ymmsl -lymmsl
LDFLAGS += $(shell export PKG_CONFIG_PATH=$(PKG_CONFIG_EXTRA_DIRS) ; pkg-config --libs protobuf)
LDFLAGS += $(shell export PKG_CONFIG_PATH=$(PKG_CONFIG_EXTRA_DIRS) ; pkg-config --libs grpc grpc++)

# Automatic header dependencies
-include $(deps)


# Make version.h
version_template := $(srcdir)/version.h.in
version_file := $(CURDIR)/../../../../VERSION
major_version := $(shell sed -e 's/^\([0-9]*\)\..*/\1/' $(version_file))
minor_version := $(shell sed -e 's/^[0-9]*\.\([0-9]*\)\..*/\1/' $(version_file))
patch_version := $(shell sed -e 's/^[0-9]*\.[0-9]*\.\([0-9]*\).*/\1/' $(version_file))

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

version.h: $(version_template) $(version_file)
	cp $(version_template) $@
	sed -i -e 's/@PROJECT_VERSION_MAJOR@/$(major_version)/' $@
	sed -i -e 's/@PROJECT_VERSION_MINOR@/$(minor_version)/' $@
	sed -i -e 's/@PROJECT_VERSION_PATCH@/$(patch_version)/' $@

libmuscle.a: $(objects)
	ar rcs $@ $^

libmuscle.so: $(lobjects)
	$(CXX) -shared -o $@ $^ $(LDFLAGS)

$(PREFIX)/include/%.hpp: $(hdrdir)/%.hpp
	@mkdir -p $(@D)
	cp $< $@

