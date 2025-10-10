#!/usr/bin/env python3
"""
数据管理器
统一管理多个数据源，提供数据获取和缓存功能
"""

import logging
import time
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

from config import (
    SystemConfig,
    CacheConfig,
    get_enabled_data_sources,
    is_data_source_enabled
)
# 尝试导入完整的Yahoo Finance提供者，如果失败则使用简化版
try:
    from .yahoo_finance import YahooFinanceProvider
    YAHOO_FULL_AVAILABLE = True
except ImportError:
    from .yahoo_finance_simple import YahooFinanceSimpleProvider as YahooFinanceProvider
    YAHOO_FULL_AVAILABLE = False
    logger.info("使用简化版Yahoo Finance提供者")

logger = logging.getLogger(__name__)


class DataManager:
    """数据管理器"""

    def __init__(self):
        """
        初始化数据管理器
        """
        self.providers = {}
        self.cache_enabled = CacheConfig.REDIS_ENABLED
        self.cache = None

        # 初始化数据提供者
        self._initialize_providers()

        # 初始化缓存
        if self.cache_enabled:
            self._initialize_cache()

        logger.info(f"数据管理器初始化完成，启用的数据源: {list(self.providers.keys())}")

    def _initialize_providers(self):
        """初始化所有可用的数据提供者"""
        try:
            # Yahoo Finance (主要数据源)
            if is_data_source_enabled("financial", "yahoo"):
                self.providers["yahoo"] = YahooFinanceProvider(
                    timeout=30,
                    rate_limit=2000
                )
                logger.info("Yahoo Finance数据提供者初始化成功")

            # TODO: 添加其他数据提供者
            # if is_data_source_enabled("financial", "financial_modeling_prep"):
            #     from .fmp_provider import FMPProvider
            #     self.providers["fmp"] = FMPProvider(
            #         api_key=os.getenv("FMP_API_KEY")
            #     )

        except Exception as e:
            logger.error(f"初始化数据提供者时发生错误: {e}")

    def _initialize_cache(self):
        """初始化缓存"""
        try:
            import redis
            self.cache = redis.from_url(CacheConfig.REDIS_URL)
            # 测试连接
            self.cache.ping()
            logger.info("Redis缓存初始化成功")
        except Exception as e:
            logger.warning(f"Redis缓存初始化失败，将禁用缓存: {e}")
            self.cache_enabled = False

    def get_financial_data(self, symbol: str, use_cache: bool = True) -> Dict[str, Any]:
        """
        获取财务数据

        Args:
            symbol: 股票代码
            use_cache: 是否使用缓存

        Returns:
            财务数据
        """
        return self._get_data_with_fallback(
            symbol=symbol,
            data_type="financial",
            method_name="get_financial_statements",
            use_cache=use_cache
        )

    def get_market_data(self, symbol: str, use_cache: bool = True) -> Dict[str, Any]:
        """
        获取市场数据

        Args:
            symbol: 股票代码
            use_cache: 是否使用缓存

        Returns:
            市场数据
        """
        return self._get_data_with_fallback(
            symbol=symbol,
            data_type="market",
            method_name="get_market_data",
            use_cache=use_cache
        )

    def get_company_info(self, symbol: str, use_cache: bool = True) -> Dict[str, Any]:
        """
        获取公司信息

        Args:
            symbol: 股票代码
            use_cache: 是否使用缓存

        Returns:
            公司信息
        """
        return self._get_data_with_fallback(
            symbol=symbol,
            data_type="company_info",
            method_name="get_company_info",
            use_cache=use_cache
        )

    def get_comprehensive_data(self, symbol: str) -> Dict[str, Any]:
        """
        获取综合数据（财务、市场、公司信息）

        Args:
            symbol: 股票代码

        Returns:
            综合数据
        """
        try:
            logger.info(f"获取 {symbol} 的综合数据")

            # 使用主要数据源获取所有数据
            primary_source = self._get_primary_source("financial")
            if not primary_source:
                return {
                    'stock_symbol': symbol,
                    'status': 'failed',
                    'error': '没有可用的数据源',
                    'timestamp': datetime.now().isoformat()
                }

            provider = self.providers[primary_source]

            # 如果是Yahoo Finance，使用综合数据方法
            if primary_source == "yahoo" and hasattr(provider, 'get_comprehensive_data'):
                return provider.get_comprehensive_data(symbol)

            # 否则分别获取各种数据
            comprehensive_data = {
                'stock_symbol': symbol,
                'data_source': primary_source,
                'status': 'success',
                'timestamp': datetime.now().isoformat(),
            }

            # 获取各种类型的数据
            financial_data = self.get_financial_data(symbol, use_cache=False)
            if financial_data.get('status') == 'success':
                comprehensive_data['financial_statements'] = financial_data.get('financial_statements', {})

            market_data = self.get_market_data(symbol, use_cache=False)
            if market_data.get('status') == 'success':
                comprehensive_data['market_data'] = market_data.get('market_data', {})

            company_info = self.get_company_info(symbol, use_cache=False)
            if company_info.get('status') == 'success':
                comprehensive_data['company_info'] = company_info.get('company_info', {})

            return comprehensive_data

        except Exception as e:
            logger.error(f"获取 {symbol} 综合数据时发生错误: {e}")
            return {
                'stock_symbol': symbol,
                'status': 'failed',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }

    def _get_data_with_fallback(
        self,
        symbol: str,
        data_type: str,
        method_name: str,
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """
        使用故障转移机制获取数据

        Args:
            symbol: 股票代码
            data_type: 数据类型
            method_name: 要调用的方法名
            use_cache: 是否使用缓存

        Returns:
            数据
        """
        # 检查缓存
        if use_cache and self.cache_enabled:
            cached_data = self._get_cached_data(symbol, data_type)
            if cached_data:
                logger.debug(f"从缓存获取 {symbol} 的{data_type}数据")
                return cached_data

        # 获取数据源优先级
        sources = SystemConfig.DATA_SOURCE_PRIORITY.get(data_type, [])

        # 尝试每个数据源
        last_error = None
        for source_name in sources:
            if source_name not in self.providers:
                continue

            try:
                logger.debug(f"尝试从 {source_name} 获取 {symbol} 的{data_type}数据")
                provider = self.providers[source_name]
                method = getattr(provider, method_name)

                result = method(symbol)

                if result.get('status') == 'success':
                    # 缓存成功的结果
                    if use_cache and self.cache_enabled:
                        self._cache_data(symbol, data_type, result)

                    logger.info(f"成功从 {source_name} 获取 {symbol} 的{data_type}数据")
                    return result
                else:
                    last_error = result.get('error', '未知错误')
                    logger.warning(f"{source_name} 返回错误: {last_error}")

            except Exception as e:
                last_error = str(e)
                logger.error(f"从 {source_name} 获取 {symbol} 数据时发生错误: {e}")
                continue

        # 所有数据源都失败
        logger.error(f"所有数据源都无法获取 {symbol} 的{data_type}数据")
        return {
            'stock_symbol': symbol,
            'status': 'failed',
            'error': f'所有数据源失败。最后错误: {last_error}',
            'timestamp': datetime.now().isoformat()
        }

    def _get_primary_source(self, data_type: str) -> Optional[str]:
        """
        获取主要数据源

        Args:
            data_type: 数据类型

        Returns:
            主要数据源名称
        """
        sources = SystemConfig.DATA_SOURCE_PRIORITY.get(data_type, [])
        for source in sources:
            if source in self.providers:
                return source
        return None

    def _get_cached_data(self, symbol: str, data_type: str) -> Optional[Dict[str, Any]]:
        """
        从缓存获取数据

        Args:
            symbol: 股票代码
            data_type: 数据类型

        Returns:
            缓存的数据，如果不存在或过期返回None
        """
        if not self.cache:
            return None

        try:
            cache_key = f"{CacheConfig.CACHE_KEYS[data_type]}{symbol}"
            cached_data = self.cache.get(cache_key)

            if cached_data:
                import json
                data = json.loads(cached_data)
                logger.debug(f"从缓存获取 {symbol} 的{data_type}数据")
                return data

        except Exception as e:
            logger.warning(f"从缓存获取数据时发生错误: {e}")

        return None

    def _cache_data(self, symbol: str, data_type: str, data: Dict[str, Any]):
        """
        缓存数据

        Args:
            symbol: 股票代码
            data_type: 数据类型
            data: 要缓存的数据
        """
        if not self.cache:
            return

        try:
            cache_key = f"{CacheConfig.CACHE_KEYS[data_type]}{symbol}"
            ttl = CacheConfig.CACHE_DURATION.get(data_type, 3600)

            import json
            serialized_data = json.dumps(data, default=str)
            self.cache.setex(cache_key, ttl, serialized_data)

            logger.debug(f"已缓存 {symbol} 的{data_type}数据，TTL: {ttl}秒")

        except Exception as e:
            logger.warning(f"缓存数据时发生错误: {e}")

    def clear_cache(self, symbol: str = None, data_type: str = None):
        """
        清除缓存

        Args:
            symbol: 股票代码，如果为None则清除所有
            data_type: 数据类型，如果为None则清除所有类型
        """
        if not self.cache:
            return

        try:
            if symbol and data_type:
                # 清除特定股票和类型的缓存
                cache_key = f"{CacheConfig.CACHE_KEYS[data_type]}{symbol}"
                self.cache.delete(cache_key)
                logger.info(f"已清除 {symbol} 的{data_type}缓存")

            elif symbol:
                # 清除特定股票的所有缓存
                for prefix in CacheConfig.CACHE_KEYS.values():
                    pattern = f"{prefix}{symbol}"
                    keys = self.cache.keys(pattern)
                    if keys:
                        self.cache.delete(*keys)
                        logger.info(f"已清除 {symbol} 的所有缓存")

            else:
                # 清除所有缓存
                self.cache.flushdb()
                logger.info("已清除所有缓存")

        except Exception as e:
            logger.error(f"清除缓存时发生错误: {e}")

    def get_data_source_status(self) -> Dict[str, Any]:
        """
        获取数据源状态

        Returns:
            数据源状态信息
        """
        status = {
            'enabled_providers': list(self.providers.keys()),
            'cache_enabled': self.cache_enabled,
            'cache_connected': self.cache is not None,
            'timestamp': datetime.now().isoformat()
        }

        # 测试每个数据源
        for name, provider in self.providers.items():
            try:
                # 使用简单的股票代码测试连接
                test_result = provider.get_market_data('AAPL')
                status[f'{name}_status'] = test_result.get('status', 'unknown')
            except Exception as e:
                status[f'{name}_status'] = f'error: {str(e)}'

        return status


# 全局数据管理器实例
_data_manager = None


def get_data_manager() -> DataManager:
    """
    获取全局数据管理器实例

    Returns:
        数据管理器实例
    """
    global _data_manager
    if _data_manager is None:
        _data_manager = DataManager()
    return _data_manager


def reset_data_manager():
    """重置全局数据管理器"""
    global _data_manager
    _data_manager = None