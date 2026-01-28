# 更新日志 (Changelog)

本文档记录采购收据管理工具的所有重要更改。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)，
版本号遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

## [未发布]

### 新增
- **Agent 工具**: 添加 `rename_sheet` 工具，支持完全自定义重命名 Sheet
- **Agent 工具**: 添加 `rename_sheet_auto` 工具，自动添加日期格式（如 "主题（日期）"）

### 修复
- **Excel 日期解析**: 修复 `read_receipt` 函数无法正确解析原始文件 Excel 日期序列号的问题
  - 支持多种日期格式：Excel 序列号、`YYYY-MM-DD`、`YYYY年MM月DD日`、datetime 对象
  - 优先从 E2 单元格（日期字段）读取，回退到最后一行的交付日期字段
- **Excel 合并功能**: 修复 `merge_excel_files` 函数的两个关键问题
  - 日期值从 2025 年被错误转换为 2026 年的问题
  - 图片未被复制到合并后文件的问题
- **默认路径**: 更新所有 Excel 工具的默认路径为 `~/Documents/receipt-309/309-采购明细.xlsx`

### 改进
- **Excel 合并功能**: 改进数据保留策略
  - 保留原始单元格值和数据类型
  - 复制合并单元格
  - 复制图片
  - 复制行高和列宽
- **Agent 指令**: 更新 agent 的 instruction 文本，包含新的默认路径信息和重命名工具说明

## [1.0.0] - 2025-01-XX

### 新增
- **AI 识别**: 使用火山引擎视觉大模型自动识别收据信息
- **Excel 操作**: 保存、读取、更新、删除收据
- **收据查询**: 按条件查询和搜索收据
- **统计分析**: 获取统计信息和分析报告
- **批量处理**: 支持批量识别多个收据图片
- **Agent 模式**: 基于 Google ADK 框架的智能助手，支持自然语言交互

### 工具列表
- `recognize_receipt`: 识别单张收据图片
- `batch_recognize`: 批量识别文件夹中的收据
- `create_manual_receipt`: 手动创建收据
- `save_receipt_to_excel`: 保存收据到 Excel
- `read_receipt_from_excel`: 从 Excel 读取收据
- `list_excel_sheets`: 列出所有 Sheet
- `update_receipt_in_excel`: 更新 Excel 中的收据
- `delete_receipt_from_excel`: 删除 Sheet
- `merge_excel_files`: 合并多个 Excel 文件
- `sort_sheets_by_date`: 按日期排序 Sheet
- `list_receipts`: 列出所有收据
- `search_receipts_by_keyword`: 按关键词搜索
- `get_receipt_by_date`: 按日期查询
- `get_receipt_summary`: 获取收据汇总
- `get_statistics`: 获取统计信息
- `export_statistics_json`: 导出统计数据
- `analyze_by_period`: 按周期分析
- `get_top_items`: 获取商品排行榜
- `get_monthly_summary`: 获取月度汇总

## 技术细节

### 日期解析改进
原始 Excel 文件使用 Excel 日期序列号（如 45980 表示 2025-11-19）存储日期。
之前的 `read_receipt` 函数无法正确解析这种格式，导致返回默认的当前日期。

修复后的 `_parse_date_from_cell` 方法支持：
- Excel 日期序列号（整数 > 30000）
- ISO 格式字符串：`2025-01-20`
- 中文格式字符串：`2025年01月20日`
- Python `datetime` 对象
- Python `date` 对象

### Excel 合并改进
之前的合并功能存在以下问题：
1. 使用 `data_only=True` 导致公式被计算结果替换
2. 未复制图片和合并单元格
3. 日期序列号被转换为字符串格式

修复后的合并功能：
- 使用 `data_only=False` 保留原始值
- 显式设置 `data_type` 保留数据类型
- 复制所有样式（字体、边框、填充、对齐）
- 复制行高和列宽
- 复制合并单元格
- 复制图片

## 使用示例

### 重命名 Sheet
```python
# 使用 rename_sheet_auto 自动添加日期格式
rename_sheet_auto(old_name="9月份开学教室布置", date_str="9-1")
# 结果: "9月份开学教室布置（9-1）"

# 使用 rename_sheet 完全自定义
rename_sheet(old_name="旧名称", new_name="新名称")
```

### 合并 Excel 文件
```python
# 合并文件到默认路径
merge_excel_files(source_paths=["./file1.xlsx", "./file2.xlsx"])

# 合并到指定路径
merge_excel_files(
    source_paths=["./source.xlsx"],
    target_path="./merged.xlsx",
    remove_duplicates=True
)
```

### Agent 自然语言交互
```
你: 合并 ~/Documents/receipt-309/309-采购明细-new.xlsx
助手: ✓ Excel 文件合并完成
      文件: /home/user/Documents/receipt-309/309-采购明细.xlsx
      合并数量: 8 个 Sheet

你: 把 "9月份开学教室布置" 添加日期 9-1
助手: ✓ Sheet 已重命名: 9月份开学教室布置 → 9月份开学教室布置（9-1）

你: 按日期从新到旧排序
助手: ✓ Sheet 已按日期从新到旧排序，共 14 个 Sheet
```
