#!/usr/bin/env python3
"""
Query Tool - 收据查询工具
支持按条件查询收据
"""

from pathlib import Path
from datetime import date
from typing import Optional

from receipt_manager.excel_handler import ExcelHandler


def _normalize_path(path: str) -> Path:
    """规范化文件路径，处理各种常见格式"""
    # 处理 LLM 可能生成的错误格式: ~/home/user/...
    if path.startswith("~/home/") or path.startswith("~/\\home\\"):
        actual_path = path[2:]  # 去掉 ~/
        # 添加根目录 /
        return Path("/" + actual_path)

    p = Path(path)

    # 如果已经是绝对路径，直接返回
    if p.is_absolute():
        return p

    # 如果路径以 ~/ 开头（正常格式）
    if path.startswith("~/"):
        return Path(path).expanduser()

    # 相对路径
    return Path(path).expanduser()


def list_receipts(
    excel_path: str = "~/Downloads/309 采购明细.xlsx",
    title_filter: Optional[str] = None,
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    limit: int = 20,
) -> str:
    """
    列出收据

    Args:
        excel_path: Excel 文件路径
        title_filter: 按主题筛选（模糊匹配）
        from_date: 起始日期（格式：YYYY-M-D）
        to_date: 结束日期（格式：YYYY-M-D）
        limit: 显示数量

    Returns:
        收据列表的格式化字符串

    Example:
        list_receipts()
        list_receipts(title_filter="打印", from_date="2025-01-01", limit=10)
    """
    try:
        excel_file = _normalize_path(excel_path)

        if not excel_file.exists():
            return f"❌ Excel 文件不存在: {excel_path}"

        handler = ExcelHandler(excel_file)
        sheets = handler.list_sheets()

        # 读取收据
        receipts = []
        for sheet_name in sheets:
            receipt = handler.read_receipt(sheet_name)
            if receipt:
                # 筛选
                if title_filter and title_filter.lower() not in receipt.title.lower():
                    continue
                if from_date:
                    from_d = date.fromisoformat(from_date)
                    if receipt.delivery_date < from_d:
                        continue
                if to_date:
                    to_d = date.fromisoformat(to_date)
                    if receipt.delivery_date > to_d:
                        continue
                receipts.append((sheet_name, receipt))

        handler.close()

        # 排序
        receipts.sort(key=lambda x: x[1].delivery_date, reverse=True)

        # 限制数量
        receipts = receipts[:limit]

        if not receipts:
            return "📭 没有找到匹配的收据"

        lines = [
            f"📋 收据列表",
            f"{'='*60}",
            f"{'日期':<12} {'主题':<25} {'商品数':>8} {'总金额':>12}",
            f"{'-'*60}",
        ]

        for sheet_name, receipt in receipts:
            lines.append(
                f"{receipt.delivery_date.isoformat():<12} "
                f"{receipt.title[:25]:<25} "
                f"{receipt.item_count:>8} "
                f"¥{float(receipt.total_amount):>10.2f}"
            )

        lines.extend([
            f"{'-'*60}",
            f"  共 {len(receipts)} 条记录",
        ])

        return "\n".join(lines)

    except Exception as e:
        return f"❌ 查询失败: {str(e)}"


