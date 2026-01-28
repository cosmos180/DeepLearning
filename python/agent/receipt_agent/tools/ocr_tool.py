#!/usr/bin/env python3
"""
OCR Tool - AI 收据识别工具
支持自然语言调用 AI 识别收据图片
"""

import asyncio
import os
from datetime import date
from decimal import Decimal
from typing import Optional, Union

# 允许嵌套事件循环
import nest_asyncio
nest_asyncio.apply()

from receipt_manager.ai_ocr import AIRecognizer
from receipt_manager import PurchaseReceipt, create_receipt


def _run_async(coro):
    """运行异步代码 (nest_asyncio 已启用)"""
    try:
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(coro)
    except RuntimeError:
        return asyncio.run(coro)


def recognize_receipt(
    image_path: str,
    api_key: Optional[str] = None,
    title_hint: Optional[str] = None,
    date_hint: Optional[str] = None,
) -> str:
    """
    使用 AI 识别收据图片

    Args:
        image_path: 图片文件路径
        api_key: API 密钥（默认从环境变量 ARK_API_KEY 读取）
        title_hint: 主题提示（可选）
        date_hint: 日期提示（可选，格式：YYYY-M-D）

    Returns:
        识别结果的格式化字符串

    Example:
        recognize_receipt(image_path="./receipt.jpg")
        recognize_receipt(image_path="./receipt.jpg", title_hint="打印", date_hint="2025-1-20")
    """
    try:
        recognizer = AIRecognizer(api_key=api_key or os.getenv("ARK_API_KEY"))
        receipt, confidence = _run_async(
            recognizer.recognize_receipt_async(image_path, title_hint, date_hint)
        )

        if receipt is None:
            return "❌ AI 识别失败，请检查图片质量或尝试手动输入"

        return format_receipt_result(receipt, confidence)

    except ValueError as e:
        return f"❌ 配置错误: {str(e)}"
    except Exception as e:
        return f"❌ 识别失败: {str(e)}"


def batch_recognize(
    folder_path: str,
    pattern: str = "*",
    api_key: Optional[str] = None,
    recursive: bool = False,
) -> str:
    """
    批量识别文件夹中的收据图片

    Args:
        folder_path: 文件夹路径
        pattern: 文件匹配模式，如 "*.jpg"
        api_key: API 密钥
        recursive: 是否递归处理子文件夹

    Returns:
        批量识别结果的汇总字符串

    Example:
        batch_recognize(folder_path="./receipts")
        batch_recognize(folder_path="./receipts", pattern="*.jpg", recursive=True)
    """
    from pathlib import Path

    folder = Path(folder_path).expanduser()
    if not folder.exists():
        return f"❌ 文件夹不存在: {folder_path}"

    # 支持的图片格式
    IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.bmp', '.gif', '.webp', '.tiff'}

    # 查找图片
    images = []
    if recursive:
        for ext in IMAGE_EXTENSIONS:
            images.extend(folder.rglob(f"*{ext}"))
            images.extend(folder.rglob(f"*{ext.upper()}"))
    else:
        for ext in IMAGE_EXTENSIONS:
            images.extend(folder.glob(f"*{ext}"))
            images.extend(folder.glob(f"*{ext.upper()}"))

    # 去重排序
    images = sorted(set(images))

    # 应用模式过滤
    if pattern and pattern != "*":
        import fnmatch
        images = [img for img in images if fnmatch.fnmatch(img.name, pattern)]

    if not images:
        return f"📭 在 {folder_path} 中未找到图片文件"

    lines = [
        f"🔍 批量识别收据",
        f"{'='*60}",
        f"  文件夹: {folder_path}",
        f"  找到图片: {len(images)} 个",
        f"{'='*60}",
    ]

    recognizer = AIRecognizer(api_key=api_key or os.getenv("ARK_API_KEY"))

    success_count = 0
    failed_count = 0

    for i, image_path in enumerate(images, 1):
        lines.append(f"\n[{i}/{len(images)}] {image_path.name}")
        lines.append("-" * 40)

        try:
            receipt, confidence = _run_async(
                recognizer.recognize_receipt_async(str(image_path))
            )

            if receipt is None:
                lines.append("  ❌ 识别失败")
                failed_count += 1
            else:
                lines.append(f"  ✓ 主题: {receipt.title}")
                lines.append(f"  ✓ 日期: {receipt.delivery_date}")
                lines.append(f"  ✓ 商品数: {receipt.item_count}")
                lines.append(f"  ✓ 总金额: ¥{receipt.total_amount:.2f}")
                lines.append(f"  ✓ 置信度: {confidence:.2%}")
                success_count += 1

        except Exception as e:
            lines.append(f"  ❌ 错误: {str(e)}")
            failed_count += 1

    # 汇总
    lines.append("\n" + "=" * 60)
    lines.append(f"✓ 成功: {success_count}")
    if failed_count > 0:
        lines.append(f"❌ 失败: {failed_count}")

    return "\n".join(lines)


