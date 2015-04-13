.PHONY: clean-pyc clean-build docs clean

help:
	@echo "clean - remove all build, test, coverage and Python artifacts"
	@echo "clean-build - remove build artifacts"
	@echo "clean-pyc - remove Python file artifacts"
	@echo "clean-test - remove test and coverage artifacts"
	@echo "lint - check style with pylint"
	@echo "test - run tests quickly with nosetests"
	@echo "test-all - run tests on every Python version with tox"
	@echo "coverage - check code coverage quickly with nosetests"
	@echo "docs - generate Sphinx HTML documentation, including API docs"
	@echo "release - package and upload a release"
	@echo "dist - package"
	@echo "install - install the package to the active Python's site-packages"

clean: clean-build clean-pyc clean-test

clean-build:
	rm -fr build/
	rm -fr dist/
	rm -fr .eggs/
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -f {} +

clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

clean-test:
	rm -fr .tox/
	rm -f .coverage
	rm -fr htmlcov/

lint:
	@if ! which pylint >/dev/null; then echo "pylint not installed.\nRun:\n    pip install pylint" && false; fi
	@if ! which pep8 >/dev/null; then echo "pep8 not installed.\nRun:\n    pip install pep8" && false; fi
	-pep8 pignacio_scripts tests
	pylint pignacio_scripts tests

test: test-deps clean-pyc
	python setup.py nosetests

test-cover: test-deps clean-pyc
	python setup.py nosetests --with-coverage --cover-package=pignacio_scripts

test-all: test-deps clean-pyc
	@if ! which tox >/dev/null; then echo "tox not installed.\nRun:\n    pip install tox" && false; fi
	tox

test-deps:
	pip install -r test_requirements.txt

coverage: test-deps clean-pyc
	coverage run --source pignacio_scripts setup.py nosetests
	make coverage-show

coverage-all:
	coverage erase
	make test-all
	make coverage-show

coverage-show:
	coverage report
	coverage html
	see htmlcov/index.html

docs:
	@if ! which sphinx-apidoc >/dev/null; then echo "sphinx not installed.\nRun:\n    pip install sphinx" && false; fi
	rm -f docs/pignacio_scripts.rst
	rm -f docs/modules.rst
	sphinx-apidoc -o docs/ pignacio_scripts
	$(MAKE) -C docs clean
	$(MAKE) -C docs html
	see docs/_build/html/index.html

release: clean dist-deps
	python setup.py sdist upload
	python setup.py bdist_wheel upload

dist: clean dist-deps
	python setup.py sdist
	python setup.py bdist_wheel
	ls -l dist

dist-deps:
	pip install -r dist_requirements.txt

install: clean
	python setup.py install

yapf:
	find pignacio_scripts -name "*.py" -exec yapf --diff {} +
