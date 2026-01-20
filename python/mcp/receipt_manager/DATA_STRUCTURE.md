# 采购收据管理工具 - 数据结构设计

## 1. 核心数据模型

### 1.1 Receipt (收据)

```python
from dataclasses import dataclass
from typing import List, Optional
from datetime import date
from decimal import Decimal
from enum import Enum


class ReceiptStatus(Enum):
    """收据状态"""
    DRAFT = "draft"           # 草稿
    PENDING = "pending"       # 待确认
    CONFIRMED = "confirmed"   # 已确认
    ARCHIVED = "archived"     # 已归档


class RecognitionMethod(Enum):
    """识别方式"""
    AI_VISION = "ai_vision"           # AI视觉识别
    OCR = "ocr"                       # OCR识别
    MANUAL = "manual"                 # 手动输入
    HYBRID = "hybrid"                 # 混合方式


@dataclass
class ReceiptItem:
    """收据商品项"""
    name: str                    # 商品名称
    quantity: Decimal            # 数量
    unit_price: Decimal          # 单价
    total_price: Decimal         # 小计
    category: Optional[str] = None   # 商品分类
    sku: Optional[str] = None        # 商品编码
    description: Optional[str] = None  # 描述信息

    def __post_init__(self):
        """自动计算小计"""
        if self.total_price is None:
            self.total_price = self.quantity * self.unit_price

    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "name": self.name,
            "quantity": float(self.quantity),
            "unit_price": float(self.unit_price),
            "total_price": float(self.total_price),
            "category": self.category,
            "sku": self.sku,
            "description": self.description,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ReceiptItem":
        """从字典创建"""
        return cls(
            name=data["name"],
            quantity=Decimal(str(data["quantity"])),
            unit_price=Decimal(str(data["unit_price"])),
            total_price=Decimal(str(data.get("total_price", 0))),
            category=data.get("category"),
            sku=data.get("sku"),
            description=data.get("description"),
        )


@dataclass
class ReceiptMetadata:
    """收据元数据"""
    original_file_path: Optional[str] = None   # 原始文件路径
    archived_file_path: Optional[str] = None   # 归档文件路径
    recognition_method: RecognitionMethod = RecognitionMethod.MANUAL
    recognition_confidence: float = 0.0        # 识别置信度
    recognized_at: Optional[str] = None        # 识别时间
    verified_at: Optional[str] = None          # 验证时间
    verified_by: Optional[str] = None          # 验证人
    notes: Optional[str] = None                # 备注信息
    tags: List[str] = None                     # 标签

    def __post_init__(self):
        if self.tags is None:
            self.tags = []


@dataclass
class Receipt:
    """收据主体"""
    # 基本信息
    receipt_id: str                          # 收据唯一ID
    date: date                               # 收据日期
    merchant: str                            # 商家名称
    merchant_address: Optional[str] = None   # 商家地址
    merchant_phone: Optional[str] = None     # 商家电话

    # 金额信息
    subtotal: Decimal                        # 小计
    tax: Decimal = Decimal("0.00")           # 税额
    discount: Decimal = Decimal("0.00")      # 折扣
    total: Decimal                           # 总计

    # 商品信息
    items: List[ReceiptItem] = None          # 商品列表

    # 支付信息
    payment_method: Optional[str] = None     # 支付方式
    transaction_id: Optional[str] = None     # 交易ID

    # 分类和标签
    category: Optional[str] = None           # 收据分类
    project: Optional[str] = None            # 项目归属
    department: Optional[str] = None         # 部门归属

    # 状态和元数据
    status: ReceiptStatus = ReceiptStatus.DRAFT
    metadata: ReceiptMetadata = None

    def __post_init__(self):
        if self.items is None:
            self.items = []
        if self.metadata is None:
            self.metadata = ReceiptMetadata()

    @property
    def sheet_name(self) -> str:
        """生成Excel Sheet名称"""
        # 格式: YYYY-MM-DD_商家名称
        date_str = self.date.strftime("%Y-%m-%d")
        # 清理商家名称中的特殊字符
        clean_merchant = "".join(
            c for c in self.merchant
            if c.isalnum() or c in (" ", "-", "_")
        ).strip()
        return f"{date_str}_{clean_merchant}"

    @property
    def item_count(self) -> int:
        """商品数量"""
        return len(self.items)

    @property
    def total_quantity(self) -> Decimal:
        """总数量"""
        return sum(item.quantity for item in self.items)

    def validate(self) -> tuple[bool, List[str]]:
        """验证收据数据"""
        errors = []

        # 验证基本信息
        if not self.merchant:
            errors.append("商家名称不能为空")

        if self.total <= 0:
            errors.append("总金额必须大于0")

        # 验证商品信息
        if not self.items:
            errors.append("商品列表不能为空")

        # 验证金额一致性
        calculated_total = (
            self.subtotal + self.tax - self.discount
        )
        if abs(calculated_total - self.total) > Decimal("0.01"):
            errors.append(
                f"金额不一致: 计算值({calculated_total}) != 总计({self.total})"
            )

        # 验证商品小计
        items_total = sum(item.total_price for item in self.items)
        if abs(items_total - self.subtotal) > Decimal("0.01"):
            errors.append(
                f"商品小计不一致: 计算值({items_total}) != 小计({self.subtotal})"
            )

        return len(errors) == 0, errors

    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "receipt_id": self.receipt_id,
            "date": self.date.isoformat(),
            "merchant": self.merchant,
            "merchant_address": self.merchant_address,
            "merchant_phone": self.merchant_phone,
            "subtotal": float(self.subtotal),
            "tax": float(self.tax),
            "discount": float(self.discount),
            "total": float(self.total),
            "items": [item.to_dict() for item in self.items],
            "payment_method": self.payment_method,
            "transaction_id": self.transaction_id,
            "category": self.category,
            "project": self.project,
            "department": self.department,
            "status": self.status.value,
            "metadata": {
                "original_file_path": self.metadata.original_file_path,
                "archived_file_path": self.metadata.archived_file_path,
                "recognition_method": self.metadata.recognition_method.value,
                "recognition_confidence": self.metadata.recognition_confidence,
                "recognized_at": self.metadata.recognized_at,
                "verified_at": self.metadata.verified_at,
                "verified_by": self.metadata.verified_by,
                "notes": self.metadata.notes,
                "tags": self.metadata.tags,
            }
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Receipt":
        """从字典创建"""
        items = [
            ReceiptItem.from_dict(item_data)
            for item_data in data.get("items", [])
        ]
        metadata_data = data.get("metadata", {})
        metadata = ReceiptMetadata(
            original_file_path=metadata_data.get("original_file_path"),
            archived_file_path=metadata_data.get("archived_file_path"),
            recognition_method=RecognitionMethod(
                metadata_data.get("recognition_method", "manual")
            ),
            recognition_confidence=metadata_data.get("recognition_confidence", 0.0),
            recognized_at=metadata_data.get("recognized_at"),
            verified_at=metadata_data.get("verified_at"),
            verified_by=metadata_data.get("verified_by"),
            notes=metadata_data.get("notes"),
            tags=metadata_data.get("tags", []),
        )

        return cls(
            receipt_id=data["receipt_id"],
            date=date.fromisoformat(data["date"]),
            merchant=data["merchant"],
            merchant_address=data.get("merchant_address"),
            merchant_phone=data.get("merchant_phone"),
            subtotal=Decimal(str(data["subtotal"])),
            tax=Decimal(str(data.get("tax", 0))),
            discount=Decimal(str(data.get("discount", 0))),
            total=Decimal(str(data["total"])),
            items=items,
            payment_method=data.get("payment_method"),
            transaction_id=data.get("transaction_id"),
            category=data.get("category"),
            project=data.get("project"),
            department=data.get("department"),
            status=ReceiptStatus(data.get("status", "draft")),
            metadata=metadata,
        )
```

