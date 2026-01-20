# 采购收据管理工具 (Receipt Manager)

一个智能的命令行工具，通过AI视觉识别技术自动提取采购收据信息，并将其结构化地记录到Excel文件中。

## 功能特性

- **智能识别**: 使用AI视觉大模型自动识别收据信息
- **多种输入**: 支持图片、扫描件、文本描述
- **Excel管理**: 自动生成和更新Excel表格
- **灵活分类**: 按日期+商家自动创建Sheet
- **批量处理**: 支持批量处理多个收据
- **备用方案**: AI识别失败时提供OCR和手动输入

## 快速开始

### 安装

```bash
# 从源码安装
git clone https://github.com/bughero/DeepLearning.git
cd DeepLearning/python/mcp/receipt_manager
pip install -e .

# 或直接使用pip
pip install receipt-manager
```

### 初始化

```bash
# 初始化配置
receipt-manager init

# 设置API密钥
export ARK_API_KEY="your-api-key"
```

### 基本使用

```bash
# 添加单个收据
receipt-manager add receipt.jpg

# 指定日期和分类
receipt-manager add receipt.jpg --date 2025-01-20 --category "办公用品"

# 批量添加
receipt-manager add *.jpg --batch

# 查看所有记录
receipt-manager list

# 导出数据
receipt-manager export --format csv
```

## 文档

- [产品设计文档](DESIGN_DOC.md) - 完整的产品设计和用户流程
- [数据结构设计](DATA_STRUCTURE.md) - 数据模型和Excel格式定义
- [技术架构文档](TECHNICAL_ARCHITECTURE.md) - 技术架构和模块设计
- [实施计划](IMPLEMENTATION_PLAN.md) - 开发计划和协作方案

## 项目结构

```
receipt_manager/
├── cli/                     # 命令行界面
│   ├── commands/           # 命令实现
│   └── ui/                 # 用户界面
├── core/                   # 核心业务逻辑
│   ├── models.py          # 数据模型
│   ├── extractor.py       # 信息提取器
│   └── validator.py       # 数据验证器
├── ai/                     # AI识别模块
│   ├── vision_client.py   # 视觉大模型客户端
│   └── ocr_engine.py      # OCR引擎
├── excel/                  # Excel操作模块
│   ├── manager.py         # Excel管理器
│   └── formatter.py       # 格式化工具
└── utils/                  # 工具模块
    ├── config.py          # 配置管理
    └── logger.py          # 日志工具
```

## 配置

配置文件位于 `~/.config/receipt-manager/config.yaml`:

```yaml
excel:
  file_path: "~/Documents/采购记录.xlsx"

ai:
  enabled: true
  api_key: "${ARK_API_KEY}"
  model: "doubao-seed-1-6-251015"
  confidence_threshold: 0.8

categories:
  - "办公用品"
  - "餐饮"
  - "交通"
  - "日用品"
  - "其他"
```

## 开发

### 环境设置

```bash
# 创建虚拟环境
python3 -m venv .venv
source .venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 安装开发工具
pip install black mypy pytest pytest-cov
```

### 运行测试

```bash
# 运行所有测试
pytest tests/

# 运行带覆盖率的测试
pytest --cov=receipt_manager --cov-report=html

# 运行特定测试
pytest tests/test_excel.py
```

### 代码格式化

```bash
# 格式化代码
black receipt_manager/

# 排序import
isort receipt_manager/

# 类型检查
mypy receipt_manager/
```

## 技术栈

- **Python 3.10+**
- **Click** - 命令行界面
- **Pydantic** - 数据验证
- **OpenPyXL** - Excel操作
- **火山引擎** - AI视觉识别
- **Tesseract** - OCR识别
- **Loguru** - 日志系统
- **Rich** - 终端美化

## 贡献

欢迎贡献！请查看 [实施计划](IMPLEMENTATION_PLAN.md) 了解如何参与开发。

## 许可证

MIT License

## 联系方式

- 作者: bughero
- 邮箱: bughero2012@gmail.com

---

**版本**: 1.0.0
**最后更新**: 2025-01-20
