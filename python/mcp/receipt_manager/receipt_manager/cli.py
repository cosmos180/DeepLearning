"""
命令行界面模块

提供友好的CLI交互界面。
"""

import sys
import json
import logging
from pathlib import Path
from typing import Optional, List
from datetime import date
from decimal import Decimal

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn

from . import PurchaseReceipt, create_receipt
from .excel_handler import ExcelHandler
from .ai_ocr import AIRecognizer, recognize_receipt

logger = logging.getLogger(__name__)

# 支持的图片格式
IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.bmp', '.gif', '.webp', '.tiff'}


# 初始化控制台
console = Console()


def print_receipt_summary(receipt: PurchaseReceipt):
    """
    打印收据摘要

    Args:
        receipt: 收据数据
    """
    # 商品表格
    table = Table(title=f"[bold cyan]{receipt.title}[/bold cyan]", show_header=True, header_style="bold magenta")
    table.add_column("序号", style="dim", width=6)
    table.add_column("商品名称", width=30)
    table.add_column("规格", width=12)
    table.add_column("单位", width=6)
    table.add_column("数量", justify="right", width=8)
    table.add_column("单价", justify="right", width=10)
    table.add_column("金额", justify="right", width=10)
    table.add_column("备注", width=15)

    for item in receipt.items:
        table.add_row(
            str(item.sequence),
            item.name,
            item.spec or "-",
            item.unit,
            f"{item.quantity}",
            f"¥{item.unit_price:.2f}",
            f"¥{item.amount:.2f}",
            item.remark or "-",
        )

    console.print(table)

    # 汇总信息
    summary = f"""
[bold]交付日期:[/bold] {receipt.delivery_date}
[bold]采购方:[/bold] {receipt.purchaser}
[bold]商品数量:[/bold] {receipt.item_count}
[bold]总金额:[/bold] [bold red]¥{receipt.total_amount:.2f}[/bold red]
[bold]识别方式:[/bold] {receipt.recognition_method}
[bold]置信度:[/bold] {receipt.confidence:.2%}
    """
    console.print(Panel(summary, title="汇总信息"))


@click.group()
@click.version_option(version="1.0.0")
@click.option(
    "--excel-file",
    "-e",
    default="~/Downloads/309 采购明细.xlsx",
    help="Excel文件路径",
)
@click.option(
    "--api-key",
    "-k",
    envvar="ARK_API_KEY",
    help="火山引擎API密钥",
)
@click.option(
    "--verbose", "-v",
    is_flag=True,
    help="详细输出",
)
@click.pass_context
def cli(ctx, excel_file, api_key, verbose):
    """
    采购收据管理工具

    使用AI视觉识别自动提取收据信息并保存到Excel。
    """
    ctx.ensure_object(dict)

    # 配置日志
    log_level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(levelname)s: %(message)s',
        stream=sys.stderr,
    )

    # 保存上下文
    ctx.obj["excel_file"] = Path(excel_file).expanduser()
    ctx.obj["api_key"] = api_key
    ctx.obj["verbose"] = verbose

    logger.info(f"Excel文件: {ctx.obj['excel_file']}")


