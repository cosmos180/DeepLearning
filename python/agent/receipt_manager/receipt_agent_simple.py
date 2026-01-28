#!/usr/bin/env python3
"""
采购收据管理智能助手 - 简化版
直接支持自然语言调用工具（无需 LLM）
"""

import os
import sys
from pathlib import Path

# 添加祖父目录到 Python 路径，以便工具可以导入 receipt_manager 模块
_agent_file = Path(__file__).resolve()
_grandparent_dir = _agent_file.parent.parent.parent
if str(_grandparent_dir) not in sys.path:
    sys.path.insert(0, str(_grandparent_dir))

import re
from datetime import date
from typing import Optional

# 导入所有工具
from tools.ocr_tool import (
    recognize_receipt,
    batch_recognize,
    create_manual_receipt,
)

from tools.excel_tool import (
    save_receipt_to_excel,
    read_receipt_from_excel,
    list_excel_sheets,
    update_receipt_in_excel,
    delete_receipt_from_excel,
)

from tools.query_tool import (
    list_receipts,
    search_receipts_by_keyword,
    get_receipt_by_date,
    get_receipt_summary,
)

from tools.stats_tool import (
    get_statistics,
    export_statistics_json,
    analyze_by_period,
    get_top_items,
    get_monthly_summary,
)


def parse_date(text: str) -> Optional[str]:
    """从文本中解析日期（YYYY-M-D 格式）"""
    # 匹配 YYYY-M-D 或 YYYY-M-D 格式
    patterns = [
        r'(\d{4})-(\d{1,2})-(\d{1,2})',  # YYYY-M-D
        r'(\d{4})年(\d{1,2})月(\d{1,2})日',  # YYYY年M月D日
        r'(\d{1,2})月(\d{1,2})日',  # M月D日（默认当年）
    ]

    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            groups = match.groups()
            if len(groups) == 3:
                if "年" in pattern:
                    return f"{groups[0]}-{groups[1]}-{groups[2]}"
                elif len(groups[0]) == 4:
                    return f"{groups[0]}-{groups[1]}-{groups[2]}"
            return f"{date.today().year}-{groups[0]}-{groups[1]}"

    return None


def parse_image_path(text: str) -> Optional[str]:
    """从文本中解析图片路径"""
    # 匹配常见图片路径格式
    patterns = [
        r'["\']?([/\w\-.\s]+\.(?:jpg|jpeg|png|bmp|gif|webp))["\']?',
        r'图片[:：]\s*([/\w\-.\s]+\.(?:jpg|jpeg|png|bmp|gif|webp))',
        r'识别[:：]\s*([/\w\-.\s]+\.(?:jpg|jpeg|png|bmp|gif|webp))',
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1)

    # 如果文本本身就是路径
    if re.match(r'^[/\w\-.\s]+\.(?:jpg|jpeg|png|bmp|gif|webp)$', text.strip(), re.IGNORECASE):
        return text.strip()

    return None


def parse_sheet_name(text: str) -> Optional[str]:
    """从文本中解析 Sheet 名称"""
    # 常见关键词后跟名称
    patterns = [
        r'Sheet[:：]\s*([^，。\n]+)',
        r'收据[:：]\s*([^，。\n]+)',
        r'删除[:：]\s*([^，。\n]+)',
        r'更新[:：]\s*([^，。\n]+)',
    ]

    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(1).strip()

    return None


