.PHONY: all
all:
	$(MAKE) -C build
	@echo
	@echo 'All done, enjoy MUSCLE 3!'

.PHONY: tests
tests:
	$(MAKE) -C build tests

.PHONY: test
test:
	$(MAKE) -C build test

.PHONY: install
install: all
	$(MAKE) -C build install

.PHONY: clean
clean:
	$(MAKE) -C build clean

.PHONY: distclean
distclean:
	$(MAKE) -C build distclean

