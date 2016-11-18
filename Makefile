FIND             := find
PIP              := pip
PROSPECTOR       := prospector
PROSPECTOR_FLAGS := --profile-path prospector.yaml --no-external-config
PYTHON           := python
RM               := rm
RM_FLAGS         := -rf
SETUP            := setup.py
TOX              := tox
TOX_DIR          := .tox
YAPF             := yapf
YAPF_FLAGS       := --verify --in-place

build_dir := build
dist_dir  := dist
test_dir  := tests

python_src = $(shell $(FIND) . -type f -name '*.py' \
                 -not -path './build/*'             \
                 -not -path './docs/*'              \
                 -not -path './.eggs/*'             \
                 -not -path './.tox/*'              \
              )

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
	@$(TOX)

analyze:
	$(PROSPECTOR) $(PROSPECTOR_FLAGS)

format:
	$(YAPF) $(YAPF_FLAGS) $(python_src)

source:
	$(PYTHON) $(SETUP) sdist

wheel:
	$(PYTHON) $(SETUP) bdist_wheel

clean:
	$(RM) $(RM_FLAGS) $(build_dir) $(dist_dir) $(TOX_DIR) *.egg-info .eggs

.PHONY: help init init-dev test analyze format source wheel clean
