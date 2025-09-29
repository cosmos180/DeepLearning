"""
Author       : bughero bughero2012@gmail.com
Date         : 2025-09-03 17:18:17
LastEditors  : bughero bughero2012@gmail.com
LastEditTime : 2025-09-03 17:18:25
FilePath     : /DeepLearning/python/mcp/grafana/__init__.py
Description  :

Copyright (c) 2025 by @Me, All Rights Reserved.
"""

"""
Grafana MCP Server Package

This package provides an MCP (Model Context Protocol) server for reading
panels from specified Grafana dashboards.
"""

__version__ = "1.0.0"
__author__ = "DeepLearning"
__email__ = "contact@example.com"

from .server import main

__all__ = ["main"]
