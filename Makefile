.PHONY: test
test:
	mypy --strict muscle_manager libmuscle/python
	pytest --cov-report xml --cov-report term --cov --pep8
