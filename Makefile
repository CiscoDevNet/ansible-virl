# Makefile
include envfile
PYTHON_EXE = python3
TOPDIR = $(shell git rev-parse --show-toplevel)
PYDIRS="ansible"
SRC_FILES := $(shell find ansible -name \*.py)
VENV = venv_ansible_virl
VENV_BIN=$(VENV)/bin

help: ## Display help
	@awk -F ':|##' \
	'/^[^\t].+?:.*?##/ {\
	printf "\033[36m%-30s\033[0m %s\n", $$1, $$NF \
	}' $(MAKEFILE_LIST)

all: clean venv_ansible_virl check test dist ## Setup ansible-virl env and run tests

venv: ## Creates the needed virtual environment.
	test -d $(VENV) || virtualenv -p $(PYTHON_EXE) $(VENV) $(ARGS)

$(VENV): $(VENV_BIN)/activate ## Build virtual environment

$(VENV_BIN)/activate: requirements.txt test-requirements.txt
	test -d $(VENV) || virtualenv -p $(PYTHON_EXE) $(VENV)
	echo "export TOP_DIR=$(TOPDIR)" >> $(VENV_BIN)/activate
	. $(VENV_BIN)/activate; pip install -U pip; pip install -r requirements.txt -r test-requirements.txt

deps: venv ## Installs the needed dependencies into the virtual environment.
	$(VENV_BIN)/pip install -U pip
	$(VENV_BIN)/pip install -r requirements.txt -r test-requirements.txt

dev: deps ## Installs ansible_virl in develop mode.
	$(VENV_BIN)/pip install -e ./

check-format: $(VENV)/bin/activate ## Check code format
	@( \
	set -eu pipefail ; set -x ;\
	DIFF=`$(VENV)/bin/yapf --style=yapf.ini -d -r *.py $(PYDIRS)` ;\
	if [ -n "$$DIFF" ] ;\
	then \
	echo -e "\nFormatting changes requested:\n" ;\
	echo "$$DIFF" ;\
	echo -e "\nRun 'make format' to automatically make changes.\n" ;\
	exit 1 ;\
	fi ;\
	)

format: $(VENV_BIN)/activate ## Format code
	$(VENV_BIN)/yapf --style=yapf.ini -i -r *.py $(PYDIRS)

pylint: $(VENV_BIN)/activate ## Run pylint
	$(VENV_BIN)/pylint --output-format=parseable --rcfile .pylintrc *.py $(SRC_FILES)

check: check-format pylint ## Check code format & lint

build: deps ## Builds EGG info and project documentation.
	$(VENV_BIN)/python setup.py egg_info

dist: build ## Creates the distribution.
	$(VENV_BIN)/python setup.py sdist --formats gztar
	$(VENV_BIN)/python setup.py bdist_wheel

dist-clean: ## Creates the distribution.
	$(VENV_BIN)/python setup.py clean --all

test: deps ## Run ansible-virl tests
	. $(VENV_BIN)/activate; pip install -U pip; pip install -r requirements.txt -r test-requirements.txt;tox -r

clean: ## Clean ansible-virl $(VENV)
	$(RM) -rf $(VENV)
	$(RM) -rf docs/_build
	$(RM) -rf dist
	$(RM) -rf *.egg-info
	$(RM) -rf *.eggs
	$(RM) -rf docs/api/*
	find . -name "*.pyc" -exec $(RM) -rf {} \;

clean-docs-html:
	$(RM) -rf docs/build/html
clean-docs-markdown:
	$(RM) -rf docs/build/markdown

apidocs: docs/source/modules.rst ## regenerate API documention sources

docs/source/modules.rst: $(SRC_FILES)  $(VENV)/bin/activate
	$(VENV_BIN)/sphinx-apidoc -M -fo docs/api . $(NON_PYTHON_LIBS)

docs: docs-markdown docs-html ## Generate documentation in HTML and Markdown

docs-markdown: clean-docs-markdown $(SPHINX_DEPS) $(VENV)/bin/activate ## Generate Markdown documentation
	. $(VENV_BIN)/activate ; $(MAKE) -C docs markdown
docs-html: clean-docs-html $(SPHINX_DEPS) $(VENV)/bin/activate ## Generate HTML documentation
	. $(VENV_BIN)/activate ; $(MAKE) -C docs html

docs-clean: ## Clean generated documentation
	$(MAKE) -C docs clean


.PHONY: all clean $(VENV) test check format check-format pylint clean-docs-html clean-docs-markdown apidocs
