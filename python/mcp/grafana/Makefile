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

## Elasticsearch Direct Query (脱开 Grafana，直接查询 ES)
es-query:
	$(PYTHON_VENV) monitoring/scripts/es_query.py '(metrics.platform: "sdc") AND (metrics.cache_info.json)' --aggregate

es-query-sdc:
	$(PYTHON_VENV) monitoring/scripts/es_query.py 'metrics.platform: "sdc"' --time-from "now-24h" --aggregate

es-query-explain:
	$(PYTHON_VENV) monitoring/scripts/es_query.py '(metrics.platform: "sdc") AND (metrics.cache_info.json)' --explain

es-query-json:
	$(PYTHON_VENV) monitoring/scripts/es_query.py '(metrics.platform: "sdc") AND (metrics.cache_info.json)' --json

## Alert Checker (基于规则的告警检查)
alert-check:
	$(PYTHON_VENV) monitoring/scripts/alert_checker.py --rules-dir monitoring/alert_rules

alert-check-rule:
	$(PYTHON_VENV) monitoring/scripts/alert_checker.py --rule monitoring/alert_rules/sdc/cache_info_json.yaml

alert-show-rule:
	$(PYTHON_VENV) monitoring/scripts/alert_checker.py --rule monitoring/alert_rules/sdc/cache_info_json.yaml --show-rule

alert-check-disk:
	$(PYTHON_VENV) monitoring/scripts/alert_checker.py --rule monitoring/alert_rules/sdc/disk_used_ratio.yaml

## Email Notification (邮件通知)
alert-email-test:
	$(PYTHON_VENV) monitoring/scripts/email_notifier.py

alert-check-email:
	$(PYTHON_VENV) monitoring/scripts/alert_checker.py --rule monitoring/alert_rules/sdc/cache_info_json.yaml --email

alert-check-all-email:
	$(PYTHON_VENV) monitoring/scripts/alert_checker.py --rules-dir monitoring/alert_rules --email

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

## ADK Agent (Google Agent Development Kit)
agent-install:
	$(VENV)/bin/pip install -r agent/requirements.txt

agent-run:
	cd agent && adk run .

agent-run-simple:
	cd agent && $(VENV)/bin/python grafana_agent_simple.py

agent-tools:
	@echo "Available Agent Tools:"
	@echo "======================"
	@echo "ES Query:"
	@echo "  search_es_by_platform(platform, time_range)"
	@echo "  search_es_by_device(device_id, platform, time_range)"
	@echo "  search_es_by_metric(metric_name, platform, min_value, time_range)"
	@echo "  search_es_custom(lucene_query, time_range, size)"
	@echo "  get_es_summary(platform, time_range)"
	@echo ""
	@echo "Alert:"
	@echo "  check_all_alerts(platform, severity)"
	@echo "  check_alert_by_rule(rule_name)"
	@echo "  get_alert_rules(platform)"
	@echo "  analyze_alert_trend(device_id, platform, hours)"
	@echo "  get_alert_suggestions(platform)"
	@echo ""
	@echo "Dashboard:"
	@echo "  list_dashboards(folder, tag, search, limit)"
	@echo "  get_dashboard_panels(dashboard_uid)"
	@echo "  search_panels(keyword, folder)"
	@echo "  get_panel_info(dashboard_uid, panel_id)"
	@echo "  get_dashboard_recommendations(platform)"

## Show this help
help:
	@echo "Grafana MCP Server - Available Commands"
	@echo "======================================="
	@echo ""
	@echo "Setup:"
	@echo "  make install      - Install dependencies"
	@echo "  make venv         - Create virtual environment"
	@echo "  make agent-install- Install ADK Agent dependencies"
	@echo ""
	@echo "Running:"
	@echo "  make run          - Start MCP server"
	@echo "  make simple-client- Run all tests"
	@echo "  make agent-run    - Run ADK Agent interactively"
	@echo ""
	@echo "Individual Tests:"
	@echo "  make test-list-tools    - List available tools"
	@echo "  make test-list-dashboards - List dashboards"
	@echo "  make test-get-panels    - Get dashboard panels"
	@echo "  make test-get-panel     - Get panel info (id=5)"
	@echo "  make test-query-data    - Query panel data (id=6)"
	@echo "  make test-get-alerts    - Get firing alerts"
	@echo "  make test-list-ds       - List datasources"
	@echo "  make test-query-es      - Query ES via Grafana"
	@echo ""
	@echo "Elasticsearch Direct Query (脱开 Grafana):"
	@echo "  make es-query           - Query: (platform:sdc) AND (cache_info.json)"
	@echo "  make es-query-sdc       - Query: platform:sdc (24h)"
	@echo "  make es-query-explain   - Show query DSL"
	@echo "  make es-query-json      - Output raw JSON"
	@echo ""
	@echo "Alert Checker (基于 YAML 规则的告警):"
	@echo "  make alert-check        - 检查所有告警规则"
	@echo "  make alert-check-rule   - 检查 cache_info.json 规则"
	@echo "  make alert-show-rule    - 显示规则详情"
	@echo "  make alert-check-disk   - 检查 disk_used_ratio 规则"
	@echo ""
	@echo "Email Notification:"
	@echo "  make alert-email-test   - 测试邮件配置"
	@echo "  make alert-check-email  - 检查告警并发送邮件"
	@echo "  make alert-check-all-email - 检查所有规则并发送邮件"
	@echo ""
	@echo "Interactive Explorer:"
	@echo "  make explore            - Interactive dashboard explorer"
	@echo "  make explore-ipc        - Explore dashboards in 'ipc' folder"
	@echo "  make explore-all        - Explore all dashboards (limit=200)"
	@echo ""
	@echo "ADK Agent:"
	@echo "  make agent-tools        - List all agent tools"
	@echo "  make agent-run          - Run agent interactively (requires ZHIPU_API_KEY)"
	@echo "  make agent-run-simple   - Run simple agent without LLM"
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
