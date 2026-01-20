"""
采购收据管理工具 - 使用示例

演示如何使用核心模块进行编程式操作。
"""

from datetime import date
from decimal import Decimal
from pathlib import Path

from receipt_manager import PurchaseReceipt, create_receipt
from receipt_manager.excel_handler import ExcelHandler
from receipt_manager.ai_ocr import recognize_receipt


def example_create_receipt():
    """示例：创建收据"""
    print("\n=== 示例1：创建收据 ===\n")

    # 创建收据
    receipt = create_receipt(
        title="数学资料打印",
        delivery_date=date(2025, 1, 20),
    )

    # 添加商品
    receipt.add_item(
        name="数学练习册",
        spec="A4",
        unit="本",
        quantity=Decimal("30"),
        unit_price=Decimal("5.5"),
    )

    receipt.add_item(
        name="试卷纸",
        spec="8开",
        unit="份",
        quantity=Decimal("50"),
        unit_price=Decimal("0.5"),
    )

    # 显示信息
    print(f"主题: {receipt.title}")
    print(f"日期: {receipt.delivery_date}")
    print(f"商品数量: {receipt.item_count}")
    print(f"总金额: ¥{receipt.total_amount:.2f}")
    print(f"Sheet名称: {receipt.sheet_name}")

    # 验证
    is_valid, errors = receipt.validate()
    print(f"\n验证结果: {'通过' if is_valid else '失败'}")
    if not is_valid:
        for error in errors:
            print(f"  - {error}")

    return receipt


def example_save_to_excel():
    """示例：保存到Excel"""
    print("\n=== 示例2：保存到Excel ===\n")

    # 创建收据
    receipt = create_receipt(
        title="教室布置采购",
        delivery_date=date(2025, 1, 21),
    )

    receipt.add_item("彩色卡纸", None, "张", Decimal("100"), Decimal("2"))
    receipt.add_item("剪刀", None, "把", Decimal("10"), Decimal("15"))
    receipt.add_item("胶水", None, "瓶", Decimal("20"), Decimal("3.5"))

    # 保存到Excel
    excel_file = Path("data/test_purchase.xlsx")
    handler = ExcelHandler(excel_file)
    handler.add_receipt(receipt)
    handler.close()

    print(f"✓ 收据已保存到: {excel_file}")
    print(f"✓ Sheet名称: {receipt.sheet_name}")


def example_read_from_excel():
    """示例：从Excel读取"""
    print("\n=== 示例3：从Excel读取 ===\n")

    excel_file = Path("data/test_purchase.xlsx")

    if not excel_file.exists():
        print(f"Excel文件不存在: {excel_file}")
        return

    handler = ExcelHandler(excel_file)

    # 列出所有Sheet
    sheets = handler.list_sheets()
    print(f"Sheet列表: {sheets}")

    # 读取收据
    for sheet_name in sheets:
        receipt = handler.read_receipt(sheet_name)
        if receipt:
            print(f"\n主题: {receipt.title}")
            print(f"日期: {receipt.delivery_date}")
            print(f"商品数量: {receipt.item_count}")
            print(f"总金额: ¥{receipt.total_amount:.2f}")

            # 打印商品清单
            print("\n商品清单:")
            for item in receipt.items:
                print(f"  {item.sequence}. {item.name} x {item.quantity} {item.unit} @ ¥{item.unit_price:.2f}")

    handler.close()


def example_ai_recognize():
    """示例：AI识别收据"""
    print("\n=== 示例4：AI识别收据 ===\n")

    # 需要设置API密钥
    import os
    if not os.getenv("ARK_API_KEY"):
        print("请设置环境变量 ARK_API_KEY")
        return

    # 假设有一张收据图片
    image_path = "data/receipt_sample.jpg"

    if not Path(image_path).exists():
        print(f"图片不存在: {image_path}")
        print("这是一个示例，实际使用时请替换为真实图片路径")
        return

    # 识别收据
    receipt, confidence = recognize_receipt(
        image_path,
        title_hint="数学资料打印",
        date_hint="2025-1-20",
    )

    if receipt:
        print(f"✓ 识别成功")
        print(f"主题: {receipt.title}")
        print(f"日期: {receipt.delivery_date}")
        print(f"置信度: {confidence:.2%}")
        print(f"商品数量: {receipt.item_count}")
        print(f"总金额: ¥{receipt.total_amount:.2f}")
    else:
        print("✗ 识别失败")


def example_statistics():
    """示例：统计信息"""
    print("\n=== 示例5：统计信息 ===\n")

    excel_file = Path("data/test_purchase.xlsx")

    if not excel_file.exists():
        print(f"Excel文件不存在: {excel_file}")
        return

    handler = ExcelHandler(excel_file)
    stats = handler.get_statistics()
    handler.close()

    print(f"Sheet数量: {stats['sheet_count']}")
    print(f"收据数量: {stats['receipt_count']}")
    print(f"商品总数: {stats['total_items']}")
    print(f"总金额: ¥{stats['total_amount']:.2f}")

    print("\n最近收据:")
    for receipt in stats['recent_receipts'][:5]:
        print(f"  - {receipt['date']}: {receipt['title']} ¥{receipt['amount']:.2f}")


def example_json_export():
    """示例：JSON导出"""
    print("\n=== 示例6：JSON导出 ===\n")

    # 创建收据
    receipt = create_receipt(
        title="测试采购",
        delivery_date=date(2025, 1, 22),
    )

    receipt.add_item("商品1", None, "个", Decimal("10"), Decimal("5"))
    receipt.add_item("商品2", None, "箱", Decimal("2"), Decimal("50"))

    # 转为JSON
    json_str = receipt.to_json(indent=2)
    print(json_str)

    # 从JSON创建
    receipt2 = PurchaseReceipt.from_json(json_str)
    print(f"\n从JSON创建的收据: {receipt2.title}")


if __name__ == "__main__":
    print("=" * 60)
    print("采购收据管理工具 - 使用示例")
    print("=" * 60)

    # 运行示例
    example_create_receipt()
    example_save_to_excel()
    example_read_from_excel()
    # example_ai_recognize()  # 需要API密钥
    example_statistics()
    example_json_export()

    print("\n" + "=" * 60)
    print("示例运行完成")
    print("=" * 60)
