# DCF估值模型 Makefile
# 一键运行和管理DCF估值脚本

.PHONY: run run-original install clean help setup test test-config dev-install doc

# 默认目标
.DEFAULT_GOAL := help

# 颜色输出
BLUE = \033[36m
GREEN = \033[32m
YELLOW = \033[33m
RED = \033[31m
NC = \033[0m  # No Color

# 更全面的帮助信息
help:
	@echo "$(BLUE)DCF估值模型 - 使用说明$(NC)"
	@echo "=========================="
	@echo ""
	@echo "$(GREEN)重构版本 - 推荐$(NC)"
	@echo "  $(YELLOW)make run$(NC)         - 运行重构版DCF估值计算（修复BUG，推荐）"
	@echo "  $(YELLOW)make run-original$(NC) - 运行原版DCF估值（对比用）"
	@echo "  $(YELLOW)make test$(NC)        - 运行重构版单元测试（13个测试用例）"
	@echo "  $(YELLOW)make test-config$(NC)  - 测试配置文件加载"
	@echo ""
	@echo "$(GREEN)配置管理$(NC)"
	@echo "  配置文件位置: ./config/"
	@echo "  - tencent.yaml  - 腾讯控股配置"
	@echo "  - apple.yaml    - Apple Inc.配置"
	@echo ""
	@echo "$(GREEN)开发工具$(NC)"
	@echo "  $(YELLOW)make doc$(NC)         - 查看重构报告"
	@echo "  $(YELLOW)make dev-install$(NC) - 安装开发工具（ipython, jupyter等）"
	@echo ""
	@echo "$(GREEN)环境管理$(NC)"
	@echo "  $(YELLOW)make setup$(NC)       - 首次设置"
	@echo "  $(YELLOW)make install$(NC)     - 安装/更新依赖"
	@echo "  $(YELLOW)make clean$(NC)       - 清理临时文件"
	@echo "  $(YELLOW)make clean-all$(NC)   - 深度清理（包含虚拟环境）"
	@echo ""
	@echo "$(GREEN)文件说明$(NC)"
	@echo "  dcf_revised.py      - 重构版代码（推荐）"
	@echo "  dcf.py              - 原版代码（对比用）"
	@echo "  test_dcf_revised.py - 重构版单元测试"
	@echo "  REFACTORING_REPORT.md - 重构报告"
	@echo ""

# Python虚拟环境
VENV = venv
PYTHON = $(VENV)/bin/python
PIP = $(VENV)/bin/pip

# 首次设置：创建虚拟环境并安装依赖
setup: check-env
	@echo "$(BLUE)正在创建虚拟环境...$(NC)"
	python3 -m venv $(VENV)
	@echo "$(GREEN)✓ 虚拟环境创建完成$(NC)"
	$(MAKE) install

# 检查Python环境
check-env:
	@command -v python3 >/dev/null 2>&1 || { echo "$(RED)错误：未找到python3，请先安装Python 3.6+$(NC)"; exit 1; }
	@echo "$(GREEN)✓ Python环境检查通过$(NC)"

# 安装依赖
install: check-env
	@echo "$(BLUE)正在安装依赖包...$(NC)"
	$(PIP) install --upgrade pip -i https://pypi.tuna.tsinghua.edu.cn/simple
	$(PIP) install numpy pandas matplotlib -i https://pypi.tuna.tsinghua.edu.cn/simple
	@echo "$(GREEN)✓ 依赖包安装完成$(NC)"

# 运行DCF估值计算（重构版）
run: check-venv
	@echo "$(BLUE)正在运行DCF估值计算（重构版）...$(NC)"
	$(PYTHON) dcf_revised.py
	@echo ""
	@echo "$(GREEN)✓ DCF估值计算完成$(NC)"


# 检查虚拟环境是否存在
check-venv:
	@if [ ! -d "$(VENV)" ]; then \
		echo "$(RED)错误：虚拟环境不存在，请先运行 'make setup'$(NC)"; \
		exit 1; \
	fi
	@if [ ! -f "$(PYTHON)" ]; then \
		echo "$(RED)错误：Python解释器不存在$(NC)"; \
		exit 1; \
	fi

# 运行单元测试
test: check-venv
	@echo "$(BLUE)正在运行单元测试...$(NC)"
	$(PYTHON) -m pytest test_dcf_revised.py -v
	@echo "$(GREEN)✓ 单元测试完成$(NC)"

# 清理生成的文件和虚拟环境
clean:
	@echo "$(BLUE)正在清理...$(NC)"
	@find . -type f -name "*.pyc" -delete
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.png" -delete 2>/dev/null || true
	@find . -type f -name ".DS_Store" -delete 2>/dev/null || true
	@echo "$(GREEN)✓ 清理临时文件完成$(NC)"

# 深度清理：同时删除虚拟环境
clean-all: clean
	@echo "$(BLUE)正在删除虚拟环境...$(NC)"
	@rm -rf $(VENV)
	@echo "$(GREEN)✓ 虚拟环境已删除$(NC)"
	@echo "$(YELLOW)提示：下次运行前请执行 'make setup'$(NC)"

# 重新安装（清理后重新设置）
reinstall: clean-all setup
	@echo "$(GREEN)✓ 重新安装完成$(NC)"

# 显示Python版本信息
version: check-venv
	@echo "$(BLUE)Python版本信息:$(NC)"
	@$(PYTHON) --version
	@echo "$(BLUE)已安装的包:$(NC)"
	@$(PIP) list | grep -E "(numpy|pandas|matplotlib)"

# 开发模式：安装额外的开发工具（如jupyter, ipython等）
dev-install: check-venv
	@echo "$(BLUE)正在安装开发工具...$(NC)"
	$(PIP) install jupyter ipython seaborn -i https://pypi.tuna.tsinghua.edu.cn/simple
	@echo "$(GREEN)✓ 开发工具安装完成$(NC)"

# 生成重构报告
doc:
	@echo "$(BLUE)查看重构报告...$(NC)"
	@if [ -f "REFACTORING_REPORT.md" ]; then \
		echo "请查看: REFACTORING_REPORT.md"; \
	else \
		echo "$(RED)重构报告不存在$(NC)"; \
	fi