@cli.command()
@click.argument("image", type=click.Path(exists=True))
@click.option(
    "--title", "-t",
    help="主题标题（提示）",
)
@click.option(
    "--date", "-d",
    help="交付日期（YYYY-M-D）",
)
@click.option(
    "--no-ai",
    is_flag=True,
    help="跳过AI识别，手动输入",
)
@click.option(
    "--yes", "-y",
    is_flag=True,
    help="跳过确认直接保存",
)
@click.pass_context
def add(ctx, image, title, date, no_ai, yes):
    """
    添加收据

    IMAGE: 收据图片路径
    """
    excel_file = ctx.obj["excel_file"]
    api_key = ctx.obj["api_key"]

    console.print(f"\n[bold cyan]添加收据:[/bold cyan] {image}\n")

    receipt = None

    if no_ai:
        # 手动输入模式
        receipt = _manual_input(image, title, date)
    else:
        # AI识别模式
        with console.status("[bold green]正在使用AI识别收据...", spinner="dots"):
            receipt, confidence = recognize_receipt(
                image,
                api_key=api_key,
                title_hint=title,
                date_hint=date,
            )

        if receipt is None:
            console.print("[bold red]AI识别失败[/bold red]")
            if click.confirm("是否切换到手动输入模式？"):
                receipt = _manual_input(image, title, date)
            else:
                sys.exit(1)

        # 显示识别结果
        print_receipt_summary(receipt)

        # 确认
        if not yes:
            if confidence < 0.8:
                console.print("[yellow]⚠️  识别置信度较低，请仔细核对信息[/yellow]")

            if not click.confirm("\n确认保存到Excel？"):
                console.print("[yellow]已取消[/yellow]")
                sys.exit(0)

    # 验证数据
    is_valid, errors = receipt.validate()
    if not is_valid:
        console.print("[bold red]数据验证失败:[/bold red]")
        for error in errors:
            console.print(f"  - {error}")
        sys.exit(1)

    # 保存到Excel
    with console.status("[bold green]正在保存到Excel...", spinner="dots"):
        handler = ExcelHandler(excel_file)
        handler.add_receipt(receipt)
        handler.close()

    console.print(f"\n[bold green]✓ 收据已保存到:[/bold green] {receipt.sheet_name}")
    console.print(f"[bold green]✓ Excel文件:[/bold green] {excel_file}\n")


@cli.command()
@click.option(
    "--title", "-t",
    help="按主题筛选",
)
@click.option(
    "--from", "from_date",
    help="起始日期（YYYY-M-D）",
)
@click.option(
    "--to", "to_date",
    help="结束日期（YYYY-M-D）",
)
@click.option(
    "--limit", "-l",
    default=20,
    help="显示数量",
)
@click.pass_context
def list(ctx, title, from_date, to_date, limit):
    """
    列出收据

    显示Excel中的所有收据或按条件筛选。
    """
    excel_file = ctx.obj["excel_file"]

    if not excel_file.exists():
        console.print(f"[bold red]Excel文件不存在: {excel_file}[/bold red]")
        sys.exit(1)

    handler = ExcelHandler(excel_file)
    sheets = handler.list_sheets()

    # 读取收据
    receipts = []
    for sheet_name in sheets:
        receipt = handler.read_receipt(sheet_name)
        if receipt:
            # 筛选
            if title and title.lower() not in receipt.title.lower():
                continue
            if from_date:
                from_d = date.fromisoformat(from_date)
                if receipt.delivery_date < from_d:
                    continue
            if to_date:
                to_d = date.fromisoformat(to_date)
                if receipt.delivery_date > to_d:
                    continue
            receipts.append(receipt)

    handler.close()

    # 排序
    receipts.sort(key=lambda x: x.delivery_date, reverse=True)

    # 限制数量
    receipts = receipts[:limit]

    # 显示
    if not receipts:
        console.print("[yellow]没有找到匹配的收据[/yellow]")
        return

    table = Table(title="收据列表", show_header=True, header_style="bold magenta")
    table.add_column("日期", width=12)
    table.add_column("主题", width=30)
    table.add_column("商品数", justify="right", width=8)
    table.add_column("总金额", justify="right", width=12)
    table.add_column("Sheet", width=25)

    for receipt in receipts:
        table.add_row(
            receipt.delivery_date.isoformat(),
            receipt.title,
            str(receipt.item_count),
            f"¥{receipt.total_amount:.2f}",
            receipt.sheet_name[:25],
        )

    console.print(table)
    console.print(f"\n共 {len(receipts)} 条记录\n")


