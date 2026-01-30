#!/usr/bin/env python3
"""
Dashboard Explorer Agent Tool
智能 Dashboard 和 Panel 探索的 Agent Tool
"""

import asyncio
import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

import httpx
import nest_asyncio

# 允许嵌套事件循环 (ADK 运行在已有事件循环中)
nest_asyncio.apply()

# 导入 ES 查询工具
sys_path = str(Path(__file__).parent)
if sys_path not in sys.path:
    sys.path.insert(0, sys_path)

from es_query_tool import (
    query_elasticsearch,
    query_elasticsearch_aggregation,
    format_es_results,
    format_aggregation_results,
)


# ============================================================================
# 配置
# ============================================================================

DEFAULT_GRAFANA_URL = "https://g.dev.tuputech.com"
DEFAULT_API_KEY = os.getenv("GRAFANA_API_KEY", "")


def _run_async(coro):
    """运行异步代码 (nest_asyncio 已启用)"""
    try:
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(coro)
    except RuntimeError:
        return asyncio.run(coro)


# ============================================================================
# Agent Tool Functions
# ============================================================================

def list_dashboards(
    folder: str = None,
    tag: str = None,
    search: str = None,
    limit: int = 50,
) -> str:
    """
    列出 Grafana 仪表板

    Args:
        folder: 按文件夹过滤 (如 'ipc', 'Production')
        tag: 按标签过滤 (如 'API', 'monitoring')
        search: 搜索关键词
        limit: 最大返回数量

    Returns:
        仪表板列表
    """
    async def _query() -> list:
        grafana_url = os.getenv("GRAFANA_URL", DEFAULT_GRAFANA_URL)
        api_key = os.getenv("GRAFANA_API_KEY", DEFAULT_API_KEY)

        url = f"{grafana_url}/api/search"
        headers = {"Content-Type": "application/json"}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"

        params = {"type": "dash-db", "limit": limit}
        if search:
            params["query"] = search
        if tag:
            params["tag"] = tag

        async with httpx.AsyncClient(headers=headers, timeout=30.0) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            return response.json()

    # 执行异步查询
    dashboards = _run_async(_query())

    # 格式化结果
    if not dashboards:
        return f"📋 未找到仪表板 (过滤: folder={folder}, tag={tag}, search={search})"

    lines = [f"📋 Grafana 仪表板 ({len(dashboards)} 个)", f"{'='*60}"]

    for dash in dashboards[:50]:
        title = dash.get("title", "Untitled")
        uid = dash.get("uid", "N/A")
        folder_title = dash.get("folderTitle", "General")
        tags = dash.get("tags", [])
        dash_url = f"{os.getenv('GRAFANA_URL', DEFAULT_GRAFANA_URL)}{dash.get('url', '')}"

        lines.append(f"\n📊 {title}")
        lines.append(f"   UID: {uid}")
        lines.append(f"   文件夹: {folder_title}")
        if tags:
            lines.append(f"   标签: {', '.join(tags)}")
        lines.append(f"   URL: {dash_url}")

    return "\n".join(lines)


def get_dashboard_panels(
    dashboard_uid: str,
) -> str:
    """
    获取仪表板的所有面板

    Args:
        dashboard_uid: 仪表板 UID

    Returns:
        面板列表
    """
    async def _query() -> dict:
        grafana_url = os.getenv("GRAFANA_URL", DEFAULT_GRAFANA_URL)
        api_key = os.getenv("GRAFANA_API_KEY", DEFAULT_API_KEY)

        url = f"{grafana_url}/api/dashboards/uid/{dashboard_uid}"
        headers = {"Content-Type": "application/json"}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"

        async with httpx.AsyncClient(headers=headers, timeout=30.0) as client:
            response = await client.get(url)
            response.raise_for_status()
            return response.json()

    # 执行异步查询
    data = _run_async(_query())
    dashboard = data.get("dashboard", {})
    panels = dashboard.get("panels", [])

    if not panels:
        return f"📊 仪表板 {dashboard_uid} 没有面板"

    lines = [
        f"📊 仪表板面板列表",
        f"{'='*60}",
        f"  仪表板: {dashboard.get('title', 'Untitled')}",
        f"  UID: {dashboard_uid}",
        f"  面板数: {len(panels)}",
        f"{'='*60}",
    ]

    # 按面板类型分组统计
    type_counts = {}
    for panel in panels:
        ptype = panel.get("type", "unknown")
        type_counts[ptype] = type_counts.get(ptype, 0) + 1

    lines.append(f"\n📈 面板类型统计:")
    for ptype, count in sorted(type_counts.items()):
        lines.append(f"  {ptype}: {count} 个")

    lines.append(f"\n📋 面板详情:")
    for panel in panels:
        pid = panel.get("id")
        title = panel.get("title", "Untitled")
        ptype = panel.get("type", "unknown")
        datasource = panel.get("datasource", {}).get("type", "N/A")

        lines.append(f"  [{pid}] {title} ({ptype}) - 数据源: {datasource}")

    return "\n".join(lines)


