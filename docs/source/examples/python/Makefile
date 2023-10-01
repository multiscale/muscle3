.PHONY: all
all:
	$(MAKE) -C build all

.PHONY: test
test:
	. build/venv/bin/activate && DONTPLOT=1 python3 reaction_diffusion.py
	. build/venv/bin/activate && DONTPLOT=1 python3 reaction_diffusion_qmc.py
	. build/venv/bin/activate && DONTPLOT=1 python3 interact_coupling.py
	. build/venv/bin/activate && DONTPLOT=1 python3 dispatch.py

.PHONY: clean
clean:
	$(MAKE) -C build clean
	rm -f *.log
