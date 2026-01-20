"""
采购收据管理工具 - 单元测试
"""

import pytest
from datetime import date
from decimal import Decimal
from pathlib import Path

from receipt_manager import PurchaseReceipt, PurchaseItem, create_receipt


class TestPurchaseItem:
    """测试商品项"""

    def test_create_item(self):
        """测试创建商品"""
        item = PurchaseItem(
            sequence=1,
            name="测试商品",
            quantity=Decimal("10"),
            unit_price=Decimal("5.5"),
        )

        assert item.sequence == 1
        assert item.name == "测试商品"
        assert item.quantity == Decimal("10")
        assert item.unit_price == Decimal("5.5")
        assert item.amount == Decimal("55")  # 自动计算

    def test_item_to_dict(self):
        """测试商品转字典"""
        item = PurchaseItem(
            sequence=1,
            name="测试商品",
            quantity=Decimal("10"),
            unit_price=Decimal("5.5"),
        )

        data = item.to_dict()

        assert data["sequence"] == 1
        assert data["name"] == "测试商品"
        assert data["quantity"] == 10.0
        assert data["unit_price"] == 5.5
        assert data["amount"] == 55.0

    def test_item_from_dict(self):
        """测试从字典创建商品"""
        data = {
            "sequence": 1,
            "name": "测试商品",
            "quantity": 10.0,
            "unit_price": 5.5,
            "amount": 55.0,
        }

        item = PurchaseItem.from_dict(data)

        assert item.sequence == 1
        assert item.name == "测试商品"
        assert item.quantity == Decimal("10")
        assert item.unit_price == Decimal("5.5")


class TestPurchaseReceipt:
    """测试收据"""

    def test_create_receipt(self):
        """测试创建收据"""
        receipt = create_receipt(
            title="测试采购",
            delivery_date=date(2025, 1, 20),
        )

        assert receipt.title == "测试采购"
        assert receipt.delivery_date == date(2025, 1, 20)
        assert receipt.purchaser == "梁程程妈妈"
        assert receipt.payment_method == "转账"
        assert len(receipt.items) == 0

    def test_sheet_name(self):
        """测试Sheet名称生成"""
        receipt = create_receipt(
            title="数学资料打印",
            delivery_date=date(2025, 1, 20),
        )

        assert receipt.sheet_name == "数学资料打印（1-20）"

    def test_add_item(self):
        """测试添加商品"""
        receipt = create_receipt(
            title="测试采购",
            delivery_date=date(2025, 1, 20),
        )

        receipt.add_item(
            name="商品1",
            quantity=Decimal("10"),
            unit_price=Decimal("5"),
        )

        assert len(receipt.items) == 1
        assert receipt.items[0].name == "商品1"
        assert receipt.items[0].sequence == 1

        receipt.add_item(
            name="商品2",
            quantity=Decimal("20"),
            unit_price=Decimal("3"),
        )

        assert len(receipt.items) == 2
        assert receipt.items[1].sequence == 2

    def test_total_amount(self):
        """测试总金额计算"""
        receipt = create_receipt(
            title="测试采购",
            delivery_date=date(2025, 1, 20),
        )

        receipt.add_item("商品1", Decimal("10"), Decimal("5"))
        receipt.add_item("商品2", Decimal("20"), Decimal("3"))

        assert receipt.total_amount == Decimal("110")  # 10*5 + 20*3

    def test_validate_success(self):
        """测试验证成功"""
        receipt = create_receipt(
            title="测试采购",
            delivery_date=date(2025, 1, 20),
        )
        receipt.add_item("商品1", Decimal("10"), Decimal("5"))

        is_valid, errors = receipt.validate()

        assert is_valid
        assert len(errors) == 0

    def test_validate_empty_title(self):
        """测试验证空标题"""
        receipt = create_receipt(
            title="",
            delivery_date=date(2025, 1, 20),
        )

        is_valid, errors = receipt.validate()

        assert not is_valid
        assert "主题标题不能为空" in errors

    def test_validate_empty_items(self):
        """测试验证空商品列表"""
        receipt = create_receipt(
            title="测试采购",
            delivery_date=date(2025, 1, 20),
        )

        is_valid, errors = receipt.validate()

        assert not is_valid
        assert "商品列表不能为空" in errors

    def test_validate_negative_quantity(self):
        """测试验证负数量"""
        receipt = create_receipt(
            title="测试采购",
            delivery_date=date(2025, 1, 20),
        )
        receipt.add_item("商品1", Decimal("-1"), Decimal("5"))

        is_valid, errors = receipt.validate()

        assert not is_valid
        assert "商品数量必须大于0" in errors

    def test_validate_negative_price(self):
        """测试验证负单价"""
        receipt = create_receipt(
            title="测试采购",
            delivery_date=date(2025, 1, 20),
        )
        receipt.add_item("商品1", Decimal("10"), Decimal("-5"))

        is_valid, errors = receipt.validate()

        assert not is_valid
        assert "商品单价不能为负数" in errors

    def test_to_dict(self):
        """测试转字典"""
        receipt = create_receipt(
            title="测试采购",
            delivery_date=date(2025, 1, 20),
        )
        receipt.add_item("商品1", Decimal("10"), Decimal("5"))

        data = receipt.to_dict()

        assert data["title"] == "测试采购"
        assert data["delivery_date"] == "2025-01-20"
        assert data["item_count"] == 1
        assert data["total_amount"] == 50.0

    def test_from_dict(self):
        """测试从字典创建"""
        data = {
            "title": "测试采购",
            "delivery_date": "2025-01-20",
            "purchaser": "梁程程妈妈",
            "payment_method": "转账",
            "items": [
                {
                    "sequence": 1,
                    "name": "商品1",
                    "quantity": 10.0,
                    "unit_price": 5.0,
                    "amount": 50.0,
                }
            ],
        }

        receipt = PurchaseReceipt.from_dict(data)

        assert receipt.title == "测试采购"
        assert receipt.delivery_date == date(2025, 1, 20)
        assert len(receipt.items) == 1

    def test_to_json(self):
        """测试转JSON"""
        receipt = create_receipt(
            title="测试采购",
            delivery_date=date(2025, 1, 20),
        )
        receipt.add_item("商品1", Decimal("10"), Decimal("5"))

        json_str = receipt.to_json()

        assert "测试采购" in json_str
        assert "2025-01-20" in json_str
        assert "商品1" in json_str

    def test_from_json(self):
        """测试从JSON创建"""
        json_str = '''{
            "title": "测试采购",
            "delivery_date": "2025-01-20",
            "items": []
        }'''

        receipt = PurchaseReceipt.from_json(json_str)

        assert receipt.title == "测试采购"
        assert receipt.delivery_date == date(2025, 1, 20)