@cli.command()
@click.option(
    "--format", "-f",
    type=click.Choice(["json", "table"]),
    default="table",
    help="输出格式",
)
@click.option(
    "--output", "-o",
    type=click.Path(),
    help="输出文件路径",
)
@click.pass_context
def export(ctx, format, output):
    """
    导出数据

    将Excel中的收据数据导出为JSON或表格。
    """
    excel_file = ctx.obj["excel_file"]

    if not excel_file.exists():
        console.print(f"[bold red]Excel文件不存在: {excel_file}[/bold red]")
        sys.exit(1)

    handler = ExcelHandler(excel_file)
    stats = handler.get_statistics()
    handler.close()

    if format == "json":
        data = json.dumps(stats, ensure_ascii=False, indent=2)
        if output:
            Path(output).write_text(data, encoding="utf-8")
            console.print(f"[bold green]✓ 已导出到: {output}[/bold green]")
        else:
            console.print(data)
    else:
        # 表格格式
        console.print(f"\n[bold cyan]统计信息[/bold cyan]")
        console.print(f"Sheet数量: {stats['sheet_count']}")
        console.print(f"收据数量: {stats['receipt_count']}")
        console.print(f"商品总数: {stats['total_items']}")
        console.print(f"总金额: [bold red]¥{stats['total_amount']:.2f}[/bold red]\n")


@cli.command()
@click.argument("title")
@click.option(
    "--date", "-d",
    help="交付日期（YYYY-M-D），默认今天",
)
@click.option(
    "--purchaser",
    default="梁程程妈妈",
    help="采购方",
)
@click.pass_context
def manual(ctx, title, date, purchaser):
    """
    手动创建收据

    TITLE: 主题标题
    """
    delivery_date = date.fromisoformat(date) if date else date.today()

    console.print(f"\n[bold cyan]手动创建收据: {title}[/bold cyan]\n")

    receipt = create_receipt(
        title=title,
        delivery_date=delivery_date,
        purchaser=purchaser,
    )

    # 添加商品
    while True:
        console.print("\n[bold]添加商品[/bold]")

        name = click.prompt("商品名称")
        quantity = click.prompt("数量", type=float)
        unit_price = click.prompt("单价", type=float)
        unit = click.prompt("单位", default="个")

        receipt.add_item(
            name=name,
            quantity=quantity,
            unit_price=unit_price,
            unit=unit,
        )

        console.print(f"[green]✓ 已添加: {name} x {quantity} {unit} @ ¥{unit_price:.2f}[/green]")

        if not click.confirm("\n继续添加商品？"):
            break

    # 显示摘要
    print_receipt_summary(receipt)

    # 确认保存
    if click.confirm("\n确认保存到Excel？"):
        excel_file = ctx.obj["excel_file"]
        handler = ExcelHandler(excel_file)
        handler.add_receipt(receipt)
        handler.close()

        console.print(f"\n[bold green]✓ 收据已保存到: {receipt.sheet_name}[/bold green]\n")