### 1.2 AI Recognition Result (AI识别结果)

```python
@dataclass
class AIRecognitionResult:
    """AI识别结果"""
    success: bool                              # 是否成功
    confidence: float                          # 置信度 (0-1)
    receipt: Optional[Receipt] = None          # 识别的收据数据
    raw_response: Optional[str] = None         # 原始响应
    errors: List[str] = None                   # 错误信息
    processing_time: float = 0.0               # 处理时间(秒)

    def __post_init__(self):
        if self.errors is None:
            self.errors = []

    @property
    def is_reliable(self) -> bool:
        """判断识别结果是否可靠"""
        return self.success and self.confidence >= 0.8

    @property
    def needs_verification(self) -> bool:
        """判断是否需要人工验证"""
        return self.success and 0.5 <= self.confidence < 0.8


@dataclass
class RecognitionRequest:
    """识别请求"""
    image_path: str                            # 图片路径
    date_hint: Optional[date] = None           # 日期提示
    merchant_hint: Optional[str] = None        # 商家提示
    category_hint: Optional[str] = None        # 分类提示
    use_ocr_fallback: bool = True              # 是否使用OCR备用
```

---

## 2. Excel表格结构

### 2.1 Sheet命名规则

```
格式: {YYYY-MM-DD}_{商家名称}
示例:
  - 2025-01-20_永辉超市
  - 2025-01-21_晨光文具
  - 2025-01-22_餐饮招待
```

