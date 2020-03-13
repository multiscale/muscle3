ifeq "$(filter $(MAKECMDGOALS), clean)" ""
ifndef MUSCLE3_HOME
$(error MUSCLE3_HOME is not defined, use 'MUSCLE3_HOME=/path/to/muscle3 make <target>' to build)
endif
endif

.PHONY: all
all: python cpp fortran

.PHONY: python
python:
	make -C python all

.PHONY: cpp
cpp:
	make -C cpp all

.PHONY: fortran
fortran:
	make -C fortran all

.PHONY: clean
clean:
	make -C cpp clean
	make -C fortran clean
	make -C python clean
	rm -f *.log
