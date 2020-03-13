.PHONY: all
all: venv


.PHONY: clean
clean:
	rm -rf venv


venv:
	python3 -m venv venv
	. venv/bin/activate && pip3 install -r ../requirements.txt
