#!/usr/bin/env python3
"""
Receipt Manager CLI - Skill 统一命令行入口
封装所有收据管理工具函数为 Click 子命令

所有工具模块使用延迟导入，确保 --help 和基础命令无需全部依赖。
"""

import os
import sys
from pathlib import Path

# ============================================================================
# 路径设置 - 确保能找到 receipt_manager 核心包和 tool 模块
# ============================================================================

_script_dir = Path(__file__).parent.resolve()
# scripts → receipt_manager → skills → .agents → DeepLearning/
_project_root = _script_dir.parents[3]

# 核心包路径
_mcp_receipt_dir = _project_root / "python" / "mcp" / "receipt_manager"
_agent_tools_dir = _project_root / "python" / "agent" / "receipt_agent" / "tools"

# 将路径添加到 sys.path
for _p in [str(_mcp_receipt_dir), str(_agent_tools_dir)]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

import click

DEFAULT_EXCEL = "~/Documents/receipt-309/309-采购明细.xlsx"


def _import_ocr():
    """延迟导入 OCR 工具模块"""
    import ocr_tool
    return ocr_tool


def _import_excel():
    """延迟导入 Excel 工具模块"""
    import excel_tool
    return excel_tool


def _import_query():
    """延迟导入查询工具模块"""
    import query_tool
    return query_tool


def _import_stats():
    """延迟导入统计工具模块"""
    import stats_tool
    return stats_tool


@click.group()
def cli():
    """采购收据管理工具"""
    pass


# ============================================================================
# OCR 识别命令
# ============================================================================

@cli.command()
@click.argument("image_path")
@click.option("--hint", default=None, help="主题提示")
@click.option("--date-hint", default=None, help="日期提示 (YYYY-M-D)")
def recognize(image_path, hint, date_hint):
    """识别单张收据图片"""
    ocr = _import_ocr()
    result = ocr.recognize_receipt(image_path=image_path, title_hint=hint, date_hint=date_hint)
    click.echo(result)


@cli.command("batch-recognize")
@click.argument("folder_path")
@click.option("--pattern", default="*", help="文件匹配模式")
@click.option("--recursive", is_flag=True, help="递归处理子文件夹")
def batch_recognize_cmd(folder_path, pattern, recursive):
    """批量识别文件夹中的收据"""
    ocr = _import_ocr()
    result = ocr.batch_recognize(folder_path=folder_path, pattern=pattern, recursive=recursive)
    click.echo(result)


@cli.command("recognize-and-save")
@click.argument("image_path")
@click.option("--excel-path", default=DEFAULT_EXCEL, help="Excel 文件路径")
@click.option("--hint", default=None, help="主题提示")
@click.option("--date-hint", default=None, help="日期提示")
def recognize_and_save_cmd(image_path, excel_path, hint, date_hint):
    """识别收据并保存到 Excel（图片自动插入到表格下方）"""
    ocr = _import_ocr()
    result = ocr.recognize_and_save(
        image_path=image_path, excel_path=excel_path,
        title_hint=hint, date_hint=date_hint,
    )
    click.echo(result)


@cli.command("create-receipt")
@click.option("--title", required=True, help="主题标题")
@click.option("--date", "delivery_date", required=True, help="交付日期 (YYYY-M-D)")
@click.option("--purchaser", default="梁程程妈妈", help="采购方")
@click.option("--payment", default="转账", help="付款方式")
@click.option("--items", default=None, help="商品列表 JSON")
def create_receipt_cmd(title, delivery_date, purchaser, payment, items):
    """手动创建收据"""
    import json
    ocr = _import_ocr()
    parsed_items = json.loads(items) if items else None
    result = ocr.create_manual_receipt(
        title=title, delivery_date=delivery_date,
        purchaser=purchaser, payment_method=payment, items=parsed_items,
    )
    click.echo(result)


# ============================================================================
# Excel 操作命令
# ============================================================================

@cli.command()
@click.option("--data", required=True, help="收据数据 JSON")
@click.option("--excel-path", default=DEFAULT_EXCEL, help="Excel 文件路径")
@click.option("--image-path", default=None, help="收据图片路径（自动插入到表格下方）")
def save(data, excel_path, image_path):
    """保存收据到 Excel"""
    import json
    excel = _import_excel()
    receipt_data = json.loads(data)
    result = excel.save_receipt_to_excel(
        receipt_data=receipt_data, excel_path=excel_path,
        image_path=image_path,
    )
    click.echo(result)


