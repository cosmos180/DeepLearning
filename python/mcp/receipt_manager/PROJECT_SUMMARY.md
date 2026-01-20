# 采购收据管理工具 - 项目概览

## 文档导航

本文档集包含采购收据管理工具的完整设计方案。建议按以下顺序阅读：

1. **README.md** - 项目介绍和快速开始
2. **DESIGN_DOC.md** - 产品设计文档（用户流程、功能模块、CLI设计）
3. **DATA_STRUCTURE.md** - 数据结构设计（数据模型、Excel格式、配置）
4. **TECHNICAL_ARCHITECTURE.md** - 技术架构设计（系统架构、模块设计）
5. **IMPLEMENTATION_PLAN.md** - 实施计划（开发步骤、协作方案）

---

## 项目简介

采购收据管理工具是一个智能的命令行工具，旨在通过AI视觉识别技术自动提取采购收据信息，并将其结构化地记录到Excel文件中。

### 核心价值

- **自动化**: 通过AI识别减少90%的手动录入工作
- **结构化**: 自动生成标准化的Excel表格，便于后续分析
- **灵活性**: 支持多种输入方式（图片、扫描件、文本描述）
- **可追溯**: 保留原始收据和识别结果的关联关系

### 目标用户

- 需要管理大量采购收据的个人用户
- 小型企业或团队的采购管理人员
- 需要定期整理报销凭证的办公人员

---

## 技术亮点

### 1. 复用现有代码

**复用视觉大模型Demo** (`/home/bughero/Documents/github/DeepLearning/python/llm/version/demo.py`):
- `AsyncArk` 客户端封装
- `FileWithProgress` 文件上传进度显示
- API调用和错误处理模式

**参考MCP服务器架构** (`/home/bughero/Documents/github/DeepLearning/python/mcp/`):
- 模块化项目结构
- 配置管理方式
- 日志记录规范

**利用照片行为检测模块** (`/home/bughero/Documents/github/DeepLearning/python/photo_behavior_detection/`):
- 图像预处理逻辑
- Tesseract OCR集成
- Pipeline处理模式

### 2. 技术栈

```
Python 3.10+
├── Click          # 命令行界面框架
├── Pydantic       # 数据验证
├── OpenPyXL       # Excel操作
├── 火山引擎API     # AI视觉识别
├── Tesseract      # OCR识别
├── Loguru         # 日志系统
└── Rich           # 终端美化
```

### 3. 架构特点

- **分层架构**: 展现层、应用层、领域层、基础设施层
- **模块化设计**: 清晰的模块划分和职责分离
- **异步处理**: 使用asyncio提高性能
- **错误处理**: 完善的错误处理和重试机制

---

## 功能概览

### 核心功能

1. **智能识别收据**
   - 使用AI视觉大模型识别收据图片
   - 提取商家、日期、金额、商品清单等信息
   - 支持多种收据格式

2. **Excel管理**
   - 自动创建Excel文件
   - 按日期+商家创建独立Sheet
   - 格式化表格，包含基础信息、商品明细、汇总信息
   - 维护概览Sheet，显示统计和最近记录

3. **数据验证**
   - 验证必填字段
   - 检查金额一致性
   - 提供详细错误报告

4. **灵活输入**
   - 支持图片文件（PNG、JPG等）
   - 支持扫描件
   - 支持文本描述
   - 提供手动输入模式

5. **批量处理**
   - 批量识别多个收据
   - 显示处理进度
   - 汇总处理结果

### CLI命令

```bash
# 添加收据
receipt-manager add receipt.jpg
receipt-manager add *.jpg --batch
receipt-manager add --text "超市购物: 牛奶x2, 总计25元"

# 查看记录
receipt-manager list
receipt-manager list --date 2025-01-20
receipt-manager list --category "办公用品"

# 导出数据
receipt-manager export --format csv
receipt-manager export --report

# 初始化配置
receipt-manager init
```

---

## 数据结构

### 收据模型

```python
Receipt:
  - receipt_id: str              # 收据唯一ID
  - date: date                   # 收据日期
  - merchant: str                # 商家名称
  - subtotal: Decimal            # 小计
  - tax: Decimal                 # 税额
  - discount: Decimal            # 折扣
  - total: Decimal               # 总计
  - items: List[ReceiptItem]     # 商品列表
  - metadata: ReceiptMetadata    # 元数据

ReceiptItem:
  - name: str                    # 商品名称
  - quantity: Decimal            # 数量
  - unit_price: Decimal          # 单价
  - total_price: Decimal         # 小计
  - category: str                # 商品分类
```

### Excel表格结构

