#!/usr/bin/env python3
"""
Stats Tool - 统计分析工具
提供收据统计和分析功能
"""

import json
from pathlib import Path
from datetime import date
from collections import defaultdict
from decimal import Decimal
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


def get_statistics(
    excel_path: str = "~/Downloads/309 采购明细.xlsx",
) -> str:
    """
    获取 Excel 统计信息

    Args:
        excel_path: Excel 文件路径

    Returns:
        统计信息的格式化字符串

    Example:
        get_statistics()
    """
    try:
        excel_file = _normalize_path(excel_path)

        if not excel_file.exists():
            return f"❌ Excel 文件不存在: {excel_path}"

        handler = ExcelHandler(excel_file)
        stats = handler.get_statistics()
        handler.close()

        lines = [
            f"📊 统计信息",
            f"{'='*60}",
            f"  文件: {excel_file}",
            f"{'='*60}",
            f"  Sheet 数量: {stats['sheet_count']}",
            f"  收据数量: {stats['receipt_count']}",
            f"  商品总数: {stats['total_items']}",
            f"  总金额: [bold red]¥{stats['total_amount']:.2f}[/bold red]",
        ]

        # 最近收据
        if stats.get('recent_receipts'):
            lines.append(f"{'='*60}")
            lines.append(f"  最近收据 (最多10条):")
            for r in stats['recent_receipts'][:5]:
                lines.append(
                    f"    - {r['date']}: {r['title'][:30]:<30} ¥{r['amount']:.2f}"
                )

        return "\n".join(lines)

    except Exception as e:
        return f"❌ 获取统计失败: {str(e)}"


def export_statistics_json(
    output_path: Optional[str] = None,
    excel_path: str = "~/Downloads/309 采购明细.xlsx",
) -> str:
    """
    导出统计信息为 JSON

    Args:
        output_path: 输出文件路径（可选，默认打印到控制台）
        excel_path: Excel 文件路径

    Returns:
        JSON 字符串或保存确认信息

    Example:
        export_statistics_json()
        export_statistics_json(output_path="./stats.json")
    """
    try:
        excel_file = _normalize_path(excel_path)

        if not excel_file.exists():
            return f"❌ Excel 文件不存在: {excel_path}"

        handler = ExcelHandler(excel_file)
        stats = handler.get_statistics()
        handler.close()

        json_str = json.dumps(stats, ensure_ascii=False, indent=2)

        if output_path:
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            output_file.write_text(json_str, encoding="utf-8")
            return f"✓ 统计信息已导出到: {output_file}"
        else:
            return json_str

    except Exception as e:
        return f"❌ 导出失败: {str(e)}"


def analyze_by_period(
    period: str = "month",
    excel_path: str = "~/Downloads/309 采购明细.xlsx",
) -> str:
    """
    按时间周期分析收据

    Args:
        period: 周期类型 (month/week/day)
        excel_path: Excel 文件路径

    Returns:
        分析结果的格式化字符串

    Example:
        analyze_by_period(period="month")
        analyze_by_period(period="week")
    """
    try:
        excel_file = _normalize_path(excel_path)

        if not excel_file.exists():
            return f"❌ Excel 文件不存在: {excel_file}"

        handler = ExcelHandler(excel_file)
        sheets = handler.list_sheets()

        # 按周期分组
        period_data = defaultdict(lambda: {"count": 0, "amount": Decimal("0")})

        for sheet_name in sheets:
            receipt = handler.read_receipt(sheet_name)
            if receipt:
                if period == "month":
                    key = f"{receipt.delivery_date.year}-{receipt.delivery_date.month:02d}"
                elif period == "week":
                    week_num = receipt.delivery_date.isocalendar()[1]
                    key = f"{receipt.delivery_date.year}-W{week_num:02d}"
                else:  # day
                    key = receipt.delivery_date.isoformat()

                period_data[key]["count"] += 1
                period_data[key]["amount"] += receipt.total_amount

        handler.close()

        if not period_data:
            return "📭 没有收据数据"

        # 排序
        sorted_periods = sorted(period_data.items(), reverse=True)

        lines = [
            f"📊 按{period}分析",
            f"{'='*60}",
            f"{'周期':<15} {'收据数':>8} {'总金额':>15}",
            f"{'-'*60}",
        ]

        total_amount = Decimal("0")
        total_count = 0

        for period_key, data in sorted_periods[:20]:  # 最多显示 20 条
            lines.append(
                f"{period_key:<15} {data['count']:>8} ¥{float(data['amount']):>13.2f}"
            )
            total_amount += data["amount"]
            total_count += data["count"]

        lines.extend([
            f"{'-'*60}",
            f"{'总计':<15} {total_count:>8} ¥{float(total_amount):>13.2f}",
        ])

        return "\n".join(lines)

    except Exception as e:
        return f"❌ 分析失败: {str(e)}"


