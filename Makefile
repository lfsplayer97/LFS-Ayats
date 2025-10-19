.PHONY: lint lint-flake8 lint-pylint lint-mypy lint-bandit

lint: lint-flake8 lint-pylint lint-mypy lint-bandit

lint-flake8:
	flake8 src tests

lint-pylint:
	pylint src

lint-mypy:
	mypy src

lint-bandit:
	bandit -c bandit.yaml -r src
