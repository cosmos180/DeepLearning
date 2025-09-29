# 测试说明

## 项目测试结构

本项目为每个MCP模块都提供了单元测试，确保各个组件的功能正确性。

### 测试目录结构
```
tests/
├── mcp/
│   ├── industry_analyst/
│   │   └── test_analyst.py
│   ├── indicator_alignment/
│   │   └── test_aligner.py
│   ├── downloader/
│   │   └── test_downloader.py
│   ├── financial_reader/
│   │   └── test_reader.py
│   ├── data_validator/
│   │   └── test_validator.py
│   ├── external_data/
│   │   └── test_external.py
│   └── report_generator/
│       └── test_generator.py
└── run_tests.py
```

## 运行测试

### 运行所有测试

```bash
cd python/investment_analyst
python run_tests.py
```

### 运行特定模块的测试

```bash
# 运行行业分析师MCP测试
python -m unittest tests.mcp.industry_analyst.test_analyst

# 运行指标对齐MCP测试
python -m unittest tests.mcp.indicator_alignment.test_aligner

# 运行下载MCP测试
python -m unittest tests.mcp.downloader.test_downloader

# 运行财报阅读MCP测试
python -m unittest tests.mcp.financial_reader.test_reader

# 运行数据验证MCP测试
python -m unittest tests.mcp.data_validator.test_validator

# 运行外部数据MCP测试
python -m unittest tests.mcp.external_data.test_external

# 运行报告生成MCP测试
python -m unittest tests.mcp.report_generator.test_generator
```

### 运行单个测试方法

```bash
# 运行行业分析师MCP的特定测试方法
python -m unittest tests.mcp.industry_analyst.test_analyst.TestIndustryAnalystMCP.test_analyze_industry
```

## 测试覆盖范围

每个MCP模块的测试都覆盖了以下方面：

1. **初始化测试** - 验证模块正确初始化
2. **功能测试** - 验证各个公共方法的功能
3. **边界条件测试** - 验证异常情况和边界条件的处理
4. **数据结构测试** - 验证返回数据的结构和类型
5. **集成测试** - 验证模块间的数据传递和协作

## 测试依赖

测试依赖已在 `requirements.txt` 中列出，确保安装了所有必要的包：

```bash
pip install -r requirements.txt
```

## 测试开发

要为新功能添加测试，请遵循以下步骤：

1. 在相应的测试模块中创建测试类
2. 为每个公共方法创建测试方法
3. 包含正常情况和异常情况的测试用例
4. 验证返回数据的结构和内容
5. 运行所有测试确保没有破坏现有功能

## 测试质量保证

- 所有测试都应具有确定性（相同输入总是产生相同输出）
- 测试应独立运行，不依赖于其他测试的执行顺序
- 测试应覆盖正常流程和异常流程
- 测试应验证数据的正确性和完整性
