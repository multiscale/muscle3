ifeq "$(filter $(MAKECMDGOALS), clean)" ""
ifndef MUSCLE3_HOME
$(error MUSCLE3_HOME is not defined, use 'MUSCLE3_HOME=/path/to/muscle3 make <target>' to build)
endif
endif

export PKG_CONFIG_PATH := $(MUSCLE3_HOME)/lib/pkgconfig:$(PKG_CONFIG_PATH)

.PHONY: all
all: python cpp fortran

.PHONY: test
test: all
	./reaction_diffusion_cpp.sh
	./reaction_diffusion_fortran.sh
	./reaction_diffusion_mc_cpp.sh
	./reaction_diffusion_mc_fortran.sh
	./reaction_diffusion_python_cpp.sh
	./reaction_diffusion_python_fortran.sh

.PHONY: test_mpi
test_mpi: all
	./reaction_diffusion_mpi_cpp.sh
	./reaction_diffusion_mpi_fortran.sh

ifdef MUSCLE_ENABLE_MPI
test: test_mpi
endif

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
