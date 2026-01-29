.PHONY: install run test clean lint

# 安装依赖
install:
	pip install -r requirements.txt

# 开发模式安装（可编辑）
dev:
	pip install -e .

# 运行 MCP 服务器
run:
	python -m tupu_bi.server

# 测试
test:
	python -m pytest tests/ -v -rs

# 代码检查
lint:
	python -m flake8 tupu_bi/

# 格式化代码
fmt:
	python -m black tupu_bi/

# 清理
clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name '*.pyc' -delete
	rm -rf build/ dist/ *.egg-info/