### 2.2 表格列结构

#### 2.2.1 基础信息区 (前10行)

| 行号 | 列A | 列B | 列C | 列D | 列E | 列F |
|-----|-----|-----|-----|-----|-----|-----|
| 1 | **收据信息** | | | | | |
| 2 | 收据编号: | {receipt_id} | | | | |
| 3 | 收据日期: | {date} | | | | |
| 4 | 商家名称: | {merchant} | | | | |
| 5 | 商家地址: | {merchant_address} | | | | |
| 6 | 商家电话: | {merchant_phone} | | | | |
| 7 | 收据分类: | {category} | | | | |
| 8 | 项目归属: | {project} | | | | |
| 9 | 部门归属: | {department} | | | | |
| 10 | 备注: | {notes} | | | | |

#### 2.2.2 商品明细区 (第11行起)

| 行号 | 列A | 列B | 列C | 列D | 列E | 列F | 列G | 列H |
|-----|-----|-----|-----|-----|-----|-----|-----|-----|
| 11 | **商品明细** | | | | | | | |
| 12 | 序号 | 商品名称 | 商品分类 | 规格/SKU | 数量 | 单价 | 小计 | 备注 |
| 13 | 1 | {item.name} | {item.category} | {item.sku} | {item.quantity} | {item.unit_price} | {item.total_price} | {item.description} |
| 14 | 2 | ... | ... | ... | ... | ... | ... | ... |
| ... | ... | ... | ... | ... | ... | ... | ... | ... |

#### 2.2.3 汇总信息区 (商品明细后)

| 行号 | 列A | 列B | 列C | 列D | 列E |
|-----|-----|-----|-----|-----|-----|
| N | **金额汇总** | | | | |
| N+1 | 商品小计: | {subtotal} | | | |
| N+2 | 税额: | {tax} | | | |
| N+3 | 折扣: | {discount} | | | |
| N+4 | 总计: | {total} | | | |
| N+5 | | | | | |
| N+6 | **支付信息** | | | | |
| N+7 | 支付方式: | {payment_method} | | | |
| N+8 | 交易编号: | {transaction_id} | | | |
| N+9 | | | | | |
| N+10 | **识别信息** | | | | |
| N+11 | 识别方式: | {recognition_method} | | | |
| N+12 | 识别置信度: | {recognition_confidence} | | | |
| N+13 | 识别时间: | {recognized_at} | | | |
| N+14 | 验证时间: | {verified_at} | | | |

### 2.3 格式化规则

```python
# 列宽设置
COLUMN_WIDTHS = {
    "A": 15,  # 序号/标签
    "B": 30,  # 商品名称/值
    "C": 15,  # 分类/值
    "D": 15,  # SKU
    "E": 10,  # 数量
    "F": 12,  # 单价
    "G": 12,  # 小计
    "H": 20,  # 备注
}

# 单元格样式
STYLES = {
    "header": {
        "font": {"bold": True, "size": 14},
        "fill": {"fgColor": "4472C4"},
        "alignment": {"horizontal": "center", "vertical": "center"},
    },
    "label": {
        "font": {"bold": True, "size": 11},
        "alignment": {"horizontal": "right", "vertical": "center"},
    },
    "value": {
        "font": {"size": 11},
        "alignment": {"horizontal": "left", "vertical": "center"},
    },
    "amount": {
        "font": {"size": 11},
        "alignment": {"horizontal": "right", "vertical": "center"},
        "number_format": '"¥"#,##0.00',
    },
    "total": {
        "font": {"bold": True, "size": 12},
        "fill": {"fgColor": "E7E6E6"},
        "alignment": {"horizontal": "right", "vertical": "center"},
        "number_format": '"¥"#,##0.00',
    },
}
```

### 2.4 Excel文件结构

```
采购记录.xlsx
├── 概览 (Overview Sheet)
│   ├── 统计汇总
│   └── 最近记录
├── 2025-01-20_永辉超市
├── 2025-01-21_晨光文具
├── 2025-01-22_餐饮招待
└── ...
```