def search_panels(
    keyword: str,
    folder: str = None,
) -> str:
    """
    搜索包含关键词的面板

    Args:
        keyword: 搜索关键词
        folder: 可选的文件夹过滤

    Returns:
        匹配的面板列表
    """
    # 简化实现 - 返回搜索提示
    return f"🔍 搜索面板: 关键词 '{keyword}'\n\n💡 提示: 使用 list_dashboards 查看所有仪表板，然后手动查找包含 '{keyword}' 的面板"


def get_panel_info(
    dashboard_uid: str,
    panel_id: int,
) -> str:
    """
    获取面板详细信息

    Args:
        dashboard_uid: 仪表板 UID
        panel_id: 面板 ID

    Returns:
        面板详细信息
    """
    async def _query() -> Any:
        grafana_url = os.getenv("GRAFANA_URL", DEFAULT_GRAFANA_URL)
        api_key = os.getenv("GRAFANA_API_KEY", DEFAULT_API_KEY)

        url = f"{grafana_url}/api/dashboards/uid/{dashboard_uid}"
        headers = {"Content-Type": "application/json"}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"

        async with httpx.AsyncClient(headers=headers, timeout=30.0) as client:
            response = await client.get(url)
            response.raise_for_status()
            data = response.json()
            panels = data.get("dashboard", {}).get("panels", [])

            for panel in panels:
                if panel.get("id") == panel_id:
                    return panel

        return None

    # 执行异步查询
    panel = _run_async(_query())

    if not panel:
        return f"❌ 未找到面板 ID {panel_id}"

    lines = [
        f"📊 面板详细信息",
        f"{'='*60}",
        f"  标题: {panel.get('title', 'Untitled')}",
        f"  ID: {panel.get('id')}",
        f"  类型: {panel.get('type', 'unknown')}",
        f"  描述: {panel.get('description', 'N/A')}",
        f"{'='*60}",
        f"\n📌 数据源:",
        f"  类型: {panel.get('datasource', {}).get('type', 'N/A')}",
        f"  UID: {panel.get('datasource', {}).get('uid', 'N/A')}",
    ]

    # 查询目标
    targets = panel.get("targets", [])
    if targets:
        lines.append(f"\n🎯 查询目标 ({len(targets)} 个):")
        for i, target in enumerate(targets[:3]):
            lines.append(f"  [{i+1}] {json.dumps(target, ensure_ascii=False)[:200]}")

    return "\n".join(lines)


def get_dashboard_recommendations(
    platform: str = "sdc",
) -> str:
    """
    获取平台相关的仪表板推荐

    Args:
        platform: 平台名称

    Returns:
        推荐的仪表板列表
    """
    recommendations = {
        "sdc": [
            ("SDC 设备监控", "urJcwIvHz", "设备健康状态、崩溃统计"),
            ("SDC 网络监控", "abc123", "网络连接状态、延迟统计"),
        ],
        "ipc": [
            ("IPC 服务监控", "def456", "服务可用性、响应时间"),
        ],
    }

    platform_recs = recommendations.get(platform.lower(), [])

    lines = [
        f"💡 仪表板推荐",
        f"{'='*60}",
        f"  平台: {platform}",
        f"{'='*60}",
    ]

    if not platform_recs:
        lines.append(f"\n⚠️ 暂无 {platform} 平台的推荐仪表板")
    else:
        lines.append(f"\n推荐仪表板:")
        for title, uid, desc in platform_recs:
            lines.append(f"\n📊 {title}")
            lines.append(f"   UID: {uid}")
            lines.append(f"   说明: {desc}")

    lines.append(f"\n💡 提示: 使用 list_dashboards(folder='{platform}') 查看更多")

    return "\n".join(lines)


# 导出所有工具函数
__all__ = [
    "list_dashboards",
    "get_dashboard_panels",
    "search_panels",
    "get_panel_info",
    "get_panel_query_results",  # 执行 panel 查询并返回实际数据
    "download_panel_render",    # 下载 panel 渲染图片
    "get_panel_render_url",     # 生成 panel 直接链接（替代方案）
    "send_panel_to_email",      # 将 panel 图片发送到邮件
    "get_dashboard_recommendations",
]


# ============================================================================
# Panel Render Download - 下载 Panel 渲染图片
# ============================================================================

def _get_render_url(
    dashboard_uid: str,
    panel_id: int,
    dashboard_slug: str = None,
    time_from: str = "now-6h",
    time_to: str = "now",
    width: int = 1000,
    height: int = 500,
) -> str:
    """
    生成 Grafana Panel 渲染 URL (需要 Image Renderer 插件)

    Args:
        dashboard_uid: 仪表板 UID
        panel_id: 面板 ID
        dashboard_slug: 仪表板 slug（可选，默认使用 dashboard_uid）
        time_from: 开始时间
        time_to: 结束时间
        width: 图片宽度
        height: 图片高度

    Returns:
        渲染 URL
    """
    grafana_url = os.getenv("GRAFANA_URL", DEFAULT_GRAFANA_URL)
    slug = dashboard_slug or dashboard_uid

    # d-solo 表示只渲染单个 panel
    return (
        f"{grafana_url}/render/d-solo/{dashboard_uid}/{slug}"
        f"?panelId={panel_id}"
        f"&from={time_from}"
        f"&to={time_to}"
        f"&width={width}"
        f"&height={height}"
    )


