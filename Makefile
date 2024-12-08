.PHONY: contrib quality style test


check_dirs := src utils setup.py


quality:
	ruff check $(check_dirs)  # linter
	ruff format --check $(check_dirs) # formatter
	python utils/check_static_imports.py
	mypy src  # type checker

style:
	ruff format $(check_dirs) # formatter
	ruff check --fix $(check_dirs) # linter
	python utils/check_static_imports.py --update

clean:
	rm -rf build/* dist/* 

# You can set these variables from the command line, and also
# from the environment for the first two.
SPHINXOPTS    ?=
SPHINXBUILD   ?= sphinx-build
SPHINXPYAPIDOC ?= sphinx-apidoc
SOURCEDIR     = docs
BUILDDIR      = docs/_build
PYSOURCEDIR   = src/wisemodel_hub

# Put it first so that "make" without argument is like "make help".
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

.PHONY: help Makefile

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
#apidoc:
#	@$(SPHINXPYAPIDOC) -o source "$(PYSOURCEDIR)" 

%: Makefile
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)