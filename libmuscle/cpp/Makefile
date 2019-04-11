.PHONY: all
all: make

build:
	mkdir build

.PHONY: configure
configure: build
	cd build && cmake ..
	cd build && ccmake ..

.PHONY: make
make: build
	cd build && cmake ..
	cd build && cmake --build .

.PHONY: install
install: make
	cd build && cmake --build . --target install

.PHONY: test
test: make
	cd build && cmake --build . --target test

.PHONY: clean
clean:
	cd build && cmake --build . --target clean

.PHONY: distclean
distclean:
	rm -rf build
