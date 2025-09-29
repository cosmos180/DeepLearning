"""
Author       : bughero bughero2012@gmail.com
Date         : 2025-09-03 17:16:46
LastEditors  : bughero bughero2012@gmail.com
LastEditTime : 2025-09-03 17:16:56
FilePath     : /DeepLearning/python/mcp/grafana/setup.py
Description  :

Copyright (c) 2025 by @Me, All Rights Reserved.
"""

#!/usr/bin/env python3
"""
Setup script for Grafana MCP Server
"""

from setuptools import setup, find_packages

setup(
    name="grafana-mcp-server",
    version="1.0.0",
    description="MCP Server for reading Grafana dashboard panels",
    author="DeepLearning",
    packages=find_packages(),
    install_requires=[
        "mcp>=1.0.0",
        "httpx>=0.25.0",
    ],
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "grafana-mcp-server=grafana.server:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
)
