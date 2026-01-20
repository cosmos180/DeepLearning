# Makefile for Grafana MCP Server
# Usage: make [target]

.PHONY: all install dev run example help test clean lint monitoring

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
MONITORING_DIR := monitoring
ELASTALERT_DIR := /opt/elastalert

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

## Interactive Explorer
explore:
	$(PYTHON_VENV) $(SIMPLE_CLIENT) explore

explore-ipc:
	$(PYTHON_VENV) $(SIMPLE_CLIENT) explore folder=ipc limit=100

explore-all:
	$(PYTHON_VENV) $(SIMPLE_CLIENT) explore limit=200

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

## Monitoring - Install ElastAlert
monitor-install:
	sudo $(MONITORING_DIR)/scripts/install_elastalert.sh

## Monitoring - Validate rules
monitor-validate:
	$(PYTHON) $(MONITORING_DIR)/scripts/validate_rules.py --rules-dir $(MONITORING_DIR)/elastalert_rules

## Monitoring - Deploy rules
monitor-deploy:
	sudo $(MONITORING_DIR)/scripts/deploy_rules.sh

## Monitoring - Test a rule (usage: make monitor-test RULE=path/to/rule.yaml)
monitor-test:
	$(MONITORING_DIR)/scripts/elastalert2.sh test $(RULE)

## Monitoring - Run ElastAlert2 service
monitor-run:
	$(MONITORING_DIR)/scripts/elastalert2.sh run

## Monitoring - Run ElastAlert2 in verbose mode
monitor-run-verbose:
	$(MONITORING_DIR)/scripts/elastalert2.sh run verbose

## Monitoring - Create ElastAlert index
monitor-create-index:
	$(MONITORING_DIR)/scripts/elastalert2.sh create-index

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
	@echo "Interactive Explorer:"
	@echo "  make explore            - Interactive dashboard explorer"
	@echo "  make explore-ipc        - Explore dashboards in 'ipc' folder"
	@echo "  make explore-all        - Explore all dashboards (limit=200)"
	@echo ""
	@echo "Monitoring (ElastAlert2):"
	@echo "  make monitor-create-index - Create ElastAlert index"
	@echo "  make monitor-test RULE   - Test a specific rule"
	@echo "  make monitor-run         - Start ElastAlert2 service"
	@echo "  make monitor-run-verbose - Start with verbose output"
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
