PREFIX ?= /usr/local

# Get source paths
hdrdir := $(CURDIR)/../../src
srcdir := $(CURDIR)/../../src/muscle_manager_protocol

VPATH := $(srcdir)
source_files := $(wildcard $(srcdir)/*.cc)
objects := $(source_files:$(srcdir)/%.cc=%.o)

CXXFLAGS += -std=c++14 -I$(hdrdir) -fPIC
CXXFLAGS += $(shell export PKG_CONFIG_PATH=$(PKG_CONFIG_PATH):$(PKG_CONFIG_EXTRA_DIRS) ; pkg-config --cflags protobuf)
CXXFLAGS += $(shell export PKG_CONFIG_PATH=$(PKG_CONFIG_PATH):$(PKG_CONFIG_EXTRA_DIRS) ; pkg-config --cflags grpc)


.PHONY: all
all: libmmp.a

.PHONY: clean
clean:
	rm -f libmmp.a
	rm -f *.o

.PHONY: distclean
distclean: clean


%.o: %.cc *.h
	@mkdir -p $(@D)
	$(CXX) $(CPPFLAGS) $(CXXFLAGS) -c $< -o $@

libmmp.a: $(objects)
	ar rcs $@ $^

