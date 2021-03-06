.PHONY: docs tests upload-pypi conda-build-35 conda-build-36 conda-build-37

tests:
	pytest

clean:
	python setup.py clean

clean-pyc:
	find . -name '*.pyc' -exec rm {} \;

upload-pypi-test:
	python setup.py sdist bdist_wheel && \
		twine upload --repository-url https://test.pypi.org/legacy/ dist/* && \
		rm -rf dist

upload-pypi:
	python setup.py sdist bdist_wheel && \
		twine upload dist/* && \
		rm -rf dist

requirements:
	pip install -r requirements-dev.txt

docs:
	make -C docs doctest && python -m sphinx -E -W "docs/source" "docs/_build"

mock-ci-tests:
	. ./ci_tests.sh

conda-build: conda-build-35 conda-build-36 conda-build-37

conda-build-35:
	conda-build --python=3.5 conda.recipe

conda-build-36:
	conda-build --python=3.6 conda.recipe

conda-build-37:
	conda-build --python=3.7 conda.recipe
