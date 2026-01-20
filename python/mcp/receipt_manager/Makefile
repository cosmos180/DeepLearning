# Makefile for receipt_manager
# 采购收据管理工具 - 命令快捷方式

.PHONY: help install test test-coverage clean lint format
.PHONY: add list export manual

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
	@echo "收据操作:"
	@echo "  make add IMG=<path>              - AI识别添加收据"
	@echo "  make add-manual IMG=<path>       - 手动输入添加收据"
	@echo "  make manual TITLE=<title>        - 手动创建收据"
	@echo "  make list                        - 查看所有收据"
	@echo "  make export                      - 导出统计信息"
	@echo ""
	@echo "示例:"
	@echo "  make add IMG=receipt.jpg"
	@echo "  make add IMG=receipt.jpg TITLE=打印"
	@echo "  make manual TITLE=数学资料打印"
	@echo ""
	@echo "配置:"
	@echo "  EXCEL_FILE=$(EXCEL_FILE)"
	@echo "  API_KEY=$${ARK_API_KEY:+(已设置)}"

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
	python -m receipt_manager.cli add "$(IMG)" -e "$(EXCEL_FILE)" $(if $(TITLE),-t "$(TITLE)",)

# 添加收据 (手动输入)
add-manual:
	@if [ -z "$(IMG)" ]; then \
		echo "错误: 请指定图片路径"; \
		echo "用法: make add-manual IMG=<path> [TITLE=<title>]"; \
		exit 1; \
	fi
	python -m receipt_manager.cli add "$(IMG)" --no-ai -e "$(EXCEL_FILE)" $(if $(TITLE),-t "$(TITLE)",)

# 手动创建收据
manual:
	@if [ -z "$(TITLE)" ]; then \
		echo "错误: 请指定主题标题"; \
		echo "用法: make manual TITLE=<title>"; \
		exit 1; \
	fi
	python -m receipt_manager.cli manual "$(TITLE)" -e "$(EXCEL_FILE)" $(if $(DATE),-d "$(DATE)",)

# 查看收据列表
list:
	python -m receipt_manager.cli list -e "$(EXCEL_FILE)"

# 导出数据
export:
	python -m receipt_manager.cli export -e "$(EXCEL_FILE)"