@cli.command()
@click.option("--sheet", required=True, help="Sheet 名称")
@click.option("--excel-path", default=DEFAULT_EXCEL, help="Excel 文件路径")
def read(sheet, excel_path):
    """读取指定收据"""
    excel = _import_excel()
    result = excel.read_receipt_from_excel(sheet_name=sheet, excel_path=excel_path)
    click.echo(result)


@cli.command("list-sheets")
@click.option("--excel-path", default=DEFAULT_EXCEL, help="Excel 文件路径")
def list_sheets_cmd(excel_path):
    """列出所有 Sheet"""
    excel = _import_excel()
    result = excel.list_excel_sheets(excel_path=excel_path)
    click.echo(result)


@cli.command()
@click.option("--sheet", required=True, help="Sheet 名称")
@click.option("--data", required=True, help="新的收据数据 JSON")
@click.option("--excel-path", default=DEFAULT_EXCEL, help="Excel 文件路径")
@click.option("--image-path", default=None, help="收据图片路径")
def update(sheet, data, excel_path, image_path):
    """更新收据"""
    import json
    excel = _import_excel()
    receipt_data = json.loads(data)
    result = excel.update_receipt_in_excel(
        sheet_name=sheet, receipt_data=receipt_data,
        excel_path=excel_path, image_path=image_path,
    )
    click.echo(result)


@cli.command()
@click.option("--sheet", required=True, help="Sheet 名称")
@click.option("--excel-path", default=DEFAULT_EXCEL, help="Excel 文件路径")
def delete(sheet, excel_path):
    """删除收据 Sheet"""
    excel = _import_excel()
    result = excel.delete_receipt_from_excel(sheet_name=sheet, excel_path=excel_path)
    click.echo(result)


@cli.command()
@click.option("--sources", required=True, help="源文件路径，逗号分隔")
@click.option("--target", default=DEFAULT_EXCEL, help="目标文件路径")
@click.option("--no-dedup", is_flag=True, help="不删除重复")
def merge(sources, target, no_dedup):
    """合并多个 Excel 文件"""
    excel = _import_excel()
    source_list = [s.strip() for s in sources.split(",")]
    result = excel.merge_excel_files(
        source_paths=source_list, target_path=target,
        remove_duplicates=not no_dedup,
    )
    click.echo(result)


@cli.command()
@click.option("--excel-path", default=DEFAULT_EXCEL, help="Excel 文件路径")
@click.option("--order", default="desc", type=click.Choice(["asc", "desc"]), help="排序顺序")
def sort(excel_path, order):
    """按日期排序 Sheet"""
    excel = _import_excel()
    result = excel.sort_sheets_by_date(excel_path=excel_path, order=order)
    click.echo(result)


@cli.command()
@click.option("--old", "old_name", required=True, help="旧 Sheet 名称")
@click.option("--new", "new_name", required=True, help="新 Sheet 名称")
@click.option("--excel-path", default=DEFAULT_EXCEL, help="Excel 文件路径")
def rename(old_name, new_name, excel_path):
    """重命名 Sheet"""
    excel = _import_excel()
    result = excel.rename_sheet(old_name=old_name, new_name=new_name, excel_path=excel_path)
    click.echo(result)


@cli.command("rename-auto")
@click.option("--old", "old_name", required=True, help="旧 Sheet 名称")
@click.option("--date", "date_str", required=True, help="日期字符串，如 9-1")
@click.option("--excel-path", default=DEFAULT_EXCEL, help="Excel 文件路径")
def rename_auto_cmd(old_name, date_str, excel_path):
    """自动重命名为 主题（日期）格式"""
    excel = _import_excel()
    result = excel.rename_sheet_auto(old_name=old_name, date_str=date_str, excel_path=excel_path)
    click.echo(result)


@cli.command()
@click.option("--excel-path", default=DEFAULT_EXCEL, help="Excel 文件路径")
def beautify(excel_path):
    """美化 Excel 样式"""
    excel = _import_excel()
    result = excel.beautify_excel(excel_path=excel_path)
    click.echo(result)


# ============================================================================
# 查询命令
# ============================================================================

