#!/usr/bin/env python3
"""
Grafana Agent 入口文件
供 adk run 命令使用
"""

from grafana_agent_adk import agent as root_agent

__all__ = ['root_agent']