def process_query(user_input: str) -> str:
    """
    处理用户查询，自动路由到合适的工具

    支持的自然语言格式:
    - "识别这张收据图片 ./receipt.jpg"
    - "列出所有收据"
    - "查看 2025-01-20 的收据"
    - "显示统计信息"
    """
    user_input_lower = user_input.lower()
    user_input_stripped = user_input.strip()

    # ==================== AI 识别 ====================
    if any(kw in user_input_lower for kw in ['识别', 'recognize', 'ocr', '收据图片', '图片']):
        image_path = parse_image_path(user_input_stripped)

        # 批量识别
        if '批量' in user_input_lower or any(kw in user_input_lower for kw in ['文件夹', 'folder', '目录', '批量']):
            folder_match = re.search(r'[/\w\-.\s]+', user_input_stripped)
            if folder_match:
                folder = folder_match.group().strip()
                return batch_recognize(folder_path=folder)

        # 单张识别
        if image_path:
            return recognize_receipt(image_path=image_path)

        return "📖 请提供图片路径，例如：\n  - 识别 ./receipt.jpg\n  - 批量识别 ./receipts 文件夹"

    # ==================== 手动创建 ====================
    if any(kw in user_input_lower for kw in ['创建', '手动', 'manual', 'new', 'add']):
        # 简化版：提示使用完整参数
        return "📖 手动创建收据需要提供完整参数，请使用:\n  create_manual_receipt(title='主题', delivery_date='2025-01-20', items=[...])"

    # ==================== Excel 操作 ====================
    if any(kw in user_input_lower for kw in ['保存', 'save', '导出', 'export', '存入']):
        # 提示需要先识别收据
        return "📖 请先使用 AI 识别收据，识别后会自动保存到 Excel"

    if any(kw in user_input_lower for kw in ['读取', '查看', 'read', '查看 sheet', 'sheet']):
        sheet_name = parse_sheet_name(user_input_stripped)
        if sheet_name:
            return read_receipt_from_excel(sheet_name=sheet_name)
        return list_excel_sheets()

    if any(kw in user_input_lower for kw in ['删除', 'delete', '移除']):
        sheet_name = parse_sheet_name(user_input_stripped)
        if sheet_name:
            return delete_receipt_from_excel(sheet_name=sheet_name)
        return "📖 请提供要删除的 Sheet 名称"

    if any(kw in user_input_lower for kw in ['更新', 'update', '修改']):
        sheet_name = parse_sheet_name(user_input_stripped)
        if sheet_name:
            return "📖 更新收据需要提供完整数据，请使用:\n  update_receipt_in_excel(sheet_name='...')"

    # ==================== 查询 ====================
    if any(kw in user_input_lower for kw in ['列出', '列表', 'list', '所有收据', '收据列表']):
        # 检查日期范围
        date_str = parse_date(user_input_stripped)
        if date_str:
            return get_receipt_by_date(target_date=date_str)
        return list_receipts()

    if any(kw in user_input_lower for kw in ['搜索', 'search', '查找', 'find', '关键词']):
        keyword_match = re.search(r'关键词[:：]?\s*["\']?([^"\']+)["\']?', user_input_stripped)
        if keyword_match:
            keyword = keyword_match.group(1).strip()
        else:
            # 提取可能的搜索词
            words = re.findall(r'[\u4e00-\u9fa5]+', user_input_stripped)
            keyword = words[-1] if words else None

        if keyword:
            return search_receipts_by_keyword(keyword=keyword)
        return "📖 请提供搜索关键词，例如：\n  - 搜索包含「打印」的收据"

    if any(kw in user_input_lower for kw in ['统计', '汇总', 'summary', 'stat']):
        if '月度' in user_input_lower or '每月' in user_input_lower:
            year_match = re.search(r'(\d{4})', user_input_stripped)
            year = int(year_match.group(1)) if year_match else None
            return get_monthly_summary(year=year)

        if '周期' in user_input_lower or '分析' in user_input_lower:
            period = 'month' if '月' in user_input_lower else 'week' if '周' in user_input_lower else 'day'
            return analyze_by_period(period=period)

        if '排行' in user_input_lower or 'top' in user_input_lower or '最多' in user_input_lower:
            return get_top_items()

        return get_statistics()

    # ==================== 默认: 显示帮助 ====================
    return show_help()


def show_help() -> str:
    """显示帮助信息"""
    return """
📖 使用指南

【AI 识别】
  识别 ./receipt.jpg
  批量识别 ./receipts 文件夹

【查询】
  列出所有收据
  查看 2025-01-20 的收据
  搜索包含「打印」的收据
  查看收据列表

【统计】
  显示统计信息
  查看月度汇总
  查看商品排行榜
  按月分析

【Excel 操作】
  列出所有 Sheet
  查看 Sheet 数学资料打印（1-20）
  删除 Sheet xxx

【直接调用工具】
  recognize_receipt(image_path='./receipt.jpg')
  list_receipts()
  get_statistics()
"""


def main():
    """运行交互式 Agent"""
    print("采购收据管理智能助手")
    print("=" * 60)
    print("💡 输入自然语言查询，如:")
    print("   - 识别 ./receipt.jpg")
    print("   - 列出所有收据")
    print("   - 查看统计信息")
    print("   - 输入 'help' 查看更多帮助")
    print("   - 输入 'quit' 退出")
    print("=" * 60)
    print()

    while True:
        try:
            user_input = input("你: ").strip()
            if not user_input:
                continue
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("再见！")
                break
            if user_input.lower() in ['help', 'h', '?']:
                print(show_help())
                continue

            # 处理查询
            result = process_query(user_input)
            print(f"\n助手: {result}\n")

        except KeyboardInterrupt:
            print("\n再见！")
            break
        except Exception as e:
            print(f"\n❌ 错误: {str(e)}\n")


if __name__ == "__main__":
    main()
