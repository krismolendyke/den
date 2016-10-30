COVERAGE         := coverage
COVERAGE_RC      := coveragerc
FIND             := find
PIP              := pip
PROSPECTOR       := prospector
PROSPECTOR_FLAGS := --profile-path prospector.yaml --no-external-config
PYTHON           := python
RM               := rm
RM_FLAGS         := -rf
SETUP            := setup.py
YAPF             := yapf
YAPF_FLAGS       := --verify --in-place

build_dir := build
dist_dir  := dist
test_dir  := tests

python_src = $(shell $(FIND) . -type f -name '*.py' -not -path './docs/*')

help:
	@$(MAKE) --print-data-base --question no-such-target | \
	grep -v -e '^no-such-target' -e '^Makefile'	     | \
	awk '/^[^.%][-A-Za-z0-9_]*:/ \
	     { print substr($$1, 1, length($$1)-1) }'        | \
	sort					             | \
	pr -2 -t

init:
	$(PIP) install --editable .

init-dev:
	$(PIP) install --editable .[dev] --editable .[doc] --editable .[notebook] --editable .[test]

test:
	PYTHONPATH=. $(COVERAGE) run --source=den $(test_dir)/test_den.py

coverage: test
	$(COVERAGE) report -m

analyze:
	$(PROSPECTOR) $(PROSPECTOR_FLAGS)

format:
	$(YAPF) $(YAPF_FLAGS) $(python_src)

register:
	$(PYTHON) $(SETUP) register

source:
	$(PYTHON) $(SETUP) sdist

egg:
	$(PYTHON) $(SETUP) bdist_egg

wheel:
	$(PYTHON) $(SETUP) bdist_wheel

upload:
	$(PYTHON) $(SETUP) sdist bdist_egg upload

clean:
	$(RM) $(RM_FLAGS) $(build_dir) $(dist_dir) *.egg-info

.PHONY: help init init-dev test analyze format register source egg wheel upload clean
