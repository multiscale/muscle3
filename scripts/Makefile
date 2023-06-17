all:

CXX?=g++
FORTRAN?=gfortran


.PHONY: clean
clean:
	cd tests && $(MAKE) clean

.PHONY: distclean
distclean:
	cd tests && $(MAKE) distclean

ifndef MUSCLE_DISABLE_FORTRAN

.PHONY: test
test:
	cd tests && $(MAKE) test

else

.PHONY: test
test:

endif

