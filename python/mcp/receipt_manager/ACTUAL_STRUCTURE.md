# 采购收据管理工具 - 实际Excel结构适配

## 实际Excel结构分析

### 文件信息
- **文件名**: `309 采购明细.xlsx`
- **用途**: 教室采购管理（采购方：梁程程妈妈）

### Sheet命名规则

```
格式：{主题名称}({月}-{日}) 或 {主题名称}（{月}-{日}）
示例：
  - 9月份开学教室布置
  - 打印资料（9-2）
  - 磁链公益（11-10）
  - 数学资料打印（11-15）
```

**命名模式**：
- 主题名称 + 可选的日期括号
- 日期格式：月-日（如 9-2, 11-10）
- 括号类型：英文()或中文（）都支持

### Sheet布局结构

```
行号  | A列          | B列          | C列          | D列     | E列        | F列          | G列          | H列     |
------|-------------|-------------|-------------|---------|-----------|-------------|-------------|---------|
1     | 主题标题    |             |             |         |           |             |             |         |
2     | 采购方：_________________ 联系方式：   | 梁程程妈妈 |         |           |             |             |         |
3     | (同第2行，通常为空)                      |         |           |             |             |             |
4     | 序号        | 商品名称    | 规格型号    | 单位    | 采购数量  | 单价（元）  | 金额（元）  | 备注    |
5     | 1           | 商品1       | 规格1       | 个      | 10        | 5.00        | =E5*F5      |         |
6     | 2           | 商品2       | 规格2       | 本      | 20        | 2.50        | =E6*F6      |         |
...   | ...         | ...         | ...         | ...     | ...       | ...         | ...         | ...     |
N-1   |             | 总计金额    |             |         |           |             | =SUM(G5:GN) |         |
N     | 交付日期：YYYY-M-D    付款方式：转账                                                            |         |
```

### 固定值配置

| 字段 | 值 | 说明 |
|-----|---|------|
| 采购方 | 梁程程妈妈 | 固定值 |
| 付款方式 | 转账 | 固定值 |
| 交付日期格式 | YYYY-M-D | 如 2025-1-20 |
| 表格宽度 | 20列（A-T） | 固定 |

### 数据列定义

| 列号 | 列名 | 类型 | 必填 | 说明 |
|-----|------|------|------|------|
| A | 序号 | 数字 | 是 | 自动递增 |
| B | 商品名称 | 文本 | 是 | 必填 |
| C | 规格型号 | 文本 | 否 | 可选 |
| D | 单位 | 文本 | 是 | 份、个、箱、本、人等 |
| E | 采购数量 | 数字 | 是 | 正整数或小数 |
| F | 单价（元） | 数字 | 是 | 最多2位小数 |
| G | 金额（元） | 公式 | 是 | =E*F |
| H | 备注 | 文本 | 否 | 可选 |

### 单元格公式

- **金额计算**: `G列 = E列 × F列`
- **总计金额**: `G{N-1} = SUM(G5:G{N-2})`

---

## 数据模型更新

### Receipt (收据)

```python
from dataclasses import dataclass
from typing import List, Optional
from datetime import date
from decimal import Decimal


@dataclass
class PurchaseItem:
    """采购商品项"""
    sequence: int              # 序号
    name: str                  # 商品名称
    spec: Optional[str] = None  # 规格型号
    unit: str = "个"           # 单位
    quantity: Decimal = Decimal("1")  # 采购数量
    unit_price: Decimal = Decimal("0")  # 单价
    amount: Optional[Decimal] = None  # 金额（自动计算）
    remark: Optional[str] = None  # 备注

    def __post_init__(self):
        """自动计算金额"""
        if self.amount is None:
            self.amount = self.quantity * self.unit_price


@dataclass
class PurchaseReceipt:
    """采购收据"""
    # 基本信息
    title: str                 # 主题标题（Sheet名称）
    delivery_date: date        # 交付日期

    # 固定值
    purchaser: str = "梁程程妈妈"  # 采购方
    payment_method: str = "转账"   # 付款方式

    # 商品明细
    items: List[PurchaseItem] = None

    # 识别信息
    recognition_method: str = "manual"  # 识别方式：ai/ocr/manual
    confidence: float = 1.0            # 识别置信度
    source_file: Optional[str] = None  # 源文件路径

    def __post_init__(self):
        if self.items is None:
            self.items = []

    @property
    def sheet_name(self) -> str:
        """生成Sheet名称"""
        # 格式：主题名称(月-日) 或 主题名称（月-日）
        month = self.delivery_date.month
        day = self.delivery_date.day
        return f"{self.title}（{month}-{day}）"

    @property
    def total_amount(self) -> Decimal:
        """计算总金额"""
        return sum(item.amount for item in self.items)

    def validate(self) -> tuple[bool, List[str]]:
        """验证数据"""
        errors = []

        if not self.title:
            errors.append("主题标题不能为空")

        if not self.items:
            errors.append("商品列表不能为空")

        for i, item in enumerate(self.items, 1):
            if not item.name:
                errors.append(f"第{i}个商品名称不能为空")
            if not item.unit:
                errors.append(f"第{i}个商品单位不能为空")
            if item.quantity <= 0:
                errors.append(f"第{i}个商品数量必须大于0")
            if item.unit_price < 0:
                errors.append(f"第{i}个商品单价不能为负数")

        return len(errors) == 0, errors
```

