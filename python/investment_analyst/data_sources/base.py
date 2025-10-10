#!/usr/bin/env python3
"""
数据提供者基类
定义数据提供者的通用接口
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from datetime import datetime

class BaseDataProvider(ABC):
    """数据提供者基类"""

    def __init__(self, name: str, **kwargs):
        """
        初始化数据提供者

        Args:
            name: 数据提供者名称
            **kwargs: 其他配置参数
        """
        self.name = name
        self.config = kwargs
        self.last_request_time = None

    @abstractmethod
    def get_financial_statements(self, symbol: str, period: str = "annual") -> Dict[str, Any]:
        """
        获取财务报表数据

        Args:
            symbol: 股票代码
            period: 报告周期 (annual/quarterly)

        Returns:
            财务报表数据
        """
        pass

    @abstractmethod
    def get_market_data(self, symbol: str) -> Dict[str, Any]:
        """
        获取市场数据

        Args:
            symbol: 股票代码

        Returns:
            市场数据
        """
        pass

    @abstractmethod
    def get_company_info(self, symbol: str) -> Dict[str, Any]:
        """
        获取公司基本信息

        Args:
            symbol: 股票代码

        Returns:
            公司信息
        """
        pass

    def get_data_source_info(self) -> Dict[str, Any]:
        """
        获取数据源信息

        Returns:
            数据源信息
        """
        return {
            'name': self.name,
            'type': self.__class__.__name__,
            'last_request_time': self.last_request_time,
            'config': self.config
        }

    def handle_error(self, symbol: str, error: Exception) -> Dict[str, Any]:
        """
        统一的错误处理

        Args:
            symbol: 股票代码
            error: 异常对象

        Returns:
            错误响应
        """
        return {
            'stock_symbol': symbol,
            'data_source': self.name,
            'status': 'failed',
            'error': str(error),
            'timestamp': datetime.now().isoformat()
        }

    def _validate_symbol(self, symbol: str) -> bool:
        """
        验证股票代码格式

        Args:
            symbol: 股票代码

        Returns:
            是否有效
        """
        if not symbol or not isinstance(symbol, str):
            return False

        # 基本的股票代码验证
        symbol = symbol.upper().strip()
        return len(symbol) >= 1 and len(symbol) <= 10 and symbol.isalnum()

    def _normalize_symbol(self, symbol: str) -> str:
        """
        标准化股票代码

        Args:
            symbol: 原始股票代码

        Returns:
            标准化后的股票代码
        """
        if not symbol:
            return ""

        return symbol.upper().strip()

    def _create_success_response(self, symbol: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        创建成功响应

        Args:
            symbol: 股票代码
            data: 返回的数据

        Returns:
            标准化的成功响应
        """
        response = {
            'stock_symbol': symbol,
            'data_source': self.name,
            'status': 'success',
            'timestamp': datetime.now().isoformat()
        }
        response.update(data)

        self.last_request_time = datetime.now()
        return response