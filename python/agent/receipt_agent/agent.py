#!/usr/bin/env python3
"""
Receipt Manager Agent 入口文件
供 adk run 命令使用
"""

import os
import sys
from pathlib import Path
import litellm

from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm

# ============================================================================
# 关键路径设置 - 必须在任何导入之前完成
# ============================================================================

_agent_dir = Path(__file__).parent
_agent_parent = _agent_dir.parent

# 找到 receipt_manager 包的实际位置
_mcp_receipt_dir = _agent_dir.parent.parent / "mcp" / "receipt_manager"
_receipt_manager_pkg = _mcp_receipt_dir / "receipt_manager"

# 重新排序 sys.path：
# 1. 移除 agent 父目录（避免命名冲突）
# 2. 将 mcp/receipt_manager 添加到最前面
_agent_parent_str = str(_agent_parent.resolve())
_mcp_receipt_dir_str = str(_mcp_receipt_dir.resolve())

# 重建 sys.path
new_sys_path = []
for p in sys.path:
    p_resolved = str(Path(p).resolve())
    if p_resolved != _agent_parent_str:
        new_sys_path.append(p)

# 将 mcp/receipt_manager 放在最前面
new_sys_path.insert(0, _mcp_receipt_dir_str)
sys.path[:] = new_sys_path

# 预加载 receipt_manager 包到 sys.modules
# 临时清除当前模块的 __package__ 属性，避免影响导入
_current_module = sys.modules.get(__name__)
if _current_module and hasattr(_current_module, '__package__'):
    _old_package = _current_module.__package__
    _current_module.__package__ = None

import receipt_manager
import importlib
importlib.import_module("receipt_manager.ai_ocr")
importlib.import_module("receipt_manager.excel_handler")

# 恢复 __package__ 属性
if _current_module and '_old_package' in locals():
    _current_module.__package__ = _old_package

# 添加 tools 目录到路径
_tools_dir = _agent_dir / "tools"

# 使用 exec 直接加载工具模块，避免 import 机制的问题
def load_tool_module(module_name):
    """使用 exec 直接加载工具模块"""
    module_path = _tools_dir / f"{module_name}.py"
    if not module_path.exists():
        raise ImportError(f"Tool module not found: {module_path}")

    with open(module_path, 'r') as f:
        code = f.read()

    # 创建模块对象
    import types
    module = types.ModuleType(module_name)
    # 设置模块的 __file__ 和 __package__
    module.__file__ = str(module_path)
    module.__package__ = None  # 顶层模块
    # 将模块添加到 sys.modules
    sys.modules[module_name] = module
    # 执行模块代码
    exec(code, module.__dict__)
    return module

# 加载所有工具模块
ocr_tool = load_tool_module("ocr_tool")
excel_tool = load_tool_module("excel_tool")
query_tool = load_tool_module("query_tool")
stats_tool = load_tool_module("stats_tool")

# ============================================================================
# 配置
# ============================================================================

# 配置智谱 AI (Zhipu AI) OpenAI 兼容端点
os.environ["OPENAI_API_KEY"] = os.environ.get("ZHIPU_API_KEY", "")
litellm.api_base = "https://open.bigmodel.cn/api/paas/v4/"

# 从工具模块中提取函数
recognize_receipt = ocr_tool.recognize_receipt
batch_recognize = ocr_tool.batch_recognize
create_manual_receipt = ocr_tool.create_manual_receipt
recognize_and_save = ocr_tool.recognize_and_save

save_receipt_to_excel = excel_tool.save_receipt_to_excel
read_receipt_from_excel = excel_tool.read_receipt_from_excel
list_excel_sheets = excel_tool.list_excel_sheets
update_receipt_in_excel = excel_tool.update_receipt_in_excel
delete_receipt_from_excel = excel_tool.delete_receipt_from_excel
merge_excel_files = excel_tool.merge_excel_files
sort_sheets_by_date = excel_tool.sort_sheets_by_date
rename_sheet = excel_tool.rename_sheet
rename_sheet_auto = excel_tool.rename_sheet_auto
beautify_excel = excel_tool.beautify_excel

list_receipts = query_tool.list_receipts
search_receipts_by_keyword = query_tool.search_receipts_by_keyword
get_receipt_by_date = query_tool.get_receipt_by_date
get_receipt_summary = query_tool.get_receipt_summary

get_statistics = stats_tool.get_statistics
export_statistics_json = stats_tool.export_statistics_json
analyze_by_period = stats_tool.analyze_by_period
get_top_items = stats_tool.get_top_items
get_monthly_summary = stats_tool.get_monthly_summary

# ============================================================================
# Root Agent - adk run 会使用这个 root_agent 变量
# ============================================================================

