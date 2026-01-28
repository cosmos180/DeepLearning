# Receipt Manager ADK Agent

基于 Google Agent Development Kit 的智能采购收据管理 Agent。

## 概述

这个 Agent 将采购收据管理功能转换为智能对话接口，支持：

- **AI 识别** - 使用 AI 自动识别收据图片
- **Excel 操作** - 保存、读取、更新、删除收据
- **收据查询** - 按条件查询和搜索收据
- **统计分析** - 获取统计信息和分析报告

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 设置 API Key

```bash
# 智谱 AI (用于 LLM Agent)
export ZHIPU_API_KEY="your-zhipu-api-key"

# 火山引擎 (用于 AI 识别)
export ARK_API_KEY="your-ark-api-key"
```

### 3. 运行 Agent

```bash
# 方式 1: 使用 ADK 运行完整版 (推荐)
cd agent
adk run .

# 方式 2: 直接运行简化版 (不需要 LLM)
python agent/receipt_agent_simple.py
```

### 4. 与 Agent 对话

```
Running agent receipt_manager_agent, type exit to exit.

[user]: 识别 ./receipt.jpg
[receipt_manager_agent]: [显示识别结果]

[user]: 列出所有收据
[receipt_manager_agent]: [显示收据列表]

[user]: 显示统计信息
[receipt_manager_agent]: [显示统计数据]

[user]: exit
```

## 可用工具

### AI 识别工具

| 工具 | 说明 | 示例 |
|------|------|------|
| `recognize_receipt` | 识别单张收据图片 | "识别 ./receipt.jpg" |
| `batch_recognize` | 批量识别文件夹 | "批量识别 ./receipts 文件夹" |
| `create_manual_receipt` | 手动创建收据 | "创建收据：数学资料打印" |

### Excel 操作工具

| 工具 | 说明 | 示例 |
|------|------|------|
| `save_receipt_to_excel` | 保存收据到 Excel | "保存收据到 Excel" |
| `read_receipt_from_excel` | 读取收据 | "查看 Sheet xxx" |
| `list_excel_sheets` | 列出所有 Sheet | "列出所有收据" |
| `update_receipt_in_excel` | 更新收据 | "更新 Sheet xxx" |
| `delete_receipt_from_excel` | 删除收据 | "删除 Sheet xxx" |

### 查询工具

| 工具 | 说明 | 示例 |
|------|------|------|
| `list_receipts` | 列出收据 | "列出所有收据" |
| `search_receipts_by_keyword` | 按关键词搜索 | "搜索包含打印的收据" |
| `get_receipt_by_date` | 获取指定日期收据 | "查看 2025-01-20 的收据" |
| `get_receipt_summary` | 获取收据摘要 | "显示收据摘要" |

### 统计工具

| 工具 | 说明 | 示例 |
|------|------|------|
| `get_statistics` | 获取统计信息 | "显示统计信息" |
| `export_statistics_json` | 导出 JSON | "导出统计为 JSON" |
| `analyze_by_period` | 按周期分析 | "按月分析收据" |
| `get_top_items` | 获取购买最多商品 | "显示商品排行榜" |
| `get_monthly_summary` | 获取月度汇总 | "查看月度汇总" |

## 自然语言示例

### AI 识别
```
"识别这张收据 ./receipt.jpg"
"批量识别 ./receipts 文件夹中的收据"
"识别 ./receipt.jpg，主题可能是打印"
```

### 查询
```
"列出所有收据"
"列出 2025年1月的收据"
"搜索包含打印的收据"
"查看 2025-01-20 的收据"
```

### 统计
```
"显示统计信息"
"查看月度汇总"
"按月分析收据"
"显示购买最多的商品"
```

## 配置

### 环境变量

| 变量 | 说明 | 必需 |
|------|------|------|
| `ZHIPU_API_KEY` | 智谱 AI API Key (LLM) | 否 |
| `ARK_API_KEY` | 火山引擎 API Key (AI识别) | 是 |

### 默认 Excel 文件

`~/Downloads/309 采购明细.xlsx`

可通过 `excel_path` 参数修改。

## 架构

```
agent/
├── __init__.py               # Root Agent 定义 (adk run 入口)
├── receipt_agent_simple.py   # 简化版 (不需要 LLM)
├── tools/
│   ├── __init__.py           # 导出所有工具
│   ├── ocr_tool.py           # AI 识别工具
│   ├── excel_tool.py         # Excel 操作工具
│   ├── query_tool.py         # 收据查询工具
│   └── stats_tool.py         # 统计分析工具
├── requirements.txt
└── README.md
```

## 原有 CLI 保留

原有的 Click CLI 仍然可用：

```bash
python -m receipt_manager.cli add ./receipt.jpg
python -m receipt_manager.cli list
python -m receipt_manager.cli batch ./receipts
```

## 模型

- **LLM Agent**: GLM-4-Flash (智谱 AI)
- **API**: OpenAI 兼容端点 (`https://open.bigmodel.cn/api/paas/v4/`)
- **AI 识别**: 火山引擎 doubao-seed 模型

## 故障排查

### Agent 启动失败

1. 确保设置了 `ZHIPU_API_KEY` (LLM Agent 需要)
2. 检查网络连接到智谱 API
3. 使用简化版测试: `python agent/receipt_agent_simple.py`

### AI 识别失败

1. 确保设置了 `ARK_API_KEY`
2. 检查图片路径是否正确
3. 查看图片格式是否支持 (jpg, png 等)

### 工具调用失败

1. 确保 Excel 文件可访问
2. 检查文件权限
3. 查看错误日志

## 许可证

MIT License
