"""
采购收据管理工具 - 核心数据模型

用于管理教室采购收据，支持AI识别和Excel导入导出。
"""

from dataclasses import dataclass, field
from typing import List, Optional
from datetime import date
from decimal import Decimal
import json
from pathlib import Path


@dataclass
class PurchaseItem:
    """
    采购商品项

    Attributes:
        sequence: 序号（从1开始）
        name: 商品名称（必填）
        spec: 规格型号（可选）
        unit: 单位（份、个、箱、本、人等）
        quantity: 采购数量
        unit_price: 单价（元）
        amount: 金额（元），自动计算为 quantity × unit_price
        remark: 备注（可选）
    """

    sequence: int
    name: str
    spec: Optional[str] = None
    unit: str = "个"
    quantity: Decimal = Decimal("1")
    unit_price: Decimal = Decimal("0")
    amount: Optional[Decimal] = None
    remark: Optional[str] = None

    def __post_init__(self):
        """自动计算金额"""
        if self.amount is None:
            self.amount = self.quantity * self.unit_price

    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "sequence": self.sequence,
            "name": self.name,
            "spec": self.spec,
            "unit": self.unit,
            "quantity": float(self.quantity),
            "unit_price": float(self.unit_price),
            "amount": float(self.amount or Decimal("0")),
            "remark": self.remark,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "PurchaseItem":
        """从字典创建"""
        return cls(
            sequence=data["sequence"],
            name=data["name"],
            spec=data.get("spec"),
            unit=data.get("unit", "个"),
            quantity=Decimal(str(data["quantity"])),
            unit_price=Decimal(str(data["unit_price"])),
            amount=Decimal(str(data.get("amount", 0))),
            remark=data.get("remark"),
        )


