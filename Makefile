VENV_DIR = ./.venv
PYTHON = $(VENV_DIR)/bin/python
PYTHON_VERSION = python3.12

TIMESTAMP := $(shell date +%Y_%m_%d__%H_%M_%S)

GREENFONT = \033[0;32m
ERRORFONT = \033[0;33m
RESETFONT = \033[0m

report_dir                    = ./reports/$(TIMESTAMP)
pytest_report_file            = $(report_dir)/test_results/index.html
pytest_report_arg             = --html=$(pytest_report_file)
pytest_coverage_report_folder = $(report_dir)/coverage
pytest_coverage_args          = --cov=src --cov=tests --cov-report html:$(pytest_coverage_report_folder)
pylint_output_location        = ./reports/lint_results.txt
pylint_rc_file                = .pylintrc

# Put 'help' first so this is the default if no target is specified
.SILENT: help
.PHONY: help
help:
	echo "This Makefile provides convenient workflow utilities for devs"
	echo "Targets:"
	echo "    lint: Run Pylint and output to $(live_pylint_file)"
	echo "    smoke: Run smoke tests to check for basic syntax issues"
	echo "    all-tests: Run all Pytest tests and output to $(report_dir)"
	echo "    venv-init: Create a new Python3.12 venv and install requirements"
	echo "    preview-docs: Create local preview of docs as HTML files for checking before a Confluence publish"
	echo "    publish-docs: Publish docs to Confluence page (only automatic docs, most are manually written on Confluence)"

# TODO add more smoke tests!
.PHONY: smoke
smoke: venv-exists
	$(PYTHON) tests/smokes/smoke.py
	echo -e "$(GREENFONT)Success: Completed smoke tests\n$(RESETFONT)"

.PHONY: lint
lint: venv-exists
	mkdir -p reports
	echo "Running linter..."
	$(PYTHON) -m pylint . --rcfile=$(pylint_rc_file) --exit-zero > $(pylint_output_location)
	echo -e "$(GREENFONT)Success: Completed lint.\n$(RESETFONT)"

.PHONY: reports-dir
reports-dir:
	mkdir -p $(report_dir)

.PHONY: all-tests
all-tests: reports-dir venv-exists
	echo -e "Created directory: $(report_dir)\n"
	
	echo "Running Pytests on $(pytest_file_spec) - this may take a moment"
	-$(PYTHON) -m pytest $(pytest_file_spec) $(pytest_coverage_args) $(pytest_report_arg)
	# hyphen here indicates to Make that it's okay if this return nonzero, proceed anyway
	echo -e "$(GREENFONT)Completed pytest run$(RESETFONT)\n"

	# Move symbolic link "HEAD" to new report_dir
	ln -sfn $(TIMESTAMP) ./reports/HEAD
	echo -e "Moved symbolic link ./reports/HEAD to new report directory\n"
	
	echo "Coverage report : $(pytest_coverage_report_folder)/index.html"
	echo "Test results    : $(pytest_report_file)"

# Assert that a venv exists or give an error (prefer not to create the venv automatically as the user may have a preference)
.SILENT: venv-exists
.PHONY:  venv-exists
venv-exists:
	if [ ! -x ".venv/bin/python" ]; then \
	echo "Error: .venv/bin/python does not exist or is not executable. Please 'make venv-init'"; \
	exit 1; \
	fi

.PHONY: venv-init
venv-init:
	echo -e "Creating Python 3.12 venv at $(VENV_DIR)"
	$(PYTHON_VERSION) -m venv $(VENV_DIR)
	echo -e "Installing dependencies for devs..."
	$(PYTHON) -m pip install -r requirements.txt
	echo -e "$(GREENFONT)Completed venv setup and package install.\n$(RESETFONT)"

DOCS_SOURCE_DIR      = docs_gen
DOCS_BUILD_DIR       = docs_gen/_build

## TODO add make targets to build docs

BUILD_VERSION ?=
# Specify which version to build with 'make dist'
# This should be a git tag e.g. "1.0" which will be checked out

.PHONY: dist
dist:
	if [ -n "$(BUILD_VERSION)" ]; then \
		echo "Checking out $(BUILD_VERSION)"; \
		git checkout -q "$(BUILD_VERSION)"; \
	fi

	mkdir -p "dist"

	# If the current commit is tagged, use that as the name. Otherwise, get a tag for the current commit and remove the last nine characters to get a 'post' version name
	if git tag --points-at HEAD | grep -q .; then \
		sed -i "s/^version = \".*\"/version = \"`git describe --tags --always`\"/" pyproject.toml; \
	else \
		echo -e "$(ERRORFONT)This git commit is not tagged. Build will be given version number 0.dev0 $(RESETFONT)"; \
		sed -i "s/^version = \".*\"/version = \"0.dev0\"/" pyproject.toml; \
	fi

	$(PYTHON) -m build | (head -n 3 ; echo -e "\n    hiding extra log messages...\n"; tail -n 3)
	rm -r src/*.egg-info

	if [ -n "$(BUILD_VERSION)" ]; then \
		echo "Returning to previous git commit"; \
		git checkout -q -f @{-1}; \
	fi

.PHONY: clean
clean:            ## Clean artefacts, caches, and temporary files
	find ./ -name '*.pyc' -exec rm -f {} \;
	find ./ -name '__pycache__' -exec rm -rf {} \;
	find ./ -name '*~' -exec rm -f {} \;
	rm -rf .cache
	rm -rf .pytest_cache
	rm -rf .mypy_cache
	rm -rf build
	rm -rf dist
	rm -rf *.egg-info
	rm -rf htmlcov
	rm -rf .tox/
	rm -rf docs/_build