def _get_direct_url(
    dashboard_uid: str,
    panel_id: int,
    dashboard_slug: str = None,
    time_from: str = "now-6h",
    time_to: str = "now",
    org_id: int = 1,
) -> str:
    """
    生成 Grafana Panel 直接访问 URL (不需要 Image Renderer 插件)

    Args:
        dashboard_uid: 仪表板 UID
        panel_id: 面板 ID
        dashboard_slug: 仪表板 slug（可选，默认使用 dashboard_uid）
        time_from: 开始时间
        time_to: 结束时间
        org_id: 组织 ID

    Returns:
        直接访问 URL
    """
    grafana_url = os.getenv("GRAFANA_URL", DEFAULT_GRAFANA_URL)
    slug = dashboard_slug or dashboard_uid

    # 直接访问 dashboard 的特定 panel
    return (
        f"{grafana_url}/d/{dashboard_uid}/{slug}"
        f"?orgId={org_id}"
        f"&viewPanel={panel_id}"
        f"&from={time_from}"
        f"&to={time_to}"
    )


def download_panel_render(
    dashboard_uid: str,
    panel_id: int,
    output_path: str = None,
    time_range: str = "6h",
    width: int = 1000,
    height: int = 500,
) -> str:
    """
    下载 Panel 的渲染图片到本地

    注意：需要 Grafana Image Renderer 插件已安装并可用。
    如果下载失败（插件不可用），会自动返回直接访问链接作为备用方案。

    Args:
        dashboard_uid: 仪表板 UID (如 'urJcwIvHz')
        panel_id: 面板 ID (数字，如 2)
        output_path: 输出文件路径 (可选，默认自动生成)
        time_range: 时间范围 (如 '1h', '6h', '24h', 'today')
        width: 图片宽度 (像素)
        height: 图片高度 (像素)

    Returns:
        保存的文件路径，或直接访问链接（render 不可用时）

    示例:
        download_panel_render(dashboard_uid='urJcwIvHz', panel_id=2)
        download_panel_render(
            dashboard_uid='urJcwIvHz',
            panel_id=2,
            output_path='./panel_screenshot.png',
            time_range='24h'
        )
    """
    async def _download():
        grafana_url = os.getenv("GRAFANA_URL", DEFAULT_GRAFANA_URL)
        api_key = os.getenv("GRAFANA_API_KEY", DEFAULT_API_KEY)

        # 解析时间范围
        if time_range == "today":
            time_from = "now/d"
        else:
            time_from = f"now-{time_range}"

        # 生成渲染 URL
        render_url = _get_render_url(
            dashboard_uid=dashboard_uid,
            panel_id=panel_id,
            time_from=time_from,
            time_to="now",
            width=width,
            height=height,
        )

        # 设置请求头
        headers = {}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"

        # 下载图片
        async with httpx.AsyncClient(headers=headers, timeout=60.0) as client:
            response = await client.get(render_url)

            # 检查是否是 Image Renderer 不可用的错误
            # Grafana 返回 HTML 页面或特定错误信息
            content_type = response.headers.get("content-type", "")

            if "text/html" in content_type or response.status_code != 200:
                # Render 插件不可用，返回 None 表示需要回退
                return None, None

            response.raise_for_status()

            # 生成保存路径
            save_path = output_path
            if save_path is None:
                output_dir = Path.cwd() / "panel_renders"
                output_dir.mkdir(exist_ok=True)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                save_path = str(output_dir / f"panel_{dashboard_uid}_{panel_id}_{timestamp}.png")
            else:
                save_path = str(Path(output_path))
                Path(save_path).parent.mkdir(parents=True, exist_ok=True)

            # 保存图片
            with open(save_path, "wb") as f:
                f.write(response.content)

            return save_path, render_url

    # 执行异步下载
    try:
        result = _run_async(_download())
        file_path, url = result

        if file_path is None:
            # Render 插件不可用，自动回退到直接链接
            fallback_url = get_panel_render_url(
                dashboard_uid=dashboard_uid,
                panel_id=panel_id,
                time_range=time_range,
            )
            return f"{fallback_url}\n\n⚠️ 注意: Grafana Image Renderer 插件不可用，已提供直接访问链接作为备用方案。"

        lines = [
            f"📸 Panel 渲染图片已下载",
            f"{'='*60}",
            f"  Dashboard UID: {dashboard_uid}",
            f"  Panel ID: {panel_id}",
            f"  时间范围: {time_range}",
            f"  尺寸: {width}x{height}",
            f"{'='*60}",
            f"  保存路径: {file_path}",
        ]

        return "\n".join(lines)

    except Exception as e:
        # 出错时也回退到直接链接
        return f"{get_panel_render_url(dashboard_uid, panel_id, time_range)}\n\n⚠️ 下载失败 ({str(e)})，已提供直接访问链接作为备用方案。"


