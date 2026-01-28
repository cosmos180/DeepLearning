# Makefile for receipt_manager
# 采购收据管理工具 - 命令快捷方式

.PHONY: help install test test-coverage clean lint format
.PHONY: add list export manual batch
.PHONY: agent-install agent-run agent-run-simple agent-tools

# 配置变量
EXCEL_FILE ?= ~/Documents/309 采购明细.xlsx
API_KEY ?= $(ARK_API_KEY)

# 默认目标
help:
	@echo "采购收据管理工具 - 常用命令"
	@echo ""
	@echo "安装与测试:"
	@echo "  make install          - 安装依赖"
	@echo "  make test             - 运行测试"
	@echo "  make test-coverage    - 运行测试并生成覆盖率报告"
	@echo "  make lint             - 代码检查 (mypy)"
	@echo "  make format           - 代码格式化 (black)"
	@echo "  make clean            - 清理临时文件"
	@echo ""
	@echo "收据操作 (CLI):"
	@echo "  make add IMG=<path>              - AI识别添加收据"
	@echo "  make add-manual IMG=<path>       - 手动输入添加收据"
	@echo "  make manual TITLE=<title>        - 手动创建收据"
	@echo "  make batch FOLDER=<path>         - 批量处理文件夹中的收据"
	@echo "  make list                        - 查看所有收据"
	@echo "  make export                      - 导出统计信息"
	@echo ""
	@echo "Agent 智能助手:"
	@echo "  make agent-install    - 安装 Agent 依赖"
	@echo "  make agent-run        - 运行 ADK Agent (需要 ZHIPU_API_KEY)"
	@echo "  make agent-run-simple - 运行简化版 Agent (不需要 LLM)"
	@echo "  make agent-tools      - 列出所有 Agent 工具"
	@echo ""
	@echo "示例:"
	@echo "  make add IMG=receipt.jpg"
	@echo "  make add IMG=receipt.jpg TITLE=打印"
	@echo "  make manual TITLE=数学资料打印"
	@echo "  make batch FOLDER=./receipts"
	@echo "  make agent-run-simple    # 启动智能对话助手"
	@echo ""
	@echo "配置:"
	@echo "  EXCEL_FILE=$(EXCEL_FILE)"
	@echo "  API_KEY=$${ARK_API_KEY:+(已设置)}"
	@echo "  ZHIPU_API_KEY=$${ZHIPU_API_KEY:+(已设置)}"

# 安装依赖
install:
	@echo "安装依赖..."
	pip install -r requirements.txt

# 运行测试
test:
	@echo "运行测试..."
	pytest tests/ -v

# 测试覆盖率
test-coverage:
	@echo "运行测试并生成覆盖率报告..."
	pytest tests/ --cov=receipt_manager --cov-report=html --cov-report=term
	@echo "覆盖率报告: htmlcov/index.html"

# 代码检查
lint:
	@echo "代码类型检查..."
	mypy receipt_manager/
	@echo "代码风格检查..."
	black --check receipt_manager/

# 代码格式化
format:
	@echo "格式化代码..."
	black receipt_manager/

# 清理临时文件
clean:
	@echo "清理临时文件..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	rm -rf .pytest_cache htmlcov .coverage

# 添加收据 (AI识别)
add:
	@if [ -z "$(IMG)" ]; then \
		echo "错误: 请指定图片路径"; \
		echo "用法: make add IMG=<path> [TITLE=<title>]"; \
		exit 1; \
	fi
	@if [ -z "$(API_KEY)" ]; then \
		echo "错误: 请设置 ARK_API_KEY 环境变量"; \
		echo "export ARK_API_KEY='your-api-key'"; \
		exit 1; \
	fi
	python -m receipt_manager.cli -e "$(EXCEL_FILE)" add "$(shell bash -c 'echo $(IMG)')" $(if $(TITLE),-t "$(TITLE)",)

