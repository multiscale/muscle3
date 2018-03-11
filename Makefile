.PHONY: test
test:
	mypy --strict muscle_manager libmuscle/python
	pytest --cov-report xml --cov-report term --cov --pep8

.PHONY: docs-clean
docs-clean:
	rm -rf docs/source/apidocs/*
	rm -rf docs/build/*

.PHONY: docs
docs:
	sphinx-build -a docs/source/ docs/build