#### 概览Sheet结构

| 列A | 列B | 列C | 列D | 列E |
|-----|-----|-----|-----|-----|
| **统计汇总** | | | | |
| 总收据数: | {count} | | | |
| 总金额: | {total_amount} | | | |
| 本月收据数: | {month_count} | | | |
| 本月金额: | {month_amount} | | | |
| | | | | |
| **最近记录** | | | | |
| 日期 | 商家 | 金额 | 分类 | Sheet |
| {date} | {merchant} | {total} | {category} | {sheet_name} |
| ... | ... | ... | ... | ... |

---

## 3. 配置数据结构

### 3.1 Application Config (应用配置)

```python
from pathlib import Path
from typing import List, Optional
from pydantic import BaseModel, Field


class ExcelConfig(BaseModel):
    """Excel配置"""
    file_path: Path = Field(
        default=Path("~/Documents/采购记录.xlsx"),
        description="Excel文件路径"
    )
    template_path: Optional[Path] = Field(
        default=None,
        description="Excel模板文件路径"
    )
    auto_backup: bool = Field(
        default=True,
        description="是否自动备份"
    )
    backup_count: int = Field(
        default=5,
        description="保留备份数量"
    )


class AIConfig(BaseModel):
    """AI配置"""
    enabled: bool = Field(default=True, description="是否启用AI")
    provider: str = Field(
        default="volcengine",
        description="AI服务提供商"
    )
    api_key: str = Field(
        default="",
        description="API密钥"
    )
    model: str = Field(
        default="doubao-seed-1-6-251015",
        description="模型名称"
    )
    confidence_threshold: float = Field(
        default=0.8,
        ge=0.0,
        le=1.0,
        description="置信度阈值"
    )
    max_retries: int = Field(
        default=3,
        description="最大重试次数"
    )
    timeout: int = Field(
        default=120,
        description="超时时间(秒)"
    )


class OCRConfig(BaseModel):
    """OCR配置"""
    enabled: bool = Field(default=True, description="是否启用OCR")
    tesseract_path: Optional[Path] = Field(
        default=None,
        description="Tesseract可执行文件路径"
    )
    language: str = Field(
        default="chi_sim+eng",
        description="OCR语言"
    )
    preprocessing: bool = Field(
        default=True,
        description="是否进行图像预处理"
    )


class ValidationConfig(BaseModel):
    """验证配置"""
    required_fields: List[str] = Field(
        default=["date", "merchant", "total", "items"],
        description="必填字段"
    )
    date_format: str = Field(
        default="%Y-%m-%d",
        description="日期格式"
    )
    strict_amount_validation: bool = Field(
        default=True,
        description="严格金额验证"
    )
    allow_negative_amount: bool = Field(
        default=False,
        description="允许负金额"
    )


class StorageConfig(BaseModel):
    """存储配置"""
    archive_path: Path = Field(
        default=Path("~/Documents/receipts/archive"),
        description="归档路径"
    )
    keep_original: bool = Field(
        default=True,
        description="保留原始文件"
    )
    compress_archive: bool = Field(
        default=False,
        description="压缩归档"
    )
    archive_format: str = Field(
        default="{date}_{merchant}_{id}",
        description="归档命名格式"
    )


class CategoryConfig(BaseModel):
    """分类配置"""
    default_categories: List[str] = Field(
        default=[
            "办公用品",
            "餐饮",
            "交通",
            "日用品",
            "其他",
        ],
        description="默认分类"
    )
    auto_classify: bool = Field(
        default=True,
        description="自动分类"
    )


class UIConfig(BaseModel):
    """界面配置"""
    show_progress: bool = Field(default=True, description="显示进度")
    color_output: bool = Field(default=True, description="彩色输出")
    confirm_threshold: float = Field(
        default=0.8,
        description="需要确认的置信度阈值"
    )
    editor: Optional[str] = Field(
        default=None,
        description="外部编辑器"
    )


class AppConfig(BaseModel):
    """应用配置"""
    excel: ExcelConfig = Field(default_factory=ExcelConfig)
    ai: AIConfig = Field(default_factory=AIConfig)
    ocr: OCRConfig = Field(default_factory=OCRConfig)
    validation: ValidationConfig = Field(default_factory=ValidationConfig)
    storage: StorageConfig = Field(default_factory=StorageConfig)
    category: CategoryConfig = Field(default_factory=CategoryConfig)
    ui: UIConfig = Field(default_factory=UIConfig)

    class Config:
        env_nested_delimiter = "__"
        env_prefix = "RECEIPT_MANAGER_"

    @classmethod
    def from_yaml(cls, path: Path) -> "AppConfig":
        """从YAML文件加载配置"""
        import yaml
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        return cls(**data)

    def to_yaml(self, path: Path) -> None:
        """保存配置到YAML文件"""
        import yaml
        with open(path, "w", encoding="utf-8") as f:
            yaml.dump(
                self.model_dump(mode="python"),
                f,
                allow_unicode=True,
                default_flow_style=False,
            )
```

