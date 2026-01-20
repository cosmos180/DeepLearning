"""
Excel处理模块

负责读取和写入采购明细Excel文件，格式符合实际使用的309 采购明细.xlsx结构。
"""

from pathlib import Path
from typing import List, Optional, Tuple
from datetime import date
from decimal import Decimal
import shutil
import re

try:
    from openpyxl import Workbook, load_workbook
    from openpyxl.styles import Font, Alignment, Border, Side, PatternFill
    from openpyxl.utils import get_column_letter
except ImportError:
    raise ImportError(
        "需要安装 openpyxl: pip install openpyxl"
    )

from . import PurchaseReceipt, PurchaseItem


class ExcelHandler:
    """
    Excel处理器

    负责读取和写入采购明细Excel文件。
    """

    # 表格列定义
    COLS = {
        "sequence": "A",    # 序号
        "name": "B",        # 商品名称
        "spec": "C",        # 规格型号
        "unit": "D",        # 单位
        "quantity": "E",    # 采购数量
        "unit_price": "F",  # 单价（元）
        "amount": "G",      # 金额（元）
        "remark": "H",      # 备注
    }

    # 固定值
    DEFAULT_PURCHASER = "梁程程妈妈"
    DEFAULT_PAYMENT_METHOD = "转账"

    def __init__(self, file_path: Path, auto_backup: bool = True):
        """
        初始化Excel处理器

        Args:
            file_path: Excel文件路径
            auto_backup: 是否自动备份
        """
        self.file_path = Path(file_path).expanduser()
        self.auto_backup = auto_backup
        self._workbook = None

    def _load_workbook(self) -> Workbook:
        """加载工作簿"""
        if self._workbook is None:
            if self.file_path.exists():
                self._workbook = load_workbook(self.file_path)
            else:
                # 创建新工作簿
                self._workbook = Workbook()
                # 删除默认Sheet
                if "Sheet" in self._workbook.sheetnames:
                    self._workbook.remove(self._workbook["Sheet"])
        return self._workbook

    def _backup(self):
        """备份Excel文件"""
        if self.auto_backup and self.file_path.exists():
            backup_path = self.file_path.with_suffix(
                f".bak.{date.today().isoformat()}"
            )
            shutil.copy2(self.file_path, backup_path)

    def sheet_exists(self, sheet_name: str) -> bool:
        """
        检查Sheet是否存在

        Args:
            sheet_name: Sheet名称

        Returns:
            是否存在
        """
        wb = self._load_workbook()
        return sheet_name in wb.sheetnames

    def add_receipt(self, receipt: PurchaseReceipt) -> None:
        """
        添加收据到Excel

        Args:
            receipt: 收据数据
        """
        # 备份
        self._backup()

        # 加载工作簿
        wb = self._load_workbook()

        # 创建或更新Sheet
        sheet_name = receipt.sheet_name
        if sheet_name in wb.sheetnames:
            # 更新现有Sheet
            ws = wb[sheet_name]
            self._update_sheet(ws, receipt)
        else:
            # 创建新Sheet
            ws = wb.create_sheet(title=sheet_name)
            self._create_sheet(ws, receipt)

        # 保存
        self._save()

    def _create_sheet(self, ws, receipt: PurchaseReceipt):
        """
        创建新Sheet

        Sheet布局：
        第1行: 主题标题
        第2行: 采购方信息
        第3行: (空)
        第4行: 表头
        第5行起: 商品明细
        倒数第2行: 总计
        最后1行: 交付信息
        """
        # 1. 标题行 (第1行)
        ws.merge_cells("A1:T1")
        ws["A1"] = receipt.title
        ws["A1"].font = Font(size=16, bold=True)
        ws["A1"].alignment = Alignment(horizontal="center", vertical="center")

        # 2. 采购方信息 (第2行)
        ws["A2"] = "采购方：_____________________ 联系方式："
        ws["B2"] = receipt.purchaser
        ws["A2"].font = Font(size=11)
        ws["B2"].font = Font(size=11)

        # 3. 表头 (第4行)
        headers = ["序号", "商品名称", "规格型号", "单位", "采购数量", "单价（元）", "金额（元）", "备注"]
        for col, header in enumerate(headers, 1):
            cell = ws.cell(row=4, column=col, value=header)
            cell.font = Font(bold=True, size=11)
            cell.alignment = Alignment(horizontal="center", vertical="center")
            cell.fill = PatternFill(start_color="D3D3D3", end_color="D3D3D3", fill_type="solid")

        # 4. 商品明细 (第5行起)
        row = 5
        for item in receipt.items:
            ws[f"A{row}"] = item.sequence
            ws[f"B{row}"] = item.name
            ws[f"C{row}"] = item.spec or ""
            ws[f"D{row}"] = item.unit
            ws[f"E{row}"] = float(item.quantity)
            ws[f"F{row}"] = float(item.unit_price)

            # 金额公式
            ws[f"G{row}"] = f"=E{row}*F{row}"
            ws[f"G{row}"].number_format = "#,##0.00"

            ws[f"H{row}"] = item.remark or ""

            row += 1

        # 5. 总计行 (倒数第2行)
        ws[f"A{row}"] = "总计金额"
        ws[f"A{row}"].font = Font(bold=True)
        ws[f"G{row}"] = f"=SUM(G5:G{row-1})"
        ws[f"G{row}"].font = Font(bold=True)
        ws[f"G{row}"].number_format = "#,##0.00"

        # 6. 交付信息 (最后1行)
        row += 1
        delivery_date_str = receipt.delivery_date.strftime("%Y-%-m-%-d")
        ws[f"A{row}"] = f"交付日期：{delivery_date_str}    付款方式：{receipt.payment_method}"
        ws[f"A{row}"].font = Font(size=10)

        # 7. 设置列宽
        column_widths = {
            "A": 6,   # 序号
            "B": 30,  # 商品名称
            "C": 15,  # 规格型号
            "D": 8,   # 单位
            "E": 12,  # 采购数量
            "F": 12,  # 单价
            "G": 12,  # 金额
            "H": 20,  # 备注
        }
        for col, width in column_widths.items():
            ws.column_dimensions[col].width = width

        # 8. 设置行高
        ws.row_dimensions[1].height = 30  # 标题行
        for r in range(4, row + 1):
            ws.row_dimensions[r].height = 20  # 数据行

    def _update_sheet(self, ws, receipt: PurchaseReceipt):
        """
        更新现有Sheet
        """
        # 清空现有数据（保留前4行）
        max_row = ws.max_row
        if max_row > 4:
            ws.delete_rows(5, max_row - 4)

        # 重新创建
        self._create_sheet(ws, receipt)

    def _save(self):
        """保存工作簿"""
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        if self._workbook:
            self._workbook.save(self.file_path)

    def read_receipt(self, sheet_name: str) -> Optional[PurchaseReceipt]:
        """
        从Sheet读取收据

        Args:
            sheet_name: Sheet名称

        Returns:
            收据数据，如果Sheet不存在返回None
        """
        wb = self._load_workbook()

        if sheet_name not in wb.sheetnames:
            return None

        ws = wb[sheet_name]

        # 1. 读取标题
        title = ws["A1"].value or ""

        # 2. 读取采购方
        purchaser = ws["B2"].value or self.DEFAULT_PURCHASER

        # 3. 读取交付日期（从最后一行）
        last_row = ws.max_row
        delivery_info = ws[f"A{last_row}"].value or ""
        delivery_date = self._parse_delivery_date(delivery_info)

        # 4. 读取商品明细
        items = []
        row = 5
        while row <= last_row:
            seq = ws[f"A{row}"].value
            name = ws[f"B{row}"].value

            # 跳过空行
            if not seq and not name:
                row += 1
                continue

            # 跳过"总计金额"行和交付信息行
            if isinstance(seq, str) and ("总计" in seq or "交付" in seq or "付款" in seq):
                break
            if isinstance(name, str) and ("总计" in name or "交付" in name or "付款" in name):
                break

            # 确保seq是数字
            try:
                seq_num = int(seq) if seq else 0
            except (ValueError, TypeError):
                row += 1
                continue

            item = PurchaseItem(
                sequence=seq_num,
                name=name or "",
                spec=ws[f"C{row}"].value,
                unit=ws[f"D{row}"].value or "个",
                quantity=Decimal(str(ws[f"E{row}"].value or 0)),
                unit_price=Decimal(str(ws[f"F{row}"].value or 0)),
                remark=ws[f"H{row}"].value,
            )
            items.append(item)
            row += 1

        return PurchaseReceipt(
            title=title,
            delivery_date=delivery_date,
            purchaser=purchaser,
            items=items,
            recognition_method="excel",
        )

    def list_sheets(self) -> List[str]:
        """
        列出所有Sheet名称

        Returns:
            Sheet名称列表
        """
        wb = self._load_workbook()
        return wb.sheetnames

    def _parse_delivery_date(self, delivery_info: str) -> date:
        """
        从交付信息中解析日期

        格式：交付日期：2025-1-20    付款方式：转账

        Args:
            delivery_info: 交付信息字符串

        Returns:
            日期
        """
        # 提取日期部分
        match = re.search(r'(\d{4})-(\d{1,2})-(\d{1,2})', delivery_info)
        if match:
            year, month, day = match.groups()
            return date(int(year), int(month), int(day))

        # 默认返回今天
        return date.today()

    def get_statistics(self) -> dict:
        """
        获取统计信息

        Returns:
            统计信息字典
        """
        wb = self._load_workbook()
        sheets = wb.sheetnames

        receipts = []
        for sheet_name in sheets:
            receipt = self.read_receipt(sheet_name)
            if receipt:
                receipts.append(receipt)

        total_amount = sum(r.total_amount for r in receipts)
        total_items = sum(r.item_count for r in receipts)

        return {
            "sheet_count": len(sheets),
            "receipt_count": len(receipts),
            "total_amount": float(total_amount),
            "total_items": total_items,
            "recent_receipts": [
                {
                    "title": r.title,
                    "date": r.delivery_date.isoformat(),
                    "amount": float(r.total_amount),
                    "sheet": r.sheet_name,
                }
                for r in sorted(receipts, key=lambda x: x.delivery_date, reverse=True)[:10]
            ],
        }

    def close(self):
        """关闭工作簿"""
        if self._workbook:
            self._workbook.close()
            self._workbook = None


# 便捷函数
def load_excel(file_path: str) -> ExcelHandler:
    """
    加载Excel文件

    Args:
        file_path: 文件路径

    Returns:
        ExcelHandler实例
    """
    return ExcelHandler(Path(file_path))


def create_receipt_from_excel(file_path: str, sheet_name: str) -> Optional[PurchaseReceipt]:
    """
    从Excel创建收据

    Args:
        file_path: Excel文件路径
        sheet_name: Sheet名称

    Returns:
        收据数据
    """
    handler = load_excel(file_path)
    receipt = handler.read_receipt(sheet_name)
    handler.close()
    return receipt


def save_receipt_to_excel(file_path: str, receipt: PurchaseReceipt) -> None:
    """
    保存收据到Excel

    Args:
        file_path: Excel文件路径
        receipt: 收据数据
    """
    handler = load_excel(file_path)
    handler.add_receipt(receipt)
    handler.close()