@cli.command("batch")
@click.argument("folder", type=click.Path(exists=True, file_okay=False, dir_okay=True))
@click.option(
    "--pattern", "-p",
    default="*",
    help="文件匹配模式，如 *.jpg",
)
@click.option(
    "--recursive", "-r",
    is_flag=True,
    help="递归处理子文件夹",
)
@click.option(
    "--no-ai",
    is_flag=True,
    help="跳过AI识别，手动输入",
)
@click.option(
    "--interactive", "-i",
    is_flag=True,
    help="交互模式，逐个确认每个收据",
)
@click.option(
    "--continue-on-error",
    is_flag=True,
    help="遇到错误时继续处理",
)
@click.pass_context
def batch(ctx, folder, pattern, recursive, no_ai, interactive, continue_on_error):
    """
    批量处理收据图片

    默认自动保存所有识别结果，AI识别失败的会创建占位收据待后续补全。
    使用 --interactive 进入交互模式逐个确认。

    示例:
        receipt-manager batch ./receipts
        receipt-manager batch ./receipts --pattern "*.jpg"
        receipt-manager batch ./receipts --recursive
        receipt-manager batch ./receipts --interactive
    """
    excel_file = ctx.obj["excel_file"]
    api_key = ctx.obj["api_key"]

    folder_path = Path(folder).expanduser()

    # 查找图片文件
    images = _find_images(folder_path, pattern, recursive)

    if not images:
        console.print(f"[yellow]在 {folder} 中未找到图片文件[/yellow]")
        sys.exit(0)

    console.print(f"\n[bold cyan]找到 {len(images)} 个图片文件[/bold cyan]\n")

    # 显示文件列表
    for i, img in enumerate(images, 1):
        console.print(f"  {i}. {img.name}")

    mode_text = "交互模式" if interactive else "自动模式（所有识别结果将直接保存）"
    console.print(f"\n[dim]处理模式: {mode_text}[/dim]")

    if not click.confirm("\n开始批量处理？"):
        console.print("[yellow]已取消[/yellow]")
        sys.exit(0)

    # 统计
    success_count = 0
    failed_count = 0
    needs_review_count = 0
    failed_files: List[str] = []

    # 批量处理
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        console=console,
    ) as progress:

        task = progress.add_task("[cyan]处理收据...", total=len(images))

        for image_path in images:
            progress.update(task, description=f"[cyan]处理: {image_path.name}")

            try:
                receipt = None
                confidence = 0.0
                status = ""  # 状态标识

                if no_ai:
                    # 手动输入模式
                    console.print(f"\n[bold cyan]处理: {image_path.name}[/bold cyan]")
                    receipt = _manual_input(str(image_path), None, None)
                    status = "手动输入"

                else:
                    # AI识别模式
                    receipt, confidence = recognize_receipt(
                        str(image_path),
                        api_key=api_key,
                    )

                    if receipt is None:
                        # AI识别失败，创建占位收据
                        console.print(f"[yellow]⚠ {image_path.name}: AI识别失败，创建占位收据[/yellow]")
                        receipt = _create_placeholder_receipt(image_path)
                        confidence = 0.0
                        status = "待补全"
                        needs_review_count += 1
                    elif confidence < 0.7:
                        status = "需核对"
                        needs_review_count += 1
                    else:
                        status = "已识别"

                # 显示识别结果摘要
                console.print(f"\n[bold cyan]处理: {image_path.name}[/bold cyan]")
                console.print(f"  主题: {receipt.title}")
                console.print(f"  日期: {receipt.delivery_date}")
                console.print(f"  商品数: {receipt.item_count}")
                console.print(f"  总金额: ¥{receipt.total_amount:.2f}")
                console.print(f"  置信度: {confidence:.2%}")
                console.print(f"  状态: {status}")

                # 交互模式确认
                if interactive:
                    if confidence < 0.8 and status != "待补全":
                        console.print("[yellow]  ⚠️  识别置信度较低，建议核对[/yellow]")

                    if not click.confirm("  确认保存？"):
                        console.print("[yellow]  已跳过[/yellow]")
                        progress.advance(task)
                        continue

                # 保存到Excel（批处理模式下跳过严格验证）
                handler = ExcelHandler(excel_file)
                handler.add_receipt(receipt)
                handler.close()

                console.print(f"[green]✓ {image_path.name}: 已保存[/green]")
                success_count += 1

            except Exception as e:
                console.print(f"[red]✗ {image_path.name}: {str(e)}[/red]")
                if continue_on_error:
                    failed_count += 1
                    failed_files.append(image_path.name)
                    progress.advance(task)
                    continue
                else:
                    sys.exit(1)

            progress.advance(task)

    # 显示汇总
    console.print("\n" + "=" * 50)
    console.print("[bold cyan]批量处理完成[/bold cyan]")
    console.print(f"  已保存: [green]{success_count}[/green]")
    if needs_review_count > 0:
        console.print(f"  需核对/补全: [yellow]{needs_review_count}[/yellow]")
    if failed_count > 0:
        console.print(f"  失败: [red]{failed_count}[/red]")

    if failed_files:
        console.print("\n[bold red]失败的文件:[/bold red]")
        for name in failed_files:
            console.print(f"  - {name}")

    if needs_review_count > 0:
        console.print("\n[yellow]提示: 请在Excel中核对/补全标记为「需核对」或「待补全」的收据[/yellow]")

    console.print(f"\n[bold green]Excel文件:[/bold green] {excel_file}\n")


