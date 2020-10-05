# Copyright (c) 2019 CloudZero, Inc. All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

FREEZE := pip-freeze.txt
REQUIREMENTS := requirements.txt
SRC := src
TESTS := tests
VIRTUALENV := virtualenv
main = $(shell find $(SRC) -name "main.py")

$(VIRTUALENV):
	python3 -m venv $@
	@printf "\033[1;33mTo activate this virtualenv in your shell, run \033[1;32m'source $(VIRTUALENV)/bin/activate'.\033[0m\n"

.PHONY: init
init: $(FREEZE)
$(FREEZE): $(VIRTUALENV) $(REQUIREMENTS)
	. $(VIRTUALENV)/bin/activate && pip install -r $(REQUIREMENTS)
	@pip freeze > $@

.PHONY: test
test: $(FREEZE)
	. $(VIRTUALENV)/bin/activate && pytest $(SRC) $(TESTS)

.PHONY: run
run: $(main) test
	. $(VIRTUALENV)/bin/activate && python3 -m $(subst .py,,$(subst /,., $(main)))
