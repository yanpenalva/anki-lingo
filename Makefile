PYTHON ?= .venv/bin/python

.PHONY: install test lint format-check typecheck quality run config-check

install:
	$(PYTHON) -m pip install -e '.[dev]'

test:
	$(PYTHON) -m pytest

lint:
	$(PYTHON) -m ruff check .

format-check:
	$(PYTHON) -m ruff format --check .

typecheck:
	$(PYTHON) -m mypy

quality: lint format-check typecheck test

run:
	$(PYTHON) -m anki_lingo.interfaces.cli

config-check:
	$(PYTHON) -m anki_lingo.interfaces.cli config-check
