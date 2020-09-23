.PHONY: all
all: protobuf

.PHONY: install
install: protobuf
	mkdir -p $(PREFIX)/lib
	cp -ra protobuf/* $(PREFIX)/

.PHONY: clean
clean:

.PHONY: distclean
distclean: clean
	rm -f protobuf-cpp-*.tar.gz
	rm -rf $$(find . -type d -name 'protobuf-*')
	rm -rf protobuf

protobuf-cpp-$(protobuf_VERSION).tar.gz:
	$(DOWNLOAD) https://github.com/protocolbuffers/protobuf/releases/download/v$(protobuf_VERSION)/protobuf-cpp-$(protobuf_VERSION).tar.gz

protobuf-$(protobuf_VERSION): protobuf-cpp-$(protobuf_VERSION).tar.gz
	$(TAR) xf protobuf-cpp-$(protobuf_VERSION).tar.gz
	patch -p0 <protobuf_issue_5144.patch

protobuf: protobuf-$(protobuf_VERSION)
	cd protobuf-$(protobuf_VERSION) && ./configure --prefix=$(CURDIR)/protobuf && make -j $(NCORES) && make install

