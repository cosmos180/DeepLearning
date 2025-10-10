#!/usr/bin/env python3
"""
数据源模块
提供各种金融数据源的统一接口
"""

from .base import BaseDataProvider
from .yahoo_finance import YahooFinanceProvider

__all__ = [
    'BaseDataProvider',
    'YahooFinanceProvider'
]