@dataclass
class PurchaseReceipt:
    """
    采购收据

    Attributes:
        title: 主题标题（如"数学资料打印"、"教室布置"）
        delivery_date: 交付日期
        purchaser: 采购方（默认"梁程程妈妈"）
        payment_method: 付款方式（默认"转账"）
        items: 商品明细列表
        recognition_method: 识别方式（ai/ocr/manual）
        confidence: 识别置信度（0-1）
        source_file: 源文件路径
    """

    title: str
    delivery_date: date
    purchaser: str = "梁程程妈妈"
    payment_method: str = "转账"
    items: List[PurchaseItem] = field(default_factory=list)
    recognition_method: str = "manual"
    confidence: float = 1.0
    source_file: Optional[str] = None

    @property
    def sheet_name(self) -> str:
        """
        生成Excel Sheet名称

        格式：主题名称（月-日）
        例如：数学资料打印（1-20）
        """
        month = self.delivery_date.month
        day = self.delivery_date.day
        return f"{self.title}（{month}-{day}）"

    @property
    def total_amount(self) -> Decimal:
        """计算总金额"""
        return sum([item.amount or Decimal("0") for item in self.items], start=Decimal("0"))

    @property
    def item_count(self) -> int:
        """商品数量"""
        return len(self.items)

    @property
    def total_quantity(self) -> Decimal:
        """总数量"""
        return sum([item.quantity or Decimal("0") for item in self.items], start=Decimal("0"))

    def validate(self) -> tuple[bool, List[str]]:
        """
        验证收据数据

        Returns:
            (是否有效, 错误列表)
        """
        errors = []

        # 验证标题
        if not self.title or not self.title.strip():
            errors.append("主题标题不能为空")

        # 验证商品列表
        if not self.items:
            errors.append("商品列表不能为空")
        else:
            for i, item in enumerate(self.items, 1):
                if not item.name or not item.name.strip():
                    errors.append(f"第{i}个商品名称不能为空")
                if not item.unit or not item.unit.strip():
                    errors.append(f"第{i}个商品单位不能为空")
                if item.quantity <= 0:
                    errors.append(f"第{i}个商品数量必须大于0，当前值：{item.quantity}")
                if item.unit_price < 0:
                    errors.append(f"第{i}个商品单价不能为负数，当前值：{item.unit_price}")

                # 验证金额计算
                calculated_amount = item.quantity * item.unit_price
                item_amount = item.amount or Decimal("0")
                if abs(calculated_amount - item_amount) > Decimal("0.01"):
                    errors.append(
                        f"第{i}个商品金额计算错误："
                        f"{item.quantity} × {item.unit_price} = {calculated_amount}，"
                        f"但当前值为 {item_amount}"
                    )

        return len(errors) == 0, errors

    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "title": self.title,
            "delivery_date": self.delivery_date.isoformat(),
            "purchaser": self.purchaser,
            "payment_method": self.payment_method,
            "items": [item.to_dict() for item in self.items],
            "recognition_method": self.recognition_method,
            "confidence": self.confidence,
            "source_file": self.source_file,
            "total_amount": float(self.total_amount),
            "item_count": self.item_count,
        }

    def to_json(self, indent: int = 2) -> str:
        """转换为JSON字符串"""
        return json.dumps(
            self.to_dict(),
            ensure_ascii=False,
            indent=indent,
        )

    @classmethod
    def from_dict(cls, data: dict) -> "PurchaseReceipt":
        """从字典创建"""
        items = [PurchaseItem.from_dict(item_data) for item_data in data.get("items", [])]

        delivery_date = data["delivery_date"]
        if isinstance(delivery_date, str):
            delivery_date = date.fromisoformat(delivery_date)

        return cls(
            title=data["title"],
            delivery_date=delivery_date,
            purchaser=data.get("purchaser", "梁程程妈妈"),
            payment_method=data.get("payment_method", "转账"),
            items=items,
            recognition_method=data.get("recognition_method", "manual"),
            confidence=data.get("confidence", 1.0),
            source_file=data.get("source_file"),
        )

    @classmethod
    def from_json(cls, json_str: str) -> "PurchaseReceipt":
        """从JSON字符串创建"""
        data = json.loads(json_str)
        return cls.from_dict(data)

    def add_item(
        self,
        name: str,
        quantity: Decimal,
        unit_price: Decimal,
        spec: Optional[str] = None,
        unit: str = "个",
        remark: Optional[str] = None,
    ) -> "PurchaseReceipt":
        """
        添加商品项

        Args:
            name: 商品名称
            quantity: 数量
            unit_price: 单价
            spec: 规格型号
            unit: 单位
            remark: 备注

        Returns:
            self，支持链式调用
        """
        sequence = len(self.items) + 1
        item = PurchaseItem(
            sequence=sequence,
            name=name,
            spec=spec,
            unit=unit,
            quantity=quantity,
            unit_price=unit_price,
            remark=remark,
        )
        self.items.append(item)
        return self

    def __str__(self) -> str:
        """字符串表示"""
        return (
            f"PurchaseReceipt(title={self.title}, "
            f"date={self.delivery_date}, "
            f"items={len(self.items)}, "
            f"total={self.total_amount:.2f})"
        )


# 便捷函数
def create_receipt(
    title: str,
    delivery_date: date,
    purchaser: str = "梁程程妈妈",
) -> PurchaseReceipt:
    """
    创建收据

    Args:
        title: 主题标题
        delivery_date: 交付日期
        purchaser: 采购方

    Returns:
        新的PurchaseReceipt实例
    """
    return PurchaseReceipt(
        title=title,
        delivery_date=delivery_date,
        purchaser=purchaser,
    )


def validate_items(items: List[PurchaseItem]) -> tuple[bool, List[str]]:
    """
    验证商品列表

    Args:
        items: 商品列表

    Returns:
        (是否有效, 错误列表)
    """
    errors = []
    for i, item in enumerate(items, 1):
        if not item.name:
            errors.append(f"第{i}个商品名称不能为空")
        if item.quantity <= 0:
            errors.append(f"第{i}个商品数量必须大于0")
        if item.unit_price < 0:
            errors.append(f"第{i}个商品单价不能为负数")

    return len(errors) == 0, errors