def create_manual_receipt(
    title: str,
    delivery_date: Union[str, date],
    purchaser: str = "梁程程妈妈",
    payment_method: str = "转账",
    items: Optional[list] = None,
) -> str:
    """
    手动创建收据

    Args:
        title: 主题标题
        delivery_date: 交付日期（格式：YYYY-M-D）
        purchaser: 采购方（默认"梁程程妈妈"）
        payment_method: 付款方式（默认"转账"）
        items: 商品列表，每个商品包含 name, quantity, unit_price, spec, unit, remark

    Returns:
        创建结果的格式化字符串

    Example:
        create_manual_receipt(
            title="数学资料打印",
            delivery_date="2025-1-20",
            items=[
                {"name": "语文资料", "quantity": 47, "unit_price": 6.0, "unit": "份"}
            ]
        )
    """
    try:
        # 解析日期
        if isinstance(delivery_date, str):
            delivery_date = date.fromisoformat(delivery_date)

        # 创建收据
        receipt = create_receipt(
            title=title,
            delivery_date=delivery_date,
            purchaser=purchaser,
        )
        receipt.payment_method = payment_method

        # 添加商品
        if items:
            for i, item_data in enumerate(items, 1):
                receipt.add_item(
                    name=item_data.get("name", f"商品{i}"),
                    quantity=Decimal(str(item_data.get("quantity", 1))),
                    unit_price=Decimal(str(item_data.get("unit_price", 0))),
                    spec=item_data.get("spec"),
                    unit=item_data.get("unit", "个"),
                    remark=item_data.get("remark"),
                )

        # 验证
        is_valid, errors = receipt.validate()
        if not is_valid:
            error_msg = "❌ 数据验证失败:\n" + "\n".join(f"  - {e}" for e in errors)
            return error_msg

        return format_receipt_result(receipt, 1.0)

    except Exception as e:
        return f"❌ 创建失败: {str(e)}"


def format_receipt_result(receipt: PurchaseReceipt, confidence: float) -> str:
    """格式化收据识别结果"""
    lines = [
        f"📄 收据识别结果",
        f"{'='*60}",
        f"  主题: {receipt.title}",
        f"  日期: {receipt.delivery_date}",
        f"  采购方: {receipt.purchaser}",
        f"  付款方式: {receipt.payment_method}",
        f"{'='*60}",
        f"{'序号':<6} {'商品名称':<20} {'规格':<12} {'单位':<6} {'数量':>8} {'单价':>10} {'金额':>10}",
        f"{'-'*60}",
    ]

    for item in receipt.items:
        spec = (item.spec or "")[:12]
        name = item.name[:20]
        amount_val = float(item.amount) if item.amount is not None else 0.0
        lines.append(
            f"{item.sequence:<6} {name:<20} {spec:<12} {item.unit:<6} "
            f"{float(item.quantity):>8.1f} ¥{float(item.unit_price):>9.2f} ¥{amount_val:>9.2f}"
        )

    lines.extend([
        f"{'-'*60}",
        f"{'':>44} {'总计':>10} ¥{float(receipt.total_amount):>9.2f}",
        f"{'='*60}",
        f"  商品数量: {receipt.item_count}",
        f"  总数量: {float(receipt.total_quantity):.1f}",
        f"  识别方式: {receipt.recognition_method}",
        f"  置信度: {confidence:.2%}",
    ])

    return "\n".join(lines)


# 导出所有工具函数
__all__ = [
    "recognize_receipt",
    "batch_recognize",
    "create_manual_receipt",
]
