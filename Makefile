.PHONY: test
test:
	pytest --cov-report xml --cov-report term --cov
