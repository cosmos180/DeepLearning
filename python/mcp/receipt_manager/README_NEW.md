# 采购收据管理工具

一个智能的命令行工具，通过AI视觉识别技术自动提取采购收据信息，并将其保存到Excel文件中。专为教室采购管理设计，兼容现有的"309 采购明细.xlsx"格式。

## 功能特性

- **智能识别**: 使用AI视觉大模型自动识别收据图片
- **Excel兼容**: 完全兼容现有的"309 采购明细.xlsx"格式
- **灵活输入**: 支持图片识别和手动输入
- **批量处理**: 支持批量处理多个收据
- **数据验证**: 自动验证数据完整性和一致性

## 快速开始

### 安装

```bash
cd /home/bughero/Documents/github/DeepLearning/python/mcp/receipt_manager
pip install -r requirements.txt
```

### 设置API密钥

```bash
export ARK_API_KEY="your-volcengine-api-key"
```

### 基本使用

```bash
# 安装命令
pip install -e .

# 添加收据（AI识别）
receipt-manager add receipt.jpg

# 指定主题和日期
receipt-manager add receipt.jpg --title "数学资料打印" --date "2025-1-20"

# 手动输入模式
receipt-manager add receipt.jpg --no-ai

# 列出所有收据
receipt-manager list

# 导出数据
receipt-manager export --format json
```

## Excel格式说明

### Sheet命名规则

```
格式：主题名称（月-日）
示例：
  - 数学资料打印（1-20）
  - 教室布置（9-1）
```

### Sheet结构

```
行号  | 内容
------|------
1     | 主题标题
2     | 采购方：_________________ 联系方式：   | 梁程程妈妈
4     | 序号 | 商品名称 | 规格型号 | 单位 | 采购数量 | 单价（元） | 金额（元） | 备注
5+    | 商品明细行...
N-1   | 总计金额
N     | 交付日期：YYYY-M-D    付款方式：转账
```

### 固定值

- **采购方**: 梁程程妈妈
- **付款方式**: 转账

## CLI命令

### 添加收据

```bash
# AI识别
receipt-manager add receipt.jpg

# 指定提示信息
receipt-manager add receipt.jpg --title "打印资料" --date "2025-1-20"

# 跳过确认
receipt-manager add receipt.jpg --yes

# 手动输入模式
receipt-manager add --no-ai
```

### 查看记录

```bash
# 列出所有记录
receipt-manager list

# 按主题筛选
receipt-manager list --title "打印"

# 按日期范围
receipt-manager list --from "2025-1-1" --to "2025-1-31"

# 限制显示数量
receipt-manager list --limit 10
```

### 导出数据

```bash
# 导出为JSON
receipt-manager export --format json

# 导出到文件
receipt-manager export --format json --output data.json
```

### 手动创建

```bash
# 交互式创建收据
receipt-manager manual "数学资料打印"

# 指定日期
receipt-manager manual "数学资料打印" --date "2025-1-20"
```

## 项目结构

```
receipt_manager/
├── receipt_manager/
│   ├── __init__.py          # 核心数据模型
│   ├── excel_handler.py     # Excel处理
│   ├── ai_ocr.py            # AI识别
│   └── cli.py               # CLI界面
├── tests/                   # 测试文件
├── data/                    # 数据目录
├── logs/                    # 日志目录
├── requirements.txt         # 依赖列表
├── setup.py                 # 安装配置
└── README.md                # 本文件
```

## 开发

### 运行测试

```bash
# 运行所有测试
pytest tests/

# 运行特定测试
pytest tests/test_receipt_manager.py

# 查看覆盖率
pytest --cov=receipt_manager --cov-report=html
```

### 代码格式化

```bash
# 格式化代码
black receipt_manager/

# 类型检查
mypy receipt_manager/
```

## 配置

### 环境变量

| 变量 | 说明 |
|------|------|
| ARK_API_KEY | 火山引擎API密钥 |

### 默认Excel路径

默认Excel文件路径：`~/Documents/309 采购明细.xlsx`

可以通过 `--excel-file` 参数指定：

```bash
receipt-manager -e /path/to/excel.xlsx add receipt.jpg
```

## 技术栈

- **Python 3.10+**
- **Click** - 命令行界面
- **Pydantic** - 数据验证
- **OpenPyXL** - Excel操作
- **火山引擎API** - AI视觉识别
- **Loguru** - 日志系统
- **Rich** - 终端美化

## 设计文档

- [实际Excel结构适配](ACTUAL_STRUCTURE.md) - 实际Excel结构分析
- [数据结构设计](DATA_STRUCTURE.md) - 数据模型设计
- [技术架构](TECHNICAL_ARCHITECTURE.md) - 系统架构设计

## 常见问题

### Q: AI识别失败怎么办？

A: 工具会自动提示是否切换到手动输入模式，或者可以使用 `--no-ai` 参数直接进入手动模式。

### Q: 如何修改采购方名称？

A: 目前采购方固定为"梁程程妈妈"，如需修改请使用 `manual` 命令并指定 `--purchaser` 参数。

### Q: Excel文件不存在会怎样？

A: 工具会自动创建新的Excel文件。

## 贡献

欢迎贡献！请查看 [ACTUAL_STRUCTURE.md](ACTUAL_STRUCTURE.md) 了解实现细节。

## 许可证

MIT License

## 联系方式

- **作者**: bughero
- **邮箱**: bughero2012@gmail.com
- **项目路径**: /home/bughero/Documents/github/DeepLearning/python/mcp/receipt_manager

---

**版本**: 1.0.0
**最后更新**: 2025-01-20