def _create_placeholder_receipt(image_path: Path) -> PurchaseReceipt:
    """
    创建占位收据（AI识别失败时使用）

    Args:
        image_path: 图片路径

    Returns:
        占位收据
    """
    # 从文件名生成标题
    title = image_path.stem  # 去掉扩展名
    # 清理文件名中的常见前缀/后缀
    for prefix in ["IMG_", "DSC_", "PHOTO_", "微信图片_", "Screenshot_"]:
        if title.startswith(prefix):
            title = title[len(prefix):]
            break

    # 如果标题为空或只是数字，使用默认标题
    if not title or title.isdigit():
        title = f"收据_{image_path.stem}"

    # 创建收据，添加一个占位商品项
    receipt = create_receipt(
        title=title,
        delivery_date=date.today(),
        source_file=str(image_path),
    )
    receipt.recognition_method = "manual"
    receipt.confidence = 0.0

    # 添加占位商品项（标记为待补全）
    receipt.add_item(
        name="【待补全】请在Excel中填写实际商品信息",
        quantity=Decimal("1"),
        unit_price=Decimal("0"),
        unit="项",
        remark=f"原图片: {image_path.name}",
    )

    return receipt


def _find_images(folder: Path, pattern: str, recursive: bool) -> List[Path]:
    """
    查找文件夹中的图片文件

    Args:
        folder: 文件夹路径
        pattern: 文件匹配模式
        recursive: 是否递归查找

    Returns:
        图片文件路径列表
    """
    images = []

    if recursive:
        # 递归查找
        for ext in IMAGE_EXTENSIONS:
            images.extend(folder.rglob(f"*{ext}"))
            images.extend(folder.rglob(f"*{ext.upper()}"))
    else:
        # 仅当前文件夹
        for ext in IMAGE_EXTENSIONS:
            images.extend(folder.glob(f"*{ext}"))
            images.extend(folder.glob(f"*{ext.upper()}"))

    # 去重并排序
    images = sorted(set(images))

    # 如果有自定义模式，再过滤一次
    if pattern and pattern != "*":
        import fnmatch
        filtered = []
        for img in images:
            if fnmatch.fnmatch(img.name, pattern):
                filtered.append(img)
        images = filtered

    return images


def _manual_input(image_path: str, title_hint: Optional[str], date_hint: Optional[str]) -> PurchaseReceipt:
    """
    手动输入收据

    Args:
        image_path: 图片路径
        title_hint: 主题提示
        date_hint: 日期提示

    Returns:
        收据数据
    """
    console.print("\n[bold yellow]手动输入模式[/bold yellow]\n")

    # 输入标题
    title = title_hint or click.prompt("主题标题")

    # 输入日期
    if date_hint:
        delivery_date = date.fromisoformat(date_hint)
    else:
        date_str = click.prompt("交付日期", default=date.today().isoformat())
        delivery_date = date.fromisoformat(date_str)

    # 创建收据
    receipt = create_receipt(title=title, delivery_date=delivery_date)

    # 添加商品
    console.print("\n[bold]添加商品（输入空名称结束）[/bold]\n")

    sequence = 1
    while True:
        name = click.prompt(f"\n商品 {sequence} 名称", default="", show_default=False)

        if not name:
            break

        spec = click.prompt("  规格", default="")
        unit = click.prompt("  单位", default="个")
        quantity = click.prompt("  数量", type=float, default=1)
        unit_price = click.prompt("  单价", type=float, default=0)
        remark = click.prompt("  备注", default="")

        receipt.add_item(
            name=name,
            spec=spec if spec else None,
            unit=unit,
            quantity=quantity,
            unit_price=unit_price,
            remark=remark if remark else None,
        )

        console.print(f"[green]✓ 已添加[/green]")
        sequence += 1

    return receipt


def main():
    """主函数"""
    cli()  # type: ignore[call-arg]


if __name__ == "__main__":
    main()
