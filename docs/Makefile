ROOT := ..
VENV := $(ROOT)/.venv
REQUIREMENTS := requirements-docx.txt
TEMPLATE_SCRIPT := $(ROOT)/scripts/create_reference_template.py
EXPORT_SCRIPT := $(ROOT)/scripts/export_docx.py
SYNC_SCRIPT := $(ROOT)/scripts/sync_markdown_code.py
REFERENCE_DOC := $(ROOT)/templates/reference.docx
MANIFEST := $(ROOT)/docs/docx-manifest.json
DOCX_ARGS := --manifest $(MANIFEST) --reference-doc $(REFERENCE_DOC)

ifeq ($(OS),Windows_NT)
PYTHON ?= python
VENV_PYTHON := $(VENV)/Scripts/python.exe
DOCX_WRAPPER := powershell -NoProfile -ExecutionPolicy Bypass -File $(ROOT)/scripts/export-docx.ps1 -PythonExecutable "$(VENV_PYTHON)"
else
PYTHON ?= python3
VENV_PYTHON := $(VENV)/bin/python
DOCX_WRAPPER := $(VENV_PYTHON) $(EXPORT_SCRIPT)
endif

.PHONY: all venv install sync check-sync template docx

all: docx

venv:
	$(PYTHON) -m venv $(VENV)

install: venv
	$(VENV_PYTHON) -m pip install -r $(REQUIREMENTS)

sync:
	$(PYTHON) $(SYNC_SCRIPT)

check-sync:
	$(PYTHON) $(SYNC_SCRIPT) --check

template: install
	$(VENV_PYTHON) $(TEMPLATE_SCRIPT) --output $(REFERENCE_DOC)

docx: sync template
	$(DOCX_WRAPPER) $(DOCX_ARGS)
