python_version := $(word 2, $(shell python3 --version))
not_python_3_5 := $(patsubst 3.5%,,$(python_version))
reqs := $(if $(not_python_3_5), ../requirements.txt, ../requirements_3.5.txt)

.PHONY: all
all: venv


.PHONY: clean
clean:
	rm -rf venv


venv:
	python3 -m venv venv
	. venv/bin/activate && pip3 install -U pip setuptools wheel && pip3 install -r $(reqs) && pip3 install $(CURDIR)/../../../../../
