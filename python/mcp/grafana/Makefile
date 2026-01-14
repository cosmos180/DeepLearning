# Makefile for Grafana MCP Server
# Usage: make [target]

.PHONY: all install dev run example help test clean lint

# Variables
PYTHON := python3
VENV := .venv
PIP := $(VENV)/bin/pip
PYTHON_VENV := $(VENV)/bin/python
ACTIVATE := $(VENV)/bin/activate
REQS := requirements.txt
SERVER := server.py
EXAMPLE := example.py
CLIENT := client_example.py
SIMPLE_CLIENT := simple_client.py

# Default target
all: install

## Installation
install:
	$(PYTHON) -m pip install --upgrade pip
	$(PYTHON) -m pip install -r $(REQS)

## Virtual Environment
venv:
	$(PYTHON) -m venv $(VENV)
	$(VENV)/bin/pip install -r $(REQS)

## Run MCP Server
run:
	$(PYTHON_VENV) $(SERVER)

## Run Example
example:
	$(PYTHON_VENV) $(EXAMPLE)

## Show Example Help
example-help:
	$(PYTHON_VENV) $(EXAMPLE) --help

## Run Real Client
client:
	$(PYTHON_VENV) $(CLIENT)

## Show Client Help
client-help:
	$(PYTHON_VENV) $(CLIENT) --help

## Run Simple Client (Direct subprocess approach)
simple-client:
	$(PYTHON_VENV) $(SIMPLE_CLIENT)

## Simple Client - Individual Tests
test-list-tools:
	$(PYTHON_VENV) $(SIMPLE_CLIENT) list-tools

test-list-dashboards:
	$(PYTHON_VENV) $(SIMPLE_CLIENT) list-dashboards 20

test-list-dashboards-folder:
	$(PYTHON_VENV) $(SIMPLE_CLIENT) list-dashboards folder=ipc

test-get-panels:
	$(PYTHON_VENV) $(SIMPLE_CLIENT) get-panels

test-get-panel:
	$(PYTHON_VENV) $(SIMPLE_CLIENT) get-panel 5

test-query-data:
	$(PYTHON_VENV) $(SIMPLE_CLIENT) query-data 6

test-get-alerts:
	$(PYTHON_VENV) $(SIMPLE_CLIENT) get-alerts

test-list-ds:
	$(PYTHON_VENV) $(SIMPLE_CLIENT) list-ds

test-query-es:
	$(PYTHON_VENV) $(SIMPLE_CLIENT) query-es wsnKPH4Nk query='metrics.platform: "sdc"' time_from=now-24h

## Run Tests (if tests exist)
test:
	$(PYTHON_VENV) -m pytest tests/ -v

## Lint code
lint:
	$(PYTHON_VENV) -m flake8 *.py
	$(PYTHON_VENV) -m mypy *.py --ignore-missing-imports

## Format code
fmt:
	$(PYTHON_VENV) -m black *.py

## Clean generated files
clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache .mypy_cache

## Show this help
help:
	@echo "Grafana MCP Server - Available Commands"
	@echo "======================================="
	@echo ""
	@echo "Setup:"
	@echo "  make install      - Install dependencies"
	@echo "  make venv         - Create virtual environment"
	@echo ""
	@echo "Running:"
	@echo "  make run          - Start MCP server"
	@echo "  make simple-client- Run all tests"
	@echo ""
	@echo "Individual Tests:"
	@echo "  make test-list-tools    - List available tools"
	@echo "  make test-list-dashboards - List dashboards"
	@echo "  make test-get-panels    - Get dashboard panels"
	@echo "  make test-get-panel     - Get panel info (id=5)"
	@echo "  make test-query-data    - Query panel data (id=6)"
	@echo "  make test-get-alerts    - Get firing alerts"
	@echo "  make test-list-ds       - List datasources"
	@echo "  make test-query-es      - Query Elasticsearch directly"
	@echo ""
	@echo "Development:"
	@echo "  make test         - Run pytest tests"
	@echo "  make lint         - Lint code"
	@echo "  make fmt          - Format code"
	@echo "  make clean        - Clean cache files"
	@echo ""
	@echo "Configuration (edit in simple_client.py):"
	@echo "  grafana_url      - Grafana server URL"
	@echo "  api_key          - API key for authentication"
	@echo "  dashboard_uid    - Dashboard UID"
	@echo ""