def get_panel_render_url(
    dashboard_uid: str,
    panel_id: int,
    dashboard_slug: str = None,
    time_range: str = "6h",
    org_id: int = 1,
) -> str:
    """
    生成 Panel 的直接访问 URL（替代截图功能）

    当 Grafana Image Renderer 插件不可用时，使用此工具获取直接链接。

    Args:
        dashboard_uid: 仪表板 UID (如 'urJcwIvHz')
        panel_id: 面板 ID (数字，如 13)
        dashboard_slug: 仪表板 slug (可选，用于美化 URL)
        time_range: 时间范围 (如 '1h', '6h', '24h', 'today')
        org_id: 组织 ID (默认 1)

    Returns:
        直接访问 URL

    示例:
        get_panel_render_url(dashboard_uid='urJcwIvHz', panel_id=13, time_range='today')
        # 返回: https://g.dev.tuputech.com/d/urJcwIvHz/slug?orgId=1&viewPanel=13&from=now%2Fd&to=now
    """
    # 解析时间范围
    if time_range == "today":
        time_from = "now/d"
        time_to = "now"
    else:
        time_from = f"now-{time_range}"
        time_to = "now"

    # 生成直接访问 URL
    direct_url = _get_direct_url(
        dashboard_uid=dashboard_uid,
        panel_id=panel_id,
        dashboard_slug=dashboard_slug,
        time_from=time_from,
        time_to=time_to,
        org_id=org_id,
    )

    lines = [
        f"🔗 Panel 直接访问链接",
        f"{'='*60}",
        f"  Dashboard UID: {dashboard_uid}",
        f"  Panel ID: {panel_id}",
        f"  时间范围: {time_range}",
        f"{'='*60}",
        f"",
        f"  📎 点击访问:",
        f"  {direct_url}",
        f"",
        f"  💡 提示: 此链接会直接打开 Grafana 并显示指定的 Panel",
    ]

    return "\n".join(lines)


