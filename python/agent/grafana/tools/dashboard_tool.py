#!/usr/bin/env python3
"""
Dashboard Explorer Agent Tool
智能 Dashboard 和 Panel 探索的 Agent Tool
"""

import asyncio
import json
import os
from typing import Any

import httpx
import nest_asyncio

# 允许嵌套事件循环 (ADK 运行在已有事件循环中)
nest_asyncio.apply()


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
    "get_dashboard_recommendations",
]