@cli.command("list")
@click.option("--excel-path", default=DEFAULT_EXCEL, help="Excel 文件路径")
@click.option("--filter", "title_filter", default=None, help="按主题筛选")
@click.option("--from", "from_date", default=None, help="起始日期 (YYYY-M-D)")
@click.option("--to", "to_date", default=None, help="结束日期 (YYYY-M-D)")
@click.option("--limit", default=20, help="显示数量")
def list_cmd(excel_path, title_filter, from_date, to_date, limit):
    """列出收据"""
    query = _import_query()
    result = query.list_receipts(
        excel_path=excel_path, title_filter=title_filter,
        from_date=from_date, to_date=to_date, limit=limit,
    )
    click.echo(result)


@cli.command()
@click.option("--keyword", required=True, help="搜索关键词")
@click.option("--excel-path", default=DEFAULT_EXCEL, help="Excel 文件路径")
@click.option("--limit", default=20, help="显示数量")
def search(keyword, excel_path, limit):
    """按关键词搜索收据"""
    query = _import_query()
    result = query.search_receipts_by_keyword(keyword=keyword, excel_path=excel_path, limit=limit)
    click.echo(result)


@cli.command("by-date")
@click.option("--date", "target_date", required=True, help="目标日期 (YYYY-M-D)")
@click.option("--excel-path", default=DEFAULT_EXCEL, help="Excel 文件路径")
def by_date_cmd(target_date, excel_path):
    """获取指定日期的收据"""
    query = _import_query()
    result = query.get_receipt_by_date(target_date=target_date, excel_path=excel_path)
    click.echo(result)


@cli.command()
@click.option("--sheet", required=True, help="Sheet 名称")
@click.option("--excel-path", default=DEFAULT_EXCEL, help="Excel 文件路径")
def summary(sheet, excel_path):
    """获取收据摘要"""
    query = _import_query()
    result = query.get_receipt_summary(sheet_name=sheet, excel_path=excel_path)
    click.echo(result)


# ============================================================================
# 统计命令
# ============================================================================

@cli.command()
@click.option("--excel-path", default=DEFAULT_EXCEL, help="Excel 文件路径")
def stats(excel_path):
    """获取统计信息"""
    st = _import_stats()
    result = st.get_statistics(excel_path=excel_path)
    click.echo(result)


@cli.command("export-json")
@click.option("--output", default=None, help="输出文件路径")
@click.option("--excel-path", default=DEFAULT_EXCEL, help="Excel 文件路径")
def export_json_cmd(output, excel_path):
    """导出统计为 JSON"""
    st = _import_stats()
    result = st.export_statistics_json(output_path=output, excel_path=excel_path)
    click.echo(result)


@cli.command()
@click.option("--period", default="month", type=click.Choice(["month", "week", "day"]), help="分析周期")
@click.option("--excel-path", default=DEFAULT_EXCEL, help="Excel 文件路径")
def analyze(period, excel_path):
    """按周期分析收据"""
    st = _import_stats()
    result = st.analyze_by_period(period=period, excel_path=excel_path)
    click.echo(result)


@cli.command("top-items")
@click.option("--limit", default=10, help="显示数量")
@click.option("--excel-path", default=DEFAULT_EXCEL, help="Excel 文件路径")
def top_items_cmd(limit, excel_path):
    """获取购买最多的商品"""
    st = _import_stats()
    result = st.get_top_items(excel_path=excel_path, limit=limit)
    click.echo(result)


@cli.command()
@click.option("--year", default=None, type=int, help="年份")
@click.option("--excel-path", default=DEFAULT_EXCEL, help="Excel 文件路径")
def monthly(year, excel_path):
    """获取月度汇总"""
    st = _import_stats()
    result = st.get_monthly_summary(year=year, excel_path=excel_path)
    click.echo(result)


@cli.command("merge-by-date")
@click.argument("date")
@click.option("--excel-path", default=DEFAULT_EXCEL, help="Excel 文件路径")
@click.option("--keep-original", is_flag=True, help="保留原 Sheet（默认删除）")
def merge_by_date_cmd(date, excel_path, keep_original):
    """按日期合并收据（删除原 Sheet）

    \b
    示例:
        合并 2026年2月26日的收据: merge-by-date 2026-2-26
        合并 2月26日的收据:       merge-by-date 2-26
        合并并保留原表:           merge-by-date 2-26 --keep-original
    """
    excel = _import_excel()
    result = excel.merge_by_date(
        target_date=date,
        excel_path=excel_path,
        keep_original=keep_original,
    )
    click.echo(result)


if __name__ == "__main__":
    cli()