# 添加收据 (手动输入)
add-manual:
	@if [ -z "$(IMG)" ]; then \
		echo "错误: 请指定图片路径"; \
		echo "用法: make add-manual IMG=<path> [TITLE=<title>]"; \
		exit 1; \
	fi
	python -m receipt_manager.cli -e "$(EXCEL_FILE)" add "$(shell bash -c 'echo $(IMG)')" --no-ai $(if $(TITLE),-t "$(TITLE)",)

# 手动创建收据
manual:
	@if [ -z "$(TITLE)" ]; then \
		echo "错误: 请指定主题标题"; \
		echo "用法: make manual TITLE=<title>"; \
		exit 1; \
	fi
	python -m receipt_manager.cli -e "$(EXCEL_FILE)" manual "$(TITLE)" $(if $(DATE),-d "$(DATE)",)

# 查看收据列表
list:
	python -m receipt_manager.cli -e "$(EXCEL_FILE)" list

# 导出数据
export:
	python -m receipt_manager.cli -e "$(EXCEL_FILE)" export

# 批量处理收据
batch:
	@if [ -z "$(FOLDER)" ]; then \
		echo "错误: 请指定文件夹路径"; \
		echo "用法: make batch FOLDER=<path> [PATTERN=<pattern>] [RECURSIVE=1]"; \
		exit 1; \
	fi
	@if [ -z "$(API_KEY)" ]; then \
		echo "错误: 请设置 ARK_API_KEY 环境变量"; \
		echo "export ARK_API_KEY='your-api-key'"; \
		exit 1; \
	fi
	python -m receipt_manager.cli -e "$(EXCEL_FILE)" batch "$(shell bash -c 'echo $(FOLDER)')" \
		$(if $(PATTERN),-p "$(PATTERN)",) \
		$(if $(RECURSIVE),-r,)

# ============================================================================
# Agent 相关命令
# ============================================================================

# 安装 Agent 依赖
agent-install:
	@echo "安装 Agent 依赖..."
	pip install -r receipt_manager/agent/requirements.txt

# 运行 ADK Agent (需要 ZHIPU_API_KEY)
agent-run:
	@if [ -z "$$ZHIPU_API_KEY" ]; then \
		echo "错误: 请设置 ZHIPU_API_KEY 环境变量"; \
		echo "export ZHIPU_API_KEY='your-zhipu-api-key'"; \
		exit 1; \
	fi
	@echo "启动 ADK Agent..."
	cd receipt_manager/agent && adk run .

# 运行简化版 Agent (不需要 LLM)
agent-run-simple:
	@echo "启动简化版 Agent..."
	python receipt_manager/agent/receipt_agent_simple.py

# 列出所有 Agent 工具
agent-tools:
	@echo "Agent 工具列表:"
	@echo ""
	@echo "【AI 识别工具】"
	@echo "  - recognize_receipt(image_path, api_key, title_hint, date_hint)"
	@echo "  - batch_recognize(folder_path, pattern, api_key, recursive)"
	@echo "  - create_manual_receipt(title, delivery_date, purchaser, items)"
	@echo ""
	@echo "【Excel 操作工具】"
	@echo "  - save_receipt_to_excel(receipt_data, excel_path)"
	@echo "  - read_receipt_from_excel(sheet_name, excel_path)"
	@echo "  - list_excel_sheets(excel_path)"
	@echo "  - update_receipt_in_excel(sheet_name, receipt_data, excel_path)"
	@echo "  - delete_receipt_from_excel(sheet_name, excel_path)"
	@echo ""
	@echo "【查询工具】"
	@echo "  - list_receipts(excel_path, title_filter, from_date, to_date, limit)"
	@echo "  - search_receipts_by_keyword(keyword, excel_path, limit)"
	@echo "  - get_receipt_by_date(target_date, excel_path)"
	@echo "  - get_receipt_summary(sheet_name, excel_path)"
	@echo ""
	@echo "【统计工具】"
	@echo "  - get_statistics(excel_path)"
	@echo "  - export_statistics_json(output_path, excel_path)"
	@echo "  - analyze_by_period(period, excel_path)"
	@echo "  - get_top_items(excel_path, limit)"
	@echo "  - get_monthly_summary(year, excel_path)"
