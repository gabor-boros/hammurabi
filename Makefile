.PHONY: clean clean-test clean-pyc clean-build clean-mypy docs help
.DEFAULT_GOAL := help

define BROWSER_PYSCRIPT
import os, webbrowser, sys

try:
	from urllib import pathname2url
except:
	from urllib.request import pathname2url

webbrowser.open("file://" + pathname2url(os.path.abspath(sys.argv[1])))
endef
export BROWSER_PYSCRIPT

define PRINT_HELP_PYSCRIPT
import re, sys

for line in sys.stdin:
	match = re.match(r'^([a-zA-Z_-]+):.*?## (.*)$$', line)
	if match:
		target, help = match.groups()
		print("%-20s %s" % (target, help))
endef
export PRINT_HELP_PYSCRIPT

BROWSER := python -c "$$BROWSER_PYSCRIPT"

help:
	@python -c "$$PRINT_HELP_PYSCRIPT" < $(MAKEFILE_LIST)

clean: clean-build clean-pyc clean-test clean-mypy ## remove all build, test, coverage and Python artifacts

clean-build: ## remove build artifacts
	rm -fr build/
	rm -fr dist/
	rm -fr .eggs/
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -f {} +

clean-mypy: ## remove mypy related artifacts
	rm -rf .mypy_cache

clean-pyc: ## remove Python file artifacts
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

clean-test: ## remove test and coverage artifacts
	rm -fr .tox/ \
	.coverage \
	htmlcov/ \
	.pytest_cache \
	.hypothesis/

docs: ## generate Sphinx HTML documentation, including API docs
	rm -f docs/hammurabi.rst
	rm -f docs/modules.rst
	poetry export --dev -f requirements.txt > docs/requirements.txt
	sphinx-apidoc -o docs/ hammurabi
	$(MAKE) -C docs clean
	$(MAKE) -C docs html
	$(BROWSER) docs/_build/html/index.html

format: ## run formatters on the package
	isort --apply -rc hammurabi tests
	black hammurabi tests

stubs: ## generate stubs for the package
	stubgen --include-private -o .stubs hammurabi
	black .stubs
	@echo "Do not forget to update stubs! More info: "

lint: format ## run linters against the package
	mypy hammurabi
	bandit -q -r hammurabi
	pylint hammurabi
	flake8 hammurabi --count --ignore=E501 --show-source --statistics

test-unit: ## run unit tests and generate coverage
	coverage run -m pytest -m "not integration" --hypothesis-show-statistics -vv
	coverage report

test-integration: ## run unit tests and generate coverage
	coverage run -m pytest -m "integration" --hypothesis-show-statistics -vv
	coverage report

test: ## run all tests and generate coverage
	coverage run -m pytest --hypothesis-show-statistics -vv
	coverage report

download-test-reporter:
	curl -L https://codeclimate.com/downloads/test-reporter/test-reporter-latest-linux-amd64 > ./cc-test-reporter
	chmod +x ./cc-test-reporter

test-reporter-before:
	./cc-test-reporter before-build
  
upload-coverage:
	coverage xml
	./cc-test-reporter after-build --exit-code $(TRAVIS_TEST_RESULT) -t "coverage.py"