```
Sheet名称: {YYYY-MM-DD}_{商家名称}
示例: 2025-01-20_永辉超市

表格布局:
┌─────────────────────────────────────┐
│ 收据信息                            │  <- 基础信息区 (1-10行)
├─────────────────────────────────────┤
│ 商品明细                            │  <- 商品明细表 (11行起)
│ 序号 | 名称 | 分类 | 数量 | 单价... │
├─────────────────────────────────────┤
│ 金额汇总                            │  <- 汇总信息区
│ 商品小计: xxx                       │
│ 税额: xxx                           │
│ 总计: xxx                           │
└─────────────────────────────────────┘
```

---

## 开发计划

### 时间线

```
Week 1-2:  基础框架搭建
  - 项目初始化
  - 配置管理系统
  - 日志系统
  - 数据模型
  - CLI框架

Week 3-4:  核心功能实现
  - Excel操作模块
  - AI视觉识别
  - OCR备用方案
  - 提取器服务
  - 验证器服务

Week 5-6:  增强功能
  - 添加收据命令
  - 列出记录命令
  - 导出数据命令
  - 初始化命令

Week 7:    测试和优化
  - 单元测试完善
  - 集成测试
  - 性能优化
  - 文档编写
```

### Subagent协作

| Subagent | 负责模块 | 主要任务 |
|----------|---------|---------|
| Subagent 1 | 基础架构 | 配置、日志、数据模型 |
| Subagent 2 | Excel专家 | Excel操作、格式化 |
| Subagent 3 | AI工程师 | AI识别、OCR |
| Subagent 4 | CLI开发者 | 命令行界面、交互 |
| Subagent 5 | 测试工程师 | 测试、质量保证 |

---

## 快速开始

### 1. 安装依赖

```bash
cd /home/bughero/Documents/github/DeepLearning/python/mcp/receipt_manager
pip install -r requirements.txt
```

### 2. 配置API密钥

```bash
export ARK_API_KEY="your-volcengine-api-key"
```

### 3. 初始化配置

```bash
cp config.yaml.example ~/.config/receipt-manager/config.yaml
# 编辑配置文件，设置API密钥等
```

### 4. 运行示例

```bash
# 添加收据
receipt-manager add path/to/receipt.jpg

# 查看记录
receipt-manager list

# 导出数据
receipt-manager export --format csv
```

---

## 项目文件清单

### 文档文件

```
receipt_manager/
├── README.md                    # 项目介绍
├── DESIGN_DOC.md                # 产品设计文档
├── DATA_STRUCTURE.md            # 数据结构设计
├── TECHNICAL_ARCHITECTURE.md    # 技术架构设计
├── IMPLEMENTATION_PLAN.md       # 实施计划
├── PROJECT_SUMMARY.md           # 项目概览 (本文件)
└── config.yaml.example          # 配置文件示例
```

### 代码文件 (待创建)

```
receipt_manager/
├── receipt_manager/
│   ├── __init__.py
│   ├── cli/                    # 命令行界面
│   │   ├── main.py
│   │   ├── commands/
│   │   │   ├── add.py
│   │   │   ├── list.py
│   │   │   ├── export.py
│   │   │   └── init.py
│   │   └── ui/
│   │       ├── interactive.py
│   │       └── display.py
│   ├── core/                   # 核心业务逻辑
│   │   ├── models.py
│   │   ├── extractor.py
│   │   └── validator.py
│   ├── ai/                     # AI识别模块
│   │   ├── vision_client.py
│   │   ├── ocr_engine.py
│   │   └── prompts.py
│   ├── excel/                  # Excel操作模块
│   │   ├── manager.py
│   │   ├── formatter.py
│   │   └── styles.py
│   └── utils/                  # 工具模块
│       ├── config.py
│       └── logger.py
├── tests/                      # 测试文件
│   ├── test_models.py
│   ├── test_extractor.py
│   ├── test_validator.py
│   └── test_excel.py
├── requirements.txt
└── setup.py
```

---

## 下一步行动

### 立即可开始的任务

1. **创建项目结构**
   ```bash
   mkdir -p receipt_manager/{cli,core,ai,excel,utils}
   ```

2. **安装开发依赖**
   ```bash
   pip install click pydantic openpyxl loguru rich
   ```

3. **实现基础模块**
   - 配置管理 (`utils/config.py`)
   - 日志系统 (`utils/logger.py`)
   - 数据模型 (`core/models.py`)

4. **测试基础功能**
   ```bash
   python -m pytest tests/
   ```

### 需要决策的事项

1. **API密钥管理**
   - 是否需要加密存储API密钥？
   - 是否支持多个API密钥轮换？

2. **数据存储**
   - 是否需要数据库支持？
   - 是否需要云端同步？

3. **用户界面**
   - 是否需要Web界面？
   - 是否需要移动端App？

---

## 联系方式

如有问题或建议，请联系：

- **作者**: bughero
- **邮箱**: bughero2012@gmail.com
- **项目路径**: `/home/bughero/Documents/github/DeepLearning/python/mcp/receipt_manager`

---

**文档版本**: v1.0
**创建日期**: 2025-01-20
**最后更新**: 2025-01-20