def get_top_items(
    excel_path: str = "~/Downloads/309 采购明细.xlsx",
    limit: int = 10,
) -> str:
    """
    获取购买最多的商品

    Args:
        excel_path: Excel 文件路径
        limit: 返回数量

    Returns:
        商品统计的格式化字符串

    Example:
        get_top_items()
        get_top_items(limit=20)
    """
    try:
        excel_file = _normalize_path(excel_path)

        if not excel_file.exists():
            return f"❌ Excel 文件不存在: {excel_file}"

        handler = ExcelHandler(excel_file)
        sheets = handler.list_sheets()

        # 统计商品
        item_stats = defaultdict(lambda: {"count": 0, "quantity": Decimal("0"), "amount": Decimal("0")})

        for sheet_name in sheets:
            receipt = handler.read_receipt(sheet_name)
            if receipt:
                for item in receipt.items:
                    item_stats[item.name]["count"] += 1
                    item_stats[item.name]["quantity"] += item.quantity
                    item_stats[item.name]["amount"] += item.amount or Decimal("0")

        handler.close()

        if not item_stats:
            return "📭 没有商品数据"

        # 按数量排序
        sorted_items = sorted(
            item_stats.items(),
            key=lambda x: float(x[1]["quantity"]),
            reverse=True,
        )[:limit]

        lines = [
            f"🏆 购买最多的商品 (Top {limit})",
            f"{'='*60}",
            f"{'排名':<6} {'商品名称':<25} {'次数':>8} {'总数量':>12} {'总金额':>15}",
            f"{'-'*60}",
        ]

        for rank, (name, data) in enumerate(sorted_items, 1):
            lines.append(
                f"{rank:<6} {name[:25]:<25} {data['count']:>8} "
                f"{float(data['quantity']):>12.1f} ¥{float(data['amount']):>13.2f}"
            )

        return "\n".join(lines)

    except Exception as e:
        return f"❌ 获取失败: {str(e)}"


def get_monthly_summary(
    year: Optional[int] = None,
    excel_path: str = "~/Downloads/309 采购明细.xlsx",
) -> str:
    """
    获取月度汇总

    Args:
        year: 年份（默认当前年份）
        excel_path: Excel 文件路径

    Returns:
        月度汇总的格式化字符串

    Example:
        get_monthly_summary()
        get_monthly_summary(year=2025)
    """
    try:
        if year is None:
            year = date.today().year

        excel_file = _normalize_path(excel_path)

        if not excel_file.exists():
            return f"❌ Excel 文件不存在: {excel_file}"

        handler = ExcelHandler(excel_file)
        sheets = handler.list_sheets()

        # 按月分组
        monthly_data = defaultdict(lambda: {"count": 0, "amount": Decimal("0")})

        for sheet_name in sheets:
            receipt = handler.read_receipt(sheet_name)
            if receipt and receipt.delivery_date.year == year:
                month = receipt.delivery_date.month
                monthly_data[month]["count"] += 1
                monthly_data[month]["amount"] += receipt.total_amount

        handler.close()

        if not monthly_data:
            return f"📭 {year} 年没有收据数据"

        lines = [
            f"📅 {year} 年月度汇总",
            f"{'='*60}",
            f"{'月份':<8} {'收据数':>8} {'总金额':>15}",
            f"{'-'*60}",
        ]

        total_amount = Decimal("0")
        total_count = 0

        for month in range(1, 13):
            if month in monthly_data:
                data = monthly_data[month]
                lines.append(
                    f"{month:02d}月     {data['count']:>8} ¥{float(data['amount']):>13.2f}"
                )
                total_amount += data["amount"]
                total_count += data["count"]
            else:
                lines.append(f"{month:02d}月        -         -")

        lines.extend([
            f"{'-'*60}",
            f"{'全年':<8} {total_count:>8} ¥{float(total_amount):>13.2f}",
        ])

        return "\n".join(lines)

    except Exception as e:
        return f"❌ 获取失败: {str(e)}"


# 导出所有工具函数
__all__ = [
    "get_statistics",
    "export_statistics_json",
    "analyze_by_period",
    "get_top_items",
    "get_monthly_summary",
]