root_agent = LlmAgent(
    model=LiteLlm(model="openai/glm-4.7"),
    name='receipt_manager_agent',
    description="""
    采购收据管理智能助手，帮助用户管理采购收据，支持 AI 识别、Excel 操作、查询统计等功能。

    主要功能：
    1. AI 识别 - 使用 AI 自动识别收据图片
    2. Excel 操作 - 保存、读取、更新、删除收据
    3. 收据查询 - 按条件查询和搜索收据
    4. 统计分析 - 获取统计信息和分析报告
    """,
    instruction="""
    你是一个采购收据管理智能助手，帮助用户管理采购收据。

    ## ⚠️ 重要：必须调用工具

    对于用户的每个请求，你必须调用相应的工具来获取实际数据，而不是只提供说明或建议。

    ## 工具选择规则

    ### 收据查询（最常用）
    用户想要查看收据时，使用以下工具：

    1. **list_receipts** - 列出所有收据或按条件筛选
       - 用户说: "列出所有收据"、"显示收据"、"查看收据"、"有什么收据"
       - 调用: `list_receipts()`

    2. **search_receipts_by_keyword** - 按关键词搜索
       - 用户说: "搜索XX"、"查找XX"、"关于XX的收据"
       - 调用: `search_receipts_by_keyword(keyword="关键词")`

    3. **list_excel_sheets** - 列出所有 Sheet
       - 用户说: "列出 Sheet"、"显示所有 Sheet"
       - 调用: `list_excel_sheets()`

    4. **get_receipt_by_date** - 查看指定日期的收据
       - 用户说: "查看某日的收据"、"XX日期的收据"
       - 调用: `get_receipt_by_date(target_date="2025-01-20")`

    ### 统计分析
    用户想要统计数据时：

    1. **get_statistics** - 获取总体统计
       - 用户说: "统计"、"汇总"、"总计"、"概况"
       - 调用: `get_statistics()`

    2. **get_monthly_summary** - 月度汇总
       - 用户说: "月度汇总"、"每月统计"、"XX年的汇总"
       - 调用: `get_monthly_summary(year=2025)`

    3. **get_top_items** - 商品排行榜
       - 用户说: "商品排行"、"购买最多"、"热门商品"
       - 调用: `get_top_items()`

    4. **analyze_by_period** - 按周期分析
       - 用户说: "按月分析"、"按周分析"、"周期统计"
       - 调用: `analyze_by_period(period="month")`

    ### AI 识别
    用户提到图片或收据照片时：

    1. **recognize_receipt** - 识别单张收据
       - 用户说: "识别这张收据"、"识别图片"
       - 调用: `recognize_receipt(image_path="图片路径")`

    2. **recognize_and_save** - 识别收据并保存到 Excel（包含原始图片）
       - 用户说: "识别并保存"、"录入收据"、"保存收据图片"
       - 调用: `recognize_and_save(image_path="图片路径")`

    3. **batch_recognize** - 批量识别
       - 用户说: "批量识别"、"识别文件夹"
       - 调用: `batch_recognize(folder_path="文件夹路径")`

    ### Excel 操作
    用户明确要操作 Excel 时：

    1. **merge_excel_files** - 合并多个 Excel 文件
       - 用户说: "合并Excel"、"合并文件"、"整合数据"
       - 调用: `merge_excel_files(source_paths=["文件1.xlsx", "文件2.xlsx"])`

    2. **sort_sheets_by_date** - 按 Sheet 日期排序
       - 用户说: "按日期排序"、"按时间排序"、"从新到旧排序"
       - 调用: `sort_sheets_by_date()` 或 `sort_sheets_by_date(order="asc")`

    3. **rename_sheet_auto** - 自动重命名 Sheet 为"主题（日期）"格式
       - 用户说: "重命名Sheet"、"修改Sheet名"、"把XX改为XX（日期）"
       - 调用: `rename_sheet_auto(old_name="旧名称", date_str="9-1")`

    4. **rename_sheet** - 自定义重命名 Sheet
       - 用户说: "重命名为XX"、"改名为XX"
       - 调用: `rename_sheet(old_name="旧名称", new_name="新名称")`

    5. **read_receipt_from_excel** - 读取指定收据
       - 调用: `read_receipt_from_excel(sheet_name="Sheet名称")`

    6. **delete_receipt_from_excel** - 删除收据
       - 调用: `delete_receipt_from_excel(sheet_name="Sheet名称")`

    7. **beautify_excel** - 美化 Excel（应用专业样式）
       - 用户说: "美化Excel"、"优化样式"、"格式化表格"
       - 调用: `beautify_excel()`

    ## 默认 Excel 文件

    默认 Excel 文件路径: ~/Documents/receipt-309/309-采购明细.xlsx
    （完整路径: /home/bughero/Documents/receipt-309/309-采购明细.xlsx）

    ## 回复风格

    - 使用清晰的中文回复
    - 重要信息使用表情符号突出显示
    - 必须调用工具获取实际数据
    - 金额显示时使用人民币符号 ¥
    """,
    tools=[
        # OCR 工具
        recognize_receipt,
        batch_recognize,
        create_manual_receipt,
        recognize_and_save,
        # Excel 工具
        save_receipt_to_excel,
        read_receipt_from_excel,
        list_excel_sheets,
        update_receipt_in_excel,
        delete_receipt_from_excel,
        merge_excel_files,
        sort_sheets_by_date,
        rename_sheet,
        rename_sheet_auto,
        beautify_excel,
        # 查询工具
        list_receipts,
        search_receipts_by_keyword,
        get_receipt_by_date,
        get_receipt_summary,
        # 统计工具
        get_statistics,
        export_statistics_json,
        analyze_by_period,
        get_top_items,
        get_monthly_summary,
    ],
)

__all__ = ['root_agent']