def search_receipts_by_keyword(
    keyword: str,
    excel_path: str = "~/Downloads/309 采购明细.xlsx",
    limit: int = 20,
) -> str:
    """
    按关键词搜索收据

    Args:
        keyword: 搜索关键词（匹配主题或商品名称）
        excel_path: Excel 文件路径
        limit: 显示数量

    Returns:
        搜索结果的格式化字符串

    Example:
        search_receipts_by_keyword(keyword="打印")
        search_receipts_by_keyword(keyword="资料")
    """
    try:
        excel_file = _normalize_path(excel_path)

        if not excel_file.exists():
            return f"❌ Excel 文件不存在: {excel_path}"

        handler = ExcelHandler(excel_file)
        sheets = handler.list_sheets()

        matched_receipts = []
        keyword_lower = keyword.lower()

        for sheet_name in sheets:
            receipt = handler.read_receipt(sheet_name)
            if receipt:
                # 检查主题
                if keyword_lower in receipt.title.lower():
                    matched_receipts.append((sheet_name, receipt, "主题"))
                    continue

                # 检查商品名称
                for item in receipt.items:
                    if keyword_lower in item.name.lower():
                        matched_receipts.append((sheet_name, receipt, "商品"))
                        break

        handler.close()

        if not matched_receipts:
            return f"📭 未找到包含关键词「{keyword}」的收据"

        # 去重并限制数量
        seen = set()
        unique_receipts = []
        for sheet_name, receipt, match_type in matched_receipts:
            if sheet_name not in seen:
                seen.add(sheet_name)
                unique_receipts.append((sheet_name, receipt, match_type))
                if len(unique_receipts) >= limit:
                    break

        lines = [
            f"🔍 搜索结果: {keyword}",
            f"{'='*60}",
            f"{'日期':<12} {'主题':<25} {'匹配':<8} {'金额':>12}",
            f"{'-'*60}",
        ]

        for sheet_name, receipt, match_type in unique_receipts:
            lines.append(
                f"{receipt.delivery_date.isoformat():<12} "
                f"{receipt.title[:25]:<25} "
                f"{match_type:<8} "
                f"¥{float(receipt.total_amount):>10.2f}"
            )

        lines.extend([
            f"{'-'*60}",
            f"  共 {len(unique_receipts)} 条结果",
        ])

        return "\n".join(lines)

    except Exception as e:
        return f"❌ 搜索失败: {str(e)}"


def get_receipt_by_date(
    target_date: str,
    excel_path: str = "~/Downloads/309 采购明细.xlsx",
) -> str:
    """
    获取指定日期的收据

    Args:
        target_date: 目标日期（格式：YYYY-M-D）
        excel_path: Excel 文件路径

    Returns:
        收据信息的格式化字符串

    Example:
        get_receipt_by_date(target_date="2025-01-20")
    """
    try:
        target = date.fromisoformat(target_date)

        results = list_receipts(
            excel_path=excel_path,
            from_date=target_date,
            to_date=target_date,
            limit=100,
        )

        # 检查是否有结果
        if "共 0 条记录" in results or "没有找到匹配的收据" in results:
            return f"📭 未找到日期为 {target_date} 的收据"

        return results

    except ValueError:
        return f"❌ 日期格式错误，请使用 YYYY-M-D 格式，如 2025-01-20"
    except Exception as e:
        return f"❌ 查询失败: {str(e)}"


def get_receipt_summary(
    sheet_name: str,
    excel_path: str = "~/Downloads/309 采购明细.xlsx",
) -> str:
    """
    获取收据摘要信息

    Args:
        sheet_name: Sheet 名称
        excel_path: Excel 文件路径

    Returns:
        收据摘要的格式化字符串

    Example:
        get_receipt_summary(sheet_name="数学资料打印（1-20）")
    """
    try:
        excel_file = _normalize_path(excel_path)
        handler = ExcelHandler(excel_file)

        receipt = handler.read_receipt(sheet_name)
        handler.close()

        if receipt is None:
            return f"❌ 未找到 Sheet: {sheet_name}"

        lines = [
            f"📄 收据摘要",
            f"{'='*60}",
            f"  Sheet: {sheet_name}",
            f"  主题: {receipt.title}",
            f"  日期: {receipt.delivery_date}",
            f"  采购方: {receipt.purchaser}",
            f"  付款方式: {receipt.payment_method}",
            f"{'='*60}",
            f"  商品数量: {receipt.item_count}",
            f"  总数量: {float(receipt.total_quantity):.1f}",
            f"  总金额: ¥{float(receipt.total_amount):.2f}",
        ]

        # 商品明细
        lines.append(f"{'='*60}")
        lines.append("  商品明细:")
        for item in receipt.items:
            lines.append(
                f"    {item.sequence}. {item.name} "
                f"x {float(item.quantity):.1f} {item.unit} "
                f"@ ¥{float(item.unit_price):.2f}"
            )

        return "\n".join(lines)

    except Exception as e:
        return f"❌ 获取摘要失败: {str(e)}"


# 导出所有工具函数
__all__ = [
    "list_receipts",
    "search_receipts_by_keyword",
    "get_receipt_by_date",
    "get_receipt_summary",
]