---

## AI识别Prompt模板

### 收据识别Prompt

```python
RECEIPT_RECOGNITION_PROMPT = """请仔细分析这张采购收据图片，提取出所有关键信息。

请提取以下信息并以JSON格式输出：

1. 主题标题: 这次采购的主题名称（如"数学资料打印"、"教室布置"等）

2. 交付日期: 收据上的日期（格式：YYYY-M-D，如2025-1-20）

3. 商品清单（items数组）:
   每个商品包含：
   - name: 商品名称
   - spec: 规格型号（如果有）
   - unit: 单位（份、个、箱、本、人等）
   - quantity: 数量（数字）
   - unit_price: 单价（数字）
   - amount: 金额（数字，通常等于数量×单价）
   - remark: 备注（如果有）

输出格式示例：
```json
{
  "title": "数学资料打印",
  "delivery_date": "2025-1-20",
  "items": [
    {
      "sequence": 1,
      "name": "数学练习册",
      "spec": "A4",
      "unit": "本",
      "quantity": 30,
      "unit_price": 5.00,
      "amount": 150.00,
      "remark": ""
    },
    {
      "sequence": 2,
      "name": "试卷纸",
      "spec": "8开",
      "unit": "份",
      "quantity": 50,
      "unit_price": 0.50,
      "amount": 25.00,
      "remark": ""
    }
  ],
  "confidence": 0.95
}
```

注意事项：
1. 主题标题要简洁明了
2. 日期格式必须是YYYY-M-D（如2025-1-20，不是2025-01-20）
3. 单位必须是常见的：份、个、箱、本、人、套、张、支等
4. 置信度（confidence）表示识别的可靠程度（0-1之间的数字）
5. 只输出JSON，不要有其他说明文字
"""
```

---

## Excel操作更新

### 创建Sheet的步骤

1. **写入标题（第1行）**
   - 合并A1:T1
   - 值：主题标题

2. **写入采购方信息（第2行）**
   - A2: `采购方：_____________________ 联系方式：`
   - B2: `梁程程妈妈`

3. **写入表头（第4行）**
   - A4:H4 分别为：序号、商品名称、规格型号、单位、采购数量、单价（元）、金额（元）、备注

4. **写入商品明细（第5行起）**
   - 每个商品一行
   - G列设置公式：`=E{n}*F{n}`

5. **写入总计（倒数第2行）**
   - A: `总计金额`
   - G: `=SUM(G5:G{last_row-1})`

6. **写入交付信息（最后1行）**
   - A: `交付日期：YYYY-M-D    付款方式：转账`

### 读取Sheet的步骤

1. **读取基本信息**
   - 标题：A1
   - 采购方：B2
   - 交付日期：从最后一行提取

2. **读取商品明细**
   - 从第5行开始到倒数第3行
   - 提取A-H列的数据

3. **读取总计**
   - 倒数第2行的G列

---

## CLI命令更新

### 添加收据

```bash
# 添加收据（AI识别）
receipt-manager add receipt.jpg

# 指定主题和日期
receipt-manager add receipt.jpg --title "数学资料打印" --date "2025-1-20"

# 手动输入模式
receipt-manager add --manual

# 批量处理
receipt-manager add *.jpg --batch
```

### 查看记录

```bash
# 列出所有Sheet
receipt-manager list

# 按主题搜索
receipt-manager list --title "打印"

# 按日期范围
receipt-manager list --from "2025-1-1" --to "2025-1-31"
```

### 导出数据

```bash
# 导出为JSON
receipt-manager export --format json

# 生成统计报告
receipt-manager export --report
```

---

## 配置文件更新

```yaml
# config.yaml
excel:
  file_path: "~/Documents/309 采购明细.xlsx"
  template_path: null
  auto_backup: true

  # 固定值配置
  purchaser: "梁程程妈妈"
  payment_method: "转账"

ai:
  enabled: true
  api_key: "${ARK_API_KEY}"
  model: "doubao-seed-1-6-251015"
  confidence_threshold: 0.8
  max_retries: 3
  timeout: 120

ocr:
  enabled: true
  language: "chi_sim+eng"
  preprocessing: true

validation:
  strict_amount_validation: true
  allow_negative_amount: false

ui:
  show_progress: true
  color_output: true
  confirm_threshold: 0.8
```

---

**文档版本**: v2.0 (适配实际Excel结构)
**最后更新**: 2025-01-20