---

## 4. 数据库模型 (可选扩展)

如果未来需要使用数据库存储：

```python
from sqlalchemy import Column, String, DateTime, Numeric, Integer, Text, ForeignKey, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime

Base = declarative_base()


class ReceiptDB(Base):
    """收据数据库表"""
    __tablename__ = "receipts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    receipt_id = Column(String(50), unique=True, nullable=False, index=True)
    date = Column(DateTime, nullable=False, index=True)
    merchant = Column(String(200), nullable=False, index=True)
    merchant_address = Column(String(500))
    merchant_phone = Column(String(50))

    subtotal = Column(Numeric(10, 2), nullable=False)
    tax = Column(Numeric(10, 2), default=0)
    discount = Column(Numeric(10, 2), default=0)
    total = Column(Numeric(10, 2), nullable=False)

    payment_method = Column(String(50))
    transaction_id = Column(String(100))

    category = Column(String(100), index=True)
    project = Column(String(100))
    department = Column(String(100))

    status = Column(Enum(ReceiptStatus), default=ReceiptStatus.DRAFT, index=True)

    original_file_path = Column(String(500))
    archived_file_path = Column(String(500))
    recognition_method = Column(Enum(RecognitionMethod))
    recognition_confidence = Column(Numeric(3, 2))
    recognized_at = Column(DateTime)
    verified_at = Column(DateTime)
    verified_by = Column(String(100))
    notes = Column(Text)
    tags = Column(Text)  # JSON array as string

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ReceiptItemDB(Base):
    """收据商品项数据库表"""
    __tablename__ = "receipt_items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    receipt_id = Column(UUID(as_uuid=True), ForeignKey("receipts.id"), nullable=False)
    sequence = Column(Integer, nullable=False)

    name = Column(String(200), nullable=False)
    category = Column(String(100))
    sku = Column(String(100))
    description = Column(Text)

    quantity = Column(Numeric(10, 2), nullable=False)
    unit_price = Column(Numeric(10, 2), nullable=False)
    total_price = Column(Numeric(10, 2), nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
```

---

## 5. 数据序列化

### 5.1 JSON序列化

```python
import json
from decimal import Decimal
from datetime import date


class ReceiptEncoder(json.JSONEncoder):
    """收据JSON编码器"""

    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        if isinstance(obj, date):
            return obj.isoformat()
        if isinstance(obj, (ReceiptStatus, RecognitionMethod)):
            return obj.value
        return super().default(obj)


def receipt_to_json(receipt: Receipt) -> str:
    """收据转JSON"""
    return json.dumps(receipt.to_dict(), cls=ReceiptEncoder, ensure_ascii=False, indent=2)


def receipt_from_json(json_str: str) -> Receipt:
    """JSON转收据"""
    data = json.loads(json_str)
    return Receipt.from_dict(data)
```

### 5.2 CSV导出

```python
import csv
from io import StringIO


def receipts_to_csv(receipts: List[Receipt]) -> str:
    """收据列表转CSV"""
    output = StringIO()
    writer = csv.writer(output)

    # 写入表头
    writer.writerow([
        "收据ID", "日期", "商家", "分类",
        "小计", "税额", "折扣", "总计",
        "商品数量", "状态"
    ])

    # 写入数据
    for receipt in receipts:
        writer.writerow([
            receipt.receipt_id,
            receipt.date.isoformat(),
            receipt.merchant,
            receipt.category or "",
            float(receipt.subtotal),
            float(receipt.tax),
            float(receipt.discount),
            float(receipt.total),
            receipt.item_count,
            receipt.status.value,
        ])

    return output.getvalue()
```

---

## 6. 数据验证规则

### 6.1 字段验证规则

