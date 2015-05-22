COVERAGE         := coverage
COVERAGE_RC      := coveragerc
PIP              := pip
PROSPECTOR       := prospector
PROSPECTOR_FLAGS := --profile-path prospector.yaml --no-external-config
PYTHON           := python
RM               := rm
RM_FLAGS         := -rf
SETUP            := setup.py
YAPF             := yapf
YAPF_FLAGS       := --recursive --verify --in-place

build_dir := build
dist_dir  := dist

help:
	@$(MAKE) --print-data-base --question no-such-target | \
	grep -v -e '^no-such-target' -e '^Makefile'	     | \
	awk '/^[^.%][-A-Za-z0-9_]*:/ \
	     { print substr($$1, 1, length($$1)-1) }'        | \
	sort					             | \
	pr -2 -t

init:
	$(PIP) install --requirement requirements.txt

init-test:
	$(PIP) install --requirement requirements-test.txt

test:
	$(COVERAGE) run --source=den test_den.py

coverage: test
	$(COVERAGE) report -m

analyze:
	$(PROSPECTOR) $(PROSPECTOR_FLAGS)

format:
	$(YAPF) $(YAPF_FLAGS) den *.py

register:
	$(PYTHON) $(SETUP) register

source:
	$(PYTHON) $(SETUP) sdist

egg:
	$(PYTHON) $(SETUP) bdist_egg

upload:
	$(PYTHON) $(SETUP) sdist bdist_egg upload

clean:
	$(RM) $(RM_FLAGS) $(build_dir) $(dist_dir) *.egg-info

.PHONY: help init init-test test analyze format register source egg upload clean