def send_panel_to_email(
    dashboard_uid: str,
    panel_id: int,
    recipients: str = None,
    time_range: str = "6h",
    subject: str = None,
    width: int = 1000,
    height: int = 500,
) -> str:
    """
    将 Panel 渲染图片发送到邮件

    注意：需要 Grafana Image Renderer 插件已安装并可用。
    如果 render 不可用，会发送包含直接访问链接的邮件作为备用方案。

    Args:
        dashboard_uid: 仪表板 UID (如 'urJcwIvHz')
        panel_id: 面板 ID (数字，如 2)
        recipients: 收件人邮箱，逗号分隔 (如 'user@example.com' 或 'a@x.com,b@x.com')
        time_range: 时间范围 (如 '1h', '6h', '24h', 'today')
        subject: 邮件主题 (可选，默认自动生成)
        width: 图片宽度 (像素)
        height: 图片高度 (像素)

    Returns:
        发送结果

    示例:
        send_panel_to_email(
            dashboard_uid='urJcwIvHz',
            panel_id=2,
            recipients='user@example.com',
            time_range='24h'
        )
    """
    async def _download_and_send():
        # 1. 尝试下载图片
        grafana_url = os.getenv("GRAFANA_URL", DEFAULT_GRAFANA_URL)
        api_key = os.getenv("GRAFANA_API_KEY", DEFAULT_API_KEY)

        # 解析时间范围
        if time_range == "today":
            time_from = "now/d"
        else:
            time_from = f"now-{time_range}"

        # 生成渲染 URL
        render_url = _get_render_url(
            dashboard_uid=dashboard_uid,
            panel_id=panel_id,
            time_from=time_from,
            time_to="now",
            width=width,
            height=height,
        )

        # 设置请求头
        headers = {}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"

        # 尝试下载图片
        image_data = None
        render_available = True

        try:
            async with httpx.AsyncClient(headers=headers, timeout=60.0) as client:
                response = await client.get(render_url)
                content_type = response.headers.get("content-type", "")

                # 检查 render 是否可用
                if "text/html" in content_type or response.status_code != 200:
                    render_available = False
                else:
                    response.raise_for_status()
                    image_data = response.content
        except Exception:
            render_available = False

        # 2. 准备发送邮件
        # 导入邮件通知模块
        script_dir = Path(__file__).parent.parent.parent.parent / "mcp" / "grafana" / "monitoring" / "scripts"
        if script_dir not in sys.path:
            sys.path.insert(0, str(script_dir))

        try:
            from email_notifier import EmailNotifier, EmailConfig
        except ImportError:
            return {
                "success": False,
                "error": "邮件通知模块不可用，请确保 email_notifier.py 存在"
            }

        # 加载邮件配置 - 尝试多个可能的路径
        config = None
        config_path_used = None
        possible_paths = [
            # Agent 目录下的配置
            Path(__file__).parent.parent / "monitoring" / "config" / "email.yaml",
            # MCP grafana 目录下的配置
            Path(__file__).parent.parent.parent.parent / "mcp" / "grafana" / "monitoring" / "config" / "email.yaml",
            # 默认路径
            "monitoring/config/email.yaml",
        ]

        for config_path in possible_paths:
            try:
                if isinstance(config_path, Path):
                    if config_path.exists():
                        config = EmailConfig.from_yaml(str(config_path))
                        config_path_used = str(config_path)
                        break
                else:
                    config = EmailConfig.from_yaml(config_path)
                    config_path_used = config_path
                    break
            except Exception:
                continue

        if config is None:
            return {
                "success": False,
                "error": "无法加载邮件配置：未找到 email.yaml 配置文件。请确保配置文件存在于以下位置之一：\n"
                        f"1. {possible_paths[0]}\n"
                        f"2. {possible_paths[1]}"
            }

        # 获取 panel 信息用于生成主题
        panel_info_url = f"{grafana_url}/api/dashboards/uid/{dashboard_uid}"
        panel_title = f"Panel {panel_id}"

        try:
            async with httpx.AsyncClient(headers={"Authorization": f"Bearer {api_key}"}, timeout=30.0) as client:
                response = await client.get(panel_info_url)
                if response.status_code == 200:
                    data = response.json()
                    for panel in data.get("dashboard", {}).get("panels", []):
                        if panel.get("id") == panel_id:
                            panel_title = panel.get("title", f"Panel {panel_id}")
                            break
        except Exception:
            pass  # 使用默认标题

        # 生成邮件主题
        email_subject = subject if subject is not None else f"📊 Grafana Panel Report - {panel_title}"

        # 生成直接访问链接
        direct_url = _get_direct_url(
            dashboard_uid=dashboard_uid,
            panel_id=panel_id,
            time_from=time_from,
            time_to="now",
        )

        # 3. 构建邮件内容
        if render_available and image_data:
            # 方案 A: render 可用，发送带图片的邮件
            import base64
            image_b64 = base64.b64encode(image_data).decode('utf-8')

            body = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; }}
        .container {{ max-width: 800px; margin: 0 auto; }}
        .header {{ background-color: #f8f9fa; padding: 20px; }}
        .content {{ padding: 20px; }}
        .image-container {{ text-align: center; margin: 20px 0; }}
        .image-container img {{ max-width: 100%; border: 1px solid #ddd; }}
        .footer {{ color: #666; font-size: 0.9em; margin-top: 20px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h2>📊 Grafana Panel Report</h2>
            <p><strong>Panel:</strong> {panel_title}</p>
            <p><strong>Time Range:</strong> {time_range}</p>
        </div>
        <div class="content">
            <div class="image-container">
                <img src="data:image/png;base64,{image_b64}" alt="Panel Screenshot">
            </div>
        </div>
        <div class="footer">
            <p>This is an automated message from Grafana Monitoring Agent.</p>
            <p>Dashboard: {grafana_url}/d/{dashboard_uid}</p>
        </div>
    </div>
</body>
</html>
"""
        else:
            # 方案 B: render 不可用，发送带链接的邮件
            body = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; }}
        .container {{ max-width: 800px; margin: 0 auto; }}
        .header {{ background-color: #fff3cd; padding: 20px; border-left: 4px solid #ffc107; }}
        .content {{ padding: 20px; }}
        .link-button {{ display: inline-block; padding: 12px 24px; background-color: #007bff; color: white; text-decoration: none; border-radius: 4px; margin: 10px 0; }}
        .link-button:hover {{ background-color: #0056b3; }}
        .footer {{ color: #666; font-size: 0.9em; margin-top: 20px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h2>📊 Grafana Panel Report</h2>
            <p><strong>Panel:</strong> {panel_title}</p>
            <p><strong>Time Range:</strong> {time_range}</p>
            <p style="color: #856404;">⚠️ Image Renderer 插件不可用，请点击下方链接查看 Panel</p>
        </div>
        <div class="content">
            <p style="font-size: 16px;">点击下方按钮查看实时数据：</p>
            <a href="{direct_url}" class="link-button">🔗 打开 Panel</a>
            <p style="margin-top: 20px; color: #666;">或者复制以下链接到浏览器：</p>
            <p style="background-color: #f8f9fa; padding: 10px; border-radius: 4px; word-break: break-all;">{direct_url}</p>
        </div>
        <div class="footer">
            <p>This is an automated message from Grafana Monitoring Agent.</p>
        </div>
    </div>
</body>
</html>
"""

        # 发送邮件
        notifier = EmailNotifier(config)

        # 如果指定了收件人，临时覆盖配置
        original_recipients = None
        if recipients:
            from email_notifier import RecipientsConfig
            recipient_list = [r.strip() for r in recipients.split(',')]
            original_recipients = config.recipients
            config.recipients = RecipientsConfig(to=recipient_list, cc=[], bcc=[])

        success = notifier.send(email_subject, body, severity="info", html=True)

        # 恢复原始收件人配置
        if recipients:
            config.recipients = original_recipients

        return {
            "success": success,
            "panel_title": panel_title,
            "render_available": render_available,
        }

    # 执行异步操作
    try:
        result = _run_async(_download_and_send())

        if result.get("success"):
            render_available = result.get("render_available", True)
            status_icon = "📸" if render_available else "🔗"

            lines = [
                f"{status_icon} Panel 邮件已发送",
                f"{'='*60}",
                f"  Dashboard UID: {dashboard_uid}",
                f"  Panel: {result.get('panel_title', f'#{panel_id}')}",
                f"  时间范围: {time_range}",
                f"{'='*60}",
                f"  ✅ 邮件发送成功！",
            ]

            if not render_available:
                lines.append(f"  💡 发送模式: 直接链接（Image Renderer 不可用）")

            if recipients:
                lines.append(f"  收件人: {recipients}")

            return "\n".join(lines)
        else:
            return f"❌ 发送失败: {result.get('error', 'Unknown error')}"

    except Exception as e:
        return f"❌ 发送失败: {str(e)}"
    """
    将 Panel 渲染图片发送到邮件

    此工具会：
    1. 下载 Panel 的渲染图片
    2. 将图片作为附件发送到指定邮箱

    Args:
        dashboard_uid: 仪表板 UID (如 'urJcwIvHz')
        panel_id: 面板 ID (数字，如 2)
        recipients: 收件人邮箱，逗号分隔 (如 'user@example.com' 或 'a@x.com,b@x.com')
        time_range: 时间范围 (如 '1h', '6h', '24h', 'today')
        subject: 邮件主题 (可选，默认自动生成)
        width: 图片宽度 (像素)
        height: 图片高度 (像素)

    Returns:
        发送结果

    示例:
        send_panel_to_email(
            dashboard_uid='urJcwIvHz',
            panel_id=2,
            recipients='user@example.com',
            time_range='24h'
        )
    """
    async def _download_and_send():
        # 1. 下载图片
        grafana_url = os.getenv("GRAFANA_URL", DEFAULT_GRAFANA_URL)
        api_key = os.getenv("GRAFANA_API_KEY", DEFAULT_API_KEY)

        # 解析时间范围
        if time_range == "today":
            time_from = "now/d"
        else:
            time_from = f"now-{time_range}"

        # 生成渲染 URL
        render_url = _get_render_url(
            dashboard_uid=dashboard_uid,
            panel_id=panel_id,
            time_from=time_from,
            time_to="now",
            width=width,
            height=height,
        )

        # 设置请求头
        headers = {}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"

        # 下载图片
        async with httpx.AsyncClient(headers=headers, timeout=60.0) as client:
            response = await client.get(render_url)
            response.raise_for_status()
            image_data = response.content

        # 2. 发送邮件
        # 导入邮件通知模块
        script_dir = Path(__file__).parent.parent.parent.parent / "mcp" / "grafana" / "monitoring" / "scripts"
        if script_dir not in sys.path:
            sys.path.insert(0, str(script_dir))

        try:
            from email_notifier import EmailNotifier, EmailConfig
        except ImportError:
            return {
                "success": False,
                "error": "邮件通知模块不可用，请确保 email_notifier.py 存在"
            }

        # 加载邮件配置
        try:
            config = EmailConfig.from_yaml()
        except Exception as e:
            return {
                "success": False,
                "error": f"无法加载邮件配置: {str(e)}"
            }

        # 获取 panel 信息用于生成主题
        panel_info_url = f"{grafana_url}/api/dashboards/uid/{dashboard_uid}"
        panel_title = f"Panel {panel_id}"

        try:
            async with httpx.AsyncClient(headers={"Authorization": f"Bearer {api_key}"}, timeout=30.0) as client:
                response = await client.get(panel_info_url)
                if response.status_code == 200:
                    data = response.json()
                    for panel in data.get("dashboard", {}).get("panels", []):
                        if panel.get("id") == panel_id:
                            panel_title = panel.get("title", f"Panel {panel_id}")
                            break
        except Exception:
            pass  # 使用默认标题

        # 生成邮件主题
        if subject is None:
            subject = f"📊 Grafana Panel Report - {panel_title}"

        # 构建带图片的 HTML 邮件
        # 将图片转换为 base64 嵌入邮件
        import base64
        image_b64 = base64.b64encode(image_data).decode('utf-8')

        body = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; }}
        .container {{ max-width: 800px; margin: 0 auto; }}
        .header {{ background-color: #f8f9fa; padding: 20px; }}
        .content {{ padding: 20px; }}
        .image-container {{ text-align: center; margin: 20px 0; }}
        .image-container img {{ max-width: 100%; border: 1px solid #ddd; }}
        .footer {{ color: #666; font-size: 0.9em; margin-top: 20px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h2>📊 Grafana Panel Report</h2>
            <p><strong>Panel:</strong> {panel_title}</p>
            <p><strong>Time Range:</strong> {time_range}</p>
        </div>
        <div class="content">
            <div class="image-container">
                <img src="data:image/png;base64,{image_b64}" alt="Panel Screenshot">
            </div>
        </div>
        <div class="footer">
            <p>This is an automated message from Grafana Monitoring Agent.</p>
            <p>Dashboard: {grafana_url}/d/{dashboard_uid}</p>
        </div>
    </div>
</body>
</html>
"""

        # 发送邮件
        notifier = EmailNotifier(config)

        # 如果指定了收件人，临时覆盖配置
        if recipients:
            import re
            from email_notifier import RecipientsConfig
            recipient_list = [r.strip() for r in recipients.split(',')]
            # 临时创建收件人配置
            original_recipients = config.recipients
            config.recipients = RecipientsConfig(to=recipient_list, cc=[], bcc=[])

        success = notifier.send(subject, body, severity="info", html=True)

        # 恢复原始收件人配置
        if recipients:
            config.recipients = original_recipients

        return {
            "success": success,
            "panel_title": panel_title,
        }

    # 执行异步操作
    try:
        result = _run_async(_download_and_send())

        if result.get("success"):
            lines = [
                f"📧 Panel 邮件已发送",
                f"{'='*60}",
                f"  Dashboard UID: {dashboard_uid}",
                f"  Panel: {result.get('panel_title', f'#{panel_id}')}",
                f"  时间范围: {time_range}",
                f"{'='*60}",
                f"  ✅ 邮件发送成功！",
            ]

            if recipients:
                lines.append(f"  收件人: {recipients}")

            return "\n".join(lines)
        else:
            return f"❌ 发送失败: {result.get('error', 'Unknown error')}"

    except Exception as e:
        return f"❌ 发送失败: {str(e)}"


# ============================================================================
# Panel Query Execution - 执行 Panel 查询并返回实际数据
# ============================================================================

async def _execute_elasticsearch_target(
    target: Dict[str, Any],
    time_from: str = "now-6h",
    time_to: str = "now",
) -> Dict[str, Any]:
    """
    执行 Elasticsearch 数据源的查询目标

    Args:
        target: Grafana panel target 配置
        time_from: 开始时间
        time_to: 结束时间

    Returns:
        ES 查询结果
    """
    # 提取查询参数
    query = target.get("query", "")
    metrics = target.get("metrics", [])
    bucketAggs = target.get("bucketAggs", [])
    metricAggs = target.get("metricAggs", [])

    # 如果有 metrics 定义，构建聚合查询
    if metrics or bucketAggs or metricAggs:
        # 构建聚合查询 DSL
        es_query = {
            "size": 0,
            "query": {
                "bool": {
                    "must": [
                        {"query_string": {"query": query}},
                        {"range": {"@timestamp": {"gte": time_from, "lte": time_to}}},
                    ]
                }
            },
            "aggs": {},
        }

        # 添加 bucket aggregations
        for agg in bucketAggs:
            field = agg.get("field", "")
            agg_type = agg.get("type", "terms")

            if agg_type == "terms":
                es_query["aggs"]["buckets"] = {
                    "terms": {
                        "field": field,
                        "size": agg.get("size", 100),
                    }
                }

        # 添加 metric aggregations
        for agg in metricAggs:
            field = agg.get("field", "")
            agg_type = agg.get("type", "count")

            if "buckets" in es_query["aggs"]:
                if agg_type == "count":
                    es_query["aggs"]["buckets"]["aggs"] = {"metric": {"value_count": {"field": field}}}
                elif agg_type == "avg":
                    es_query["aggs"]["buckets"]["aggs"] = {"metric": {"avg": {"field": field}}}
                elif agg_type == "max":
                    es_query["aggs"]["buckets"]["aggs"] = {"metric": {"max": {"field": field}}}
                elif agg_type == "min":
                    es_query["aggs"]["buckets"]["aggs"] = {"metric": {"min": {"field": field}}}
                elif agg_type == "sum":
                    es_query["aggs"]["buckets"]["aggs"] = {"metric": {"sum": {"field": field}}}
            else:
                if agg_type == "count":
                    es_query["aggs"]["metric"] = {"value_count": {"field": field}}
                elif agg_type == "avg":
                    es_query["aggs"]["metric"] = {"avg": {"field": field}}
                elif agg_type == "max":
                    es_query["aggs"]["metric"] = {"max": {"field": field}}
                elif agg_type == "min":
                    es_query["aggs"]["metric"] = {"min": {"field": field}}
                elif agg_type == "sum":
                    es_query["aggs"]["metric"] = {"sum": {"field": field}}

        # 执行查询
        from es_query_tool import ES_URL, DEFAULT_INDEX
        url = f"{ES_URL}/{DEFAULT_INDEX}/_search"

        async with httpx.AsyncClient(timeout=60.0) as client:
            try:
                response = await client.post(url, json=es_query)
                response.raise_for_status()
                return {"success": True, "data": response.json()}
            except httpx.HTTPError as e:
                return {"success": False, "error": str(e)}

    # 如果没有聚合，执行普通查询
    else:
        result = await query_elasticsearch(
            query_string=query,
            time_from=time_from,
            time_to=time_to,
            size=100,
        )
        return {"success": True, "data": result}


async def _execute_prometheus_target(
    target: Dict[str, Any],
    time_from: str = "now-6h",
    time_to: str = "now",
) -> Dict[str, Any]:
    """
    执行 Prometheus 数据源的查询目标

    Args:
        target: Grafana panel target 配置
        time_from: 开始时间
        time_to: 结束时间

    Returns:
        Prometheus 查询结果
    """
    # Prometheus 查询实现（需要配置 Prometheus URL）
    expr = target.get("expr", "")

    # TODO: 实现 Prometheus 查询
    return {
        "success": False,
        "error": "Prometheus 查询暂未实现，请配置 Prometheus URL"
    }


def get_panel_query_results(
    dashboard_uid: str,
    panel_id: int,
    time_range: str = "6h",
) -> str:
    """
    执行 Panel 的查询并返回实际数据

    此工具会：
    1. 获取 Panel 的配置（包括数据源和查询目标）
    2. 解析查询配置
    3. 执行实际的数据查询
    4. 返回格式化的查询结果

    Args:
        dashboard_uid: 仪表板 UID (如 'urJcwIvHz')
        panel_id: 面板 ID (数字，如 2)
        time_range: 时间范围 (如 '1h', '6h', '24h', 'today')

    Returns:
        查询结果

    示例:
        get_panel_query_results(dashboard_uid='urJcwIvHz', panel_id=2, time_range='24h')
    """
    async def _get_panel_and_execute():
        grafana_url = os.getenv("GRAFANA_URL", DEFAULT_GRAFANA_URL)
        api_key = os.getenv("GRAFANA_API_KEY", DEFAULT_API_KEY)

        # 1. 获取面板配置
        url = f"{grafana_url}/api/dashboards/uid/{dashboard_uid}"
        headers = {"Content-Type": "application/json"}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"

        async with httpx.AsyncClient(headers=headers, timeout=30.0) as client:
            response = await client.get(url)
            response.raise_for_status()
            data = response.json()

        dashboard = data.get("dashboard", {})
        panel = None
        for p in dashboard.get("panels", []):
            if p.get("id") == panel_id:
                panel = p
                break

        if not panel:
            return {"success": False, "error": f"未找到面板 ID {panel_id}"}

        # 2. 解析数据源和查询目标
        datasource = panel.get("datasource", {})
        datasource_type = datasource.get("type", "unknown")
        targets = panel.get("targets", [])

        if not targets:
            return {"success": False, "error": "面板没有配置查询目标"}

        # 3. 执行查询
        time_from = f"now-{time_range}" if time_range != "today" else "now/d"
        time_to = "now"

        results = []
        for i, target in enumerate(targets):
            if datasource_type == "elasticsearch":
                result = await _execute_elasticsearch_target(target, time_from, time_to)
            elif datasource_type == "prometheus":
                result = await _execute_prometheus_target(target, time_from, time_to)
            else:
                result = {"success": False, "error": f"不支持的数据源类型: {datasource_type}"}

            results.append({
                "target_index": i,
                "datasource_type": datasource_type,
                "result": result,
            })

        return {
            "success": True,
            "panel": {
                "title": panel.get("title", "Untitled"),
                "id": panel_id,
                "type": panel.get("type", "unknown"),
                "datasource_type": datasource_type,
            },
            "time_range": f"{time_from} ~ {time_to}",
            "results": results,
        }

    # 执行异步查询
    result = _run_async(_get_panel_and_execute())

    # 4. 格式化返回结果
    if not result.get("success"):
        return f"❌ 查询失败: {result.get('error', 'Unknown error')}"

    panel_info = result.get("panel", {})
    time_range = result.get("time_range", "")
    query_results = result.get("results", [])

    lines = [
        f"📊 Panel 查询结果",
        f"{'='*60}",
        f"  标题: {panel_info.get('title', 'N/A')}",
        f"  ID: {panel_info.get('id', 'N/A')}",
        f"  类型: {panel_info.get('type', 'N/A')}",
        f"  数据源: {panel_info.get('datasource_type', 'N/A')}",
        f"  时间范围: {time_range}",
        f"{'='*60}",
    ]

    # 处理每个查询目标的结果
    for r in query_results:
        target_idx = r.get("target_index", 0)
        ds_type = r.get("datasource_type", "")
        query_result = r.get("result", {})

        lines.append(f"\n🎯 查询目标 #{target_idx + 1} ({ds_type}):")

        if not query_result.get("success"):
            lines.append(f"   ❌ 查询失败: {query_result.get('error', 'Unknown error')}")
            continue

        data = query_result.get("data", {})

        # 根据数据源类型格式化结果
        if ds_type == "elasticsearch":
            # 使用 ES 格式化函数
            formatted = format_es_results(data, time_from=time_range.split(" ~ ")[0])
            lines.append(f"   {formatted}")
        else:
            # 其他数据源，直接显示 JSON
            lines.append(f"   {json.dumps(data, ensure_ascii=False)[:500]}")

    return "\n".join(lines)
