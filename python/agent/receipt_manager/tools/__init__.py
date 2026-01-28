"""
Agent Tools Package
导出所有 receipt_manager agent 工具函数
"""

from .ocr_tool import (
    recognize_receipt,
    batch_recognize,
    create_manual_receipt,
)

from .excel_tool import (
    save_receipt_to_excel,
    read_receipt_from_excel,
    list_excel_sheets,
    update_receipt_in_excel,
    delete_receipt_from_excel,
    merge_excel_files,
    sort_sheets_by_date,
    rename_sheet,
    rename_sheet_auto,
)

from .query_tool import (
    list_receipts,
    search_receipts_by_keyword,
    get_receipt_by_date,
    get_receipt_summary,
)

from .stats_tool import (
    get_statistics,
    export_statistics_json,
    analyze_by_period,
    get_top_items,
    get_monthly_summary,
)

__all__ = [
    # OCR 工具
    "recognize_receipt",
    "batch_recognize",
    "create_manual_receipt",
    # Excel 工具
    "save_receipt_to_excel",
    "read_receipt_from_excel",
    "list_excel_sheets",
    "update_receipt_in_excel",
    "delete_receipt_from_excel",
    "merge_excel_files",
    "sort_sheets_by_date",
    "rename_sheet",
    "rename_sheet_auto",
    # 查询工具
    "list_receipts",
    "search_receipts_by_keyword",
    "get_receipt_by_date",
    "get_receipt_summary",
    # 统计工具
    "get_statistics",
    "export_statistics_json",
    "analyze_by_period",
    "get_top_items",
    "get_monthly_summary",
]
