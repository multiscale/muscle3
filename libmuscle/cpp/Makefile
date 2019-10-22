.PHONY: all
all:
	$(MAKE) -C build
	@echo
	@echo '    All done, now you can install MUSCLE 3 using:'
	@echo
	@echo '        PREFIX=/path/to/install make install'
	@echo

.PHONY: tests
tests:
	$(MAKE) -C build tests

.PHONY: test
test:
	$(MAKE) -C build test

.PHONY: install
install: all
	$(MAKE) -C build install
	@echo
	@echo '*******************************************************************'
	@echo '*                                                                 *'
	@echo "    MUSCLE 3 is now installed in $(PREFIX)."
	@echo '*                                                                 *'
	@echo '*   To compile your model against it, add the following option    *'
	@echo '*   to your compiler command line:                                *'
	@echo '*                                                                 *'
	@echo "        -I$(PREFIX)/include"
	@echo '*                                                                 *'
	@echo '*   If your submodel uses MPI, you must add                       *'
	@echo '*                                                                 *'
	@echo '*       -DMUSCLE_ENABLE_MPI                                       *'
	@echo '*                                                                 *'
	@echo '*   as well.                                                      *'
	@echo '*                                                                 *'
	@echo '*   For linking, add this:                                        *'
	@echo '*                                                                 *'
	@echo "        -L$(PREFIX)/lib -lymmsl -lmuscle"
	@echo '*                                                                 *'
	@echo '*   To link a submodel that uses MPI, you need to link to the     *'
	@echo '*   MPI version of libmuscle instead:                             *'
	@echo '*                                                                 *'
	@echo "        -L$(PREFIX)/lib -lymmsl -lmuscle_mpi"
	@echo '*                                                                 *'
	@echo '*   If the directory you installed MUSCLE 3 in is not in your     *'
	@echo "*   system's library search path, then you have to set            *"
	@echo '*   LD_LIBRARY_PATH before compiling, linking or running:         *'
	@echo '*                                                                 *'
	@echo "       export LD_LIBRARY_PATH=\$$LD_LIBRARY_PATH:$(PREFIX)/lib"
	@echo '*                                                                 *'
	@echo '*******************************************************************'

.PHONY: clean
clean:
	$(MAKE) -C build clean

.PHONY: distclean
distclean:
	$(MAKE) -C build distclean

