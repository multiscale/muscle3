.PHONY: all
all: installation


.PHONY: clean
clean:
	rm -rf venv


venv:
	python3 -m venv venv

.PHONY: installation
installation: venv
	. venv/bin/activate && pip3 install -U pip setuptools wheel && pip3 install -U -r ../requirements.txt && pip3 install -U $(CURDIR)/../../../../../
