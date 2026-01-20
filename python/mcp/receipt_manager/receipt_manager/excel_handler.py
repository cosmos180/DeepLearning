"""
Excel处理模块

负责读取和写入采购明细Excel文件，格式符合实际使用的309 采购明细.xlsx结构。
"""

from pathlib import Path
from typing import List, Optional
from datetime import date
from decimal import Decimal
import shutil
import re
import logging

logger = logging.getLogger(__name__)

try:
    from openpyxl import Workbook, load_workbook
    from openpyxl.styles import Font, Alignment, Border, Side, PatternFill
    from openpyxl.drawing.image import Image
except ImportError:
    raise ImportError(
        "需要安装 openpyxl: pip install openpyxl"
    )


# 样式定义
class Styles:
    """Excel样式定义"""

    # 细边框
    THIN_BORDER = Border(
        left=Side(style='thin', color='000000'),
        right=Side(style='thin', color='000000'),
        top=Side(style='thin', color='000000'),
        bottom=Side(style='thin', color='000000'),
    )

    # 标题样式
    TITLE_FONT = Font(size=16, bold=True)
    TITLE_ALIGNMENT = Alignment(horizontal='center', vertical='center')

    # 表头样式
    HEADER_FONT = Font(bold=True, size=11)
    HEADER_ALIGNMENT = Alignment(horizontal='center', vertical='center')
    HEADER_FILL = PatternFill(start_color='D3D3D3', end_color='D3D3D3', fill_type='solid')

    # 数据行样式（居中对齐）
    DATA_FONT = Font(size=11)
    DATA_ALIGNMENT = Alignment(horizontal='center', vertical='center')

    # 总计行样式
    TOTAL_FONT = Font(bold=True, size=11)

    # 金额格式（带人民币符号）
    CURRENCY_FORMAT = '¥#,##0.00'

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
        创建新Sheet - 业界最佳实践布局

        布局设计：
        第1行: 收据标题（居中，大字体）
        第2行: 采购方信息（左侧标签，右侧内容）
        第3行: 空行（分隔）
        第4行: 表头（灰色背景，居中）
        第5行起: 商品明细（带边框）
        倒数第2行: 总计（加粗）
        最后1行: 交付信息（分列显示）

        对齐原则：
        - 文本内容：左对齐
        - 数值内容：右对齐
        - 表头：居中对齐
        """
        # ========== 1. 标题区域 ==========
        ws.merge_cells("A1:H1")
        ws["A1"] = receipt.title
        ws["A1"].font = Styles.TITLE_FONT
        ws["A1"].alignment = Styles.TITLE_ALIGNMENT
        ws.row_dimensions[1].height = 35

        # ========== 2. 采购方信息（分列布局）==========
        ws["A2"] = "采购方："
        ws["B2"] = receipt.purchaser
        ws["D2"] = "日期："
        ws["E2"] = receipt.delivery_date.strftime("%Y年%m月%d日")

        # 设置采购方信息样式
        for cell in [ws["A2"], ws["B2"], ws["D2"], ws["E2"]]:
            cell.font = Styles.DATA_FONT
            cell.alignment = Alignment(horizontal="left", vertical="center")
        # 标签加粗
        ws["A2"].font = Font(size=11, bold=True)
        ws["D2"].font = Font(size=11, bold=True)

        # ========== 3. 空行分隔 ==========
        ws.row_dimensions[3].height = 10

        # ========== 4. 表头行 ==========
        headers = ["序号", "商品名称", "规格型号", "单位", "数量", "单价", "金额", "备注"]
        header_range = f"A4:H4"
        for col_idx, header in enumerate(headers, 1):
            cell = ws.cell(row=4, column=col_idx, value=header)
            cell.font = Styles.HEADER_FONT
            cell.alignment = Styles.HEADER_ALIGNMENT
            cell.fill = Styles.HEADER_FILL
            cell.border = Styles.THIN_BORDER
        ws.row_dimensions[4].height = 25

        # ========== 5. 商品明细 ==========
        row = 5
        for item in receipt.items:
            # 序号 - 居中
            ws[f"A{row}"] = item.sequence
            ws[f"A{row}"].alignment = Alignment(horizontal="center", vertical="center")

            # 商品名称 - 左对齐
            ws[f"B{row}"] = item.name
            ws[f"B{row}"].alignment = Alignment(horizontal="left", vertical="center")

            # 规格型号 - 左对齐
            ws[f"C{row}"] = item.spec or ""
            ws[f"C{row}"].alignment = Alignment(horizontal="left", vertical="center")

            # 单位 - 居中
            ws[f"D{row}"] = item.unit
            ws[f"D{row}"].alignment = Alignment(horizontal="center", vertical="center")

            # 数量 - 右对齐
            ws[f"E{row}"] = float(item.quantity)
            ws[f"E{row}"].alignment = Alignment(horizontal="right", vertical="center")

            # 单价 - 右对齐，货币格式
            ws[f"F{row}"] = float(item.unit_price)
            ws[f"F{row}"].number_format = Styles.CURRENCY_FORMAT
            ws[f"F{row}"].alignment = Alignment(horizontal="right", vertical="center")

            # 金额 - 右对齐，公式+货币格式
            ws[f"G{row}"] = f"=E{row}*F{row}"
            ws[f"G{row}"].number_format = Styles.CURRENCY_FORMAT
            ws[f"G{row}"].alignment = Alignment(horizontal="right", vertical="center")

            # 备注 - 左对齐
            ws[f"H{row}"] = item.remark or ""
            ws[f"H{row}"].alignment = Alignment(horizontal="left", vertical="center")

            # 统一设置字体和边框
            for col in range(1, 9):
                cell = ws.cell(row=row, column=col)
                cell.font = Styles.DATA_FONT
                cell.border = Styles.THIN_BORDER

            ws.row_dimensions[row].height = 22
            row += 1

        # ========== 6. 总计行 ==========
        ws.merge_cells(f"A{row}:F{row}")
        ws[f"A{row}"] = "总    计"
        ws[f"A{row}"].font = Styles.TOTAL_FONT
        ws[f"A{row}"].alignment = Alignment(horizontal="center", vertical="center")
        ws[f"A{row}"].border = Styles.THIN_BORDER

        ws[f"G{row}"] = f"=SUM(G5:G{row-1})"
        ws[f"G{row}"].font = Styles.TOTAL_FONT
        ws[f"G{row}"].number_format = Styles.CURRENCY_FORMAT
        ws[f"G{row}"].alignment = Alignment(horizontal="right", vertical="center")
        ws[f"G{row}"].border = Styles.THIN_BORDER

        ws[f"H{row}"].border = Styles.THIN_BORDER
        ws.row_dimensions[row].height = 25

        # ========== 7. 交付信息（分列）==========
        row += 1
        ws["A" + str(row)] = "交付日期："
        ws["B" + str(row)] = receipt.delivery_date.strftime("%Y年%m月%d日")
        ws["D" + str(row)] = "付款方式："
        ws["E" + str(row)] = receipt.payment_method

        # 设置样式
        for col in ["A", "B", "D", "E"]:
            cell = ws[f"{col}{row}"]
            cell.font = Font(size=10)
            cell.alignment = Alignment(horizontal="left", vertical="center")
        # 标签加粗
        ws[f"A{row}"].font = Font(size=10, bold=True)
        ws[f"D{row}"].font = Font(size=10, bold=True)

        ws.row_dimensions[row].height = 20

        # ========== 8. 插入原始收据图片（表格下方）==========
        image_row = row + 2  # 在交付信息后空一行

        if receipt.source_file:
            image_path = Path(receipt.source_file)
            if image_path.exists():
                try:
                    # 加载图片
                    img = Image(str(image_path))

                    # 设置图片大小（保持比例，限制最大宽度）
                    max_width = 500  # 像素，加宽以适应表格宽度
                    if img.width > max_width:
                        ratio = max_width / img.width
                        img.width = max_width
                        img.height = int(img.height * ratio)

                    # 将图片放在表格下方
                    img.anchor = f"A{image_row}"
                    ws.add_image(img)

                    # 添加"原始凭证"标题
                    ws[f"A{image_row}"] = "原始凭证"
                    ws[f"A{image_row}"].font = Font(size=12, bold=True)
                    ws[f"A{image_row}"].alignment = Alignment(horizontal="left")

                    # 设置图片所在行的高度
                    ws.row_dimensions[image_row].height = 20  # 标题行高度
                    image_row += 1
                    # 预留图片空间（每行约15像素，动态计算）
                    img_height_rows = max(15, int(img.height / 15) + 2)
                    for r in range(image_row, image_row + img_height_rows):
                        if r not in ws.row_dimensions:
                            ws.row_dimensions[r].height = 15

                    logger.info(f"✓ 已插入收据图片: {image_path.name}")
                except Exception as e:
                    logger.warning(f"插入图片失败: {e}")

        # ========== 9. 设置列宽 ==========
        column_widths = {
            "A": 8,    # 序号
            "B": 35,   # 商品名称（加宽）
            "C": 18,   # 规格型号
            "D": 10,   # 单位
            "E": 12,   # 数量
            "F": 14,   # 单价
            "G": 14,   # 金额
            "H": 25,   # 备注
        }
        for col, width in column_widths.items():
            ws.column_dimensions[col].width = width

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

        # 3. 读取交付日期（从最后一行的A列）
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
