.PHONY: all
all: venv


.PHONY: clean
clean:
	rm -rf venv


venv:
	python3 -m venv venv
	. venv/bin/activate && pip3 install -U pip3 setuptools wheel && pip3 install -r ../requirements.txt && pip3 install $(CURDIR)/../../../../../