```python
from pydantic import field_validator, model_validator
from pydantic.dataclasses import dataclass


class ReceiptValidationRules:
    """收据验证规则"""

    @staticmethod
    def validate_merchant(value: str) -> str:
        """验证商家名称"""
        if not value or not value.strip():
            raise ValueError("商家名称不能为空")
        if len(value) > 200:
            raise ValueError("商家名称不能超过200字符")
        return value.strip()

    @staticmethod
    def validate_amount(value: Decimal) -> Decimal:
        """验证金额"""
        if value < 0:
            raise ValueError("金额不能为负数")
        if value.as_tuple().exponent < -2:
            raise ValueError("金额最多保留2位小数")
        return value

    @staticmethod
    def validate_date(value: date) -> date:
        """验证日期"""
        if value > date.today():
            raise ValueError("收据日期不能是未来日期")
        if value.year < 2000:
            raise ValueError("收据日期年份不能早于2000年")
        return value

    @staticmethod
    def validate_items(items: List[ReceiptItem]) -> List[ReceiptItem]:
        """验证商品列表"""
        if not items:
            raise ValueError("商品列表不能为空")
        for i, item in enumerate(items):
            if not item.name:
                raise ValueError(f"第{i+1}个商品名称不能为空")
            if item.quantity <= 0:
                raise ValueError(f"第{i+1}个商品数量必须大于0")
            if item.unit_price < 0:
                raise ValueError(f"第{i+1}个商品单价不能为负数")
        return items
```

### 6.2 业务规则验证

```python
class BusinessRules:
    """业务规则验证"""

    @staticmethod
    def validate_amount_consistency(receipt: Receipt) -> bool:
        """验证金额一致性"""
        calculated_total = receipt.subtotal + receipt.tax - receipt.discount
        return abs(calculated_total - receipt.total) <= Decimal("0.01")

    @staticmethod
    def validate_item_totals(receipt: Receipt) -> bool:
        """验证商品小计"""
        items_total = sum(item.total_price for item in receipt.items)
        return abs(items_total - receipt.subtotal) <= Decimal("0.01")

    @staticmethod
    def detect_duplicate_receipt(
        existing: List[Receipt],
        new_receipt: Receipt
    ) -> Optional[Receipt]:
        """检测重复收据"""
        for receipt in existing:
            if (receipt.date == new_receipt.date and
                receipt.merchant == new_receipt.merchant and
                abs(receipt.total - new_receipt.total) < Decimal("0.01")):
                return receipt
        return None
```

---

## 7. 数据访问层接口

```python
from abc import ABC, abstractmethod
from typing import List, Optional


class IReceiptRepository(ABC):
    """收据仓储接口"""

    @abstractmethod
    async def save(self, receipt: Receipt) -> Receipt:
        """保存收据"""
        pass

    @abstractmethod
    async def find_by_id(self, receipt_id: str) -> Optional[Receipt]:
        """根据ID查找收据"""
        pass

    @abstractmethod
    async def find_by_date(
        self,
        start_date: date,
        end_date: date
    ) -> List[Receipt]:
        """根据日期范围查找收据"""
        pass

    @abstractmethod
    async def find_by_merchant(self, merchant: str) -> List[Receipt]:
        """根据商家查找收据"""
        pass

    @abstractmethod
    async def find_by_category(self, category: str) -> List[Receipt]:
        """根据分类查找收据"""
        pass

    @abstractmethod
    async def list_all(
        self,
        limit: int = 100,
        offset: int = 0
    ) -> List[Receipt]:
        """列出所有收据"""
        pass

    @abstractmethod
    async def update(self, receipt: Receipt) -> Receipt:
        """更新收据"""
        pass

    @abstractmethod
    async def delete(self, receipt_id: str) -> bool:
        """删除收据"""
        pass


class IExcelRepository(ABC):
    """Excel仓储接口"""

    @abstractmethod
    def create_sheet(self, receipt: Receipt) -> None:
        """创建Sheet"""
        pass

    @abstractmethod
    def update_sheet(self, receipt: Receipt) -> None:
        """更新Sheet"""
        pass

    @abstractmethod
    def sheet_exists(self, sheet_name: str) -> bool:
        """检查Sheet是否存在"""
        pass

    @abstractmethod
    def get_overview_data(self) -> dict:
        """获取概览数据"""
        pass

    @abstractmethod
    def update_overview(self) -> None:
        """更新概览Sheet"""
        pass
```

---

**文档版本**: v1.0
**最后更新**: 2025-01-20
