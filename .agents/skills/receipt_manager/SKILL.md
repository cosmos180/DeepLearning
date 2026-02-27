---
name: receipt_manager
description: 采购收据智能管理 - 支持 AI 识别收据图片、Excel CRUD、查询统计
---

# 采购收据管理 Skill

管理采购收据的完整工具集，支持 AI 识别收据图片、Excel 存储、查询和统计分析。

## 环境要求

- Python 3.9+
- AI 识别需要设置 `ARK_API_KEY` 环境变量（火山引擎）
- 依赖安装：`pip install -r /home/bughero/Documents/github/DeepLearning/.agents/skills/receipt_manager/scripts/requirements.txt`

## 默认 Excel 文件

`~/Documents/receipt-309/309-采购明细.xlsx`

所有命令默认使用此文件，可通过 `--excel-path` 参数指定其他文件。

## CLI 入口

所有操作通过以下命令执行：

```bash
python /home/bughero/Documents/github/DeepLearning/.agents/skills/receipt_manager/scripts/receipt_cli.py <command> [options]
```

## 命令参考

### AI 识别

#### 识别单张收据
用户说：「识别这张收据」「识别图片」

```bash
python receipt_cli.py recognize <image_path> [--hint <主题提示>] [--date-hint <日期提示>]
```

#### 批量识别
用户说：「批量识别文件夹」

```bash
python receipt_cli.py batch-recognize <folder_path> [--pattern "*.jpg"] [--recursive]
```

#### 识别并保存到 Excel
用户说：「识别并保存」「录入收据」

```bash
python receipt_cli.py recognize-and-save <image_path> [--hint <提示>] [--image-anchor H2]
```

#### 手动创建收据
用户说：「创建收据」「手动录入」

```bash
python receipt_cli.py create-receipt --title <标题> --date <YYYY-M-D> [--purchaser <采购方>] [--payment <付款方式>] [--items '<JSON数组>']
```

items JSON 格式：`[{"name": "商品名", "quantity": 10, "unit_price": 5.0, "unit": "个"}]`

### Excel 操作

#### 保存收据到 Excel
```bash
python receipt_cli.py save --data '<JSON>' [--image-path <图片路径>]
```

data JSON 格式：`{"title": "主题", "delivery_date": "2025-01-20", "purchaser": "梁程程妈妈", "payment_method": "转账", "items": [...]}`

#### 读取收据
用户说：「查看 Sheet xxx」

```bash
python receipt_cli.py read --sheet <Sheet名称>
```

#### 列出所有 Sheet
用户说：「列出所有收据」「显示所有 Sheet」

```bash
python receipt_cli.py list-sheets
```

#### 更新收据
```bash
python receipt_cli.py update --sheet <Sheet名称> --data '<JSON>'
```

#### 删除收据
```bash
python receipt_cli.py delete --sheet <Sheet名称>
```

#### 合并 Excel 文件
用户说：「合并 Excel」

```bash
python receipt_cli.py merge --sources <文件1.xlsx>,<文件2.xlsx> [--target <目标.xlsx>]
```

#### 按日期排序 Sheet
用户说：「按日期排序」

```bash
python receipt_cli.py sort [--order desc]
```

#### 重命名 Sheet
```bash
python receipt_cli.py rename --old <旧名称> --new <新名称>
```

#### 自动重命名（主题+日期格式）
```bash
python receipt_cli.py rename-auto --old <旧名称> --date <9-1>
```

#### 美化 Excel
用户说：「美化 Excel」「优化样式」

```bash
python receipt_cli.py beautify
```

### 查询

#### 列出收据（支持筛选）
用户说：「列出所有收据」「列出某月收据」

```bash
python receipt_cli.py list [--filter <关键词>] [--from <起始日期>] [--to <结束日期>] [--limit 20]
```

#### 关键词搜索
用户说：「搜索包含 xxx 的收据」

```bash
python receipt_cli.py search --keyword <关键词>
```

#### 按日期查看
用户说：「查看某日的收据」

```bash
python receipt_cli.py by-date --date <YYYY-M-D>
```

#### 获取收据摘要
```bash
python receipt_cli.py summary --sheet <Sheet名称>
```

### 统计分析

#### 总体统计
用户说：「统计」「显示统计信息」

```bash
python receipt_cli.py stats
```

#### 导出统计 JSON
```bash
python receipt_cli.py export-json [--output <路径>]
```

#### 按周期分析
用户说：「按月分析」

```bash
python receipt_cli.py analyze [--period month|week|day]
```

#### 商品排行榜
用户说：「商品排行」「购买最多」

```bash
python receipt_cli.py top-items [--limit 10]
```

#### 月度汇总
用户说：「月度汇总」

```bash
python receipt_cli.py monthly [--year 2025]
```

## 注意事项

1. 金额显示使用人民币符号 ¥
2. 所有命令输出纯文本，直接展示给用户即可
3. OCR 识别需要 `ARK_API_KEY`，其他功能不需要
4. 如果用户没有指定 Excel 路径，使用默认路径
