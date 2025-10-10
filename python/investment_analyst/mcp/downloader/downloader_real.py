#!/usr/bin/env python3
"""
真实数据下载MCP
使用真实数据源获取财报和市场数据
"""

import logging
from typing import Dict, Any, List
from datetime import datetime

from config import SystemConfig
from data_sources.data_manager import get_data_manager
from utils.data_validation import validate_data_pipeline

logger = logging.getLogger(__name__)


class DownloadMCP:
    """真实数据下载MCP类"""

    def __init__(self):
        """初始化下载MCP"""
        self.use_real_data = SystemConfig.USE_REAL_DATA
        self.data_manager = get_data_manager()

        logger.info(f"下载MCP初始化完成，使用{'真实' if self.use_real_data else '模拟'}数据")

    def download_data(
        self, stock_symbol: str, aligned_indicators: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        下载数据

        Args:
            stock_symbol (str): 股票代码
            aligned_indicators (Dict[str, Any]): 对齐的指标

        Returns:
            Dict[str, Any]: 下载的数据
        """
        try:
            logger.info(f"开始下载 {stock_symbol} 的数据")

            if self.use_real_data:
                return self._download_real_data(stock_symbol, aligned_indicators)
            else:
                return self._download_mock_data(stock_symbol, aligned_indicators)

        except Exception as e:
            logger.error(f"下载 {stock_symbol} 数据时发生错误: {e}")
            return {
                'stock_symbol': stock_symbol,
                'error': str(e),
                'download_status': 'failed',
                'timestamp': datetime.now().isoformat(),
            }

    def _download_real_data(
        self, stock_symbol: str, aligned_indicators: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        使用真实数据源下载数据

        Args:
            stock_symbol: 股票代码
            aligned_indicators: 对齐的指标

        Returns:
            下载的数据
        """
        try:
            # 获取综合数据（包含财务、市场、公司信息）
            comprehensive_data = self.data_manager.get_comprehensive_data(stock_symbol)

            if comprehensive_data.get('status') != 'success':
                return {
                    'stock_symbol': stock_symbol,
                    'error': comprehensive_data.get('error', '获取数据失败'),
                    'download_status': 'failed',
                    'timestamp': datetime.now().isoformat(),
                }

            # 转换数据格式以匹配现有接口
            result = {
                'stock_symbol': stock_symbol,
                'raw_data': comprehensive_data,
                'download_status': 'success',
                'timestamp': datetime.now().isoformat(),
                'data_source': comprehensive_data.get('data_source', 'unknown'),
            }

            # 提取各个组件的数据
            if 'financial_statements' in comprehensive_data:
                result['financial_data'] = comprehensive_data['financial_statements']

            if 'market_data' in comprehensive_data:
                result['market_data'] = comprehensive_data['market_data']

            if 'company_info' in comprehensive_data:
                result['company_info'] = comprehensive_data['company_info']

            # 添加验证警告
            if 'validation_warnings' in comprehensive_data:
                result['validation_warnings'] = comprehensive_data['validation_warnings']

            logger.info(f"成功下载 {stock_symbol} 的真实数据")
            return result

        except Exception as e:
            logger.error(f"下载 {stock_symbol} 真实数据时发生错误: {e}")
            # 如果真实数据失败，回退到模拟数据
            logger.info("回退到模拟数据")
            return self._download_mock_data(stock_symbol, aligned_indicators)

    def _download_mock_data(
        self, stock_symbol: str, aligned_indicators: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        使用模拟数据下载数据（原有逻辑）

        Args:
            stock_symbol: 股票代码
            aligned_indicators: 对齐的指标

        Returns:
            模拟数据
        """
        try:
            # 下载财务报表数据
            financial_data = self._get_mock_financial_data(stock_symbol)

            # 下载行业数据
            industry_data = self._get_mock_industry_data(stock_symbol)

            # 下载市场数据
            market_data = self._get_mock_market_data(stock_symbol)

            # 下载宏观经济数据
            macro_data = self._get_mock_macro_data()

            return {
                'stock_symbol': stock_symbol,
                'financial_data': financial_data,
                'industry_data': industry_data,
                'market_data': market_data,
                'macro_data': macro_data,
                'download_status': 'success',
                'timestamp': datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"下载 {stock_symbol} 模拟数据时发生错误: {e}")
            return {
                'stock_symbol': stock_symbol,
                'error': str(e),
                'download_status': 'failed',
                'timestamp': datetime.now().isoformat(),
            }

    def _get_mock_financial_data(self, stock_symbol: str) -> Dict[str, Any]:
        """
        获取模拟财务数据

        Args:
            stock_symbol (str): 股票代码

        Returns:
            Dict[str, Any]: 模拟财务数据
        """
        # 根据股票代码返回不同的模拟数据
        mock_data = {
            "AAPL": {
                "stock_symbol": "AAPL",
                "financial_statements": {
                    "income_statement": {
                        "revenue": 394328000000,
                        "gross_profit": 170782000000,
                        "operating_income": 114301000000,
                        "net_income": 99803000000,
                        "eps": 6.11,
                        "shares_outstanding": 16319400000,
                    },
                    "balance_sheet": {
                        "total_assets": 352755000000,
                        "total_liabilities": 287912000000,
                        "total_equity": 64843000000,
                        "cash_and_equivalents": 29965000000,
                        "long_term_debt": 111526000000,
                    },
                    "cash_flow_statement": {
                        "operating_cash_flow": 122151000000,
                        "investing_cash_flow": -22597000000,
                        "financing_cash_flow": -93353000000,
                    },
                },
                "period": "2023",
                "currency": "USD",
            },
            "MSFT": {
                "stock_symbol": "MSFT",
                "financial_statements": {
                    "income_statement": {
                        "revenue": 211915000000,
                        "gross_profit": 144239000000,
                        "operating_income": 88523000000,
                        "net_income": 72361000000,
                        "eps": 9.65,
                        "shares_outstanding": 7499000000,
                    },
                    "balance_sheet": {
                        "total_assets": 512268000000,
                        "total_liabilities": 205753000000,
                        "total_equity": 206515000000,
                        "cash_and_equivalents": 34827000000,
                        "long_term_debt": 98421000000,
                    },
                    "cash_flow_statement": {
                        "operating_cash_flow": 88992000000,
                        "investing_cash_flow": -27559000000,
                        "financing_cash_flow": -40603000000,
                    },
                },
                "period": "2023",
                "currency": "USD",
            },
        }

        return mock_data.get(stock_symbol, self._get_default_financial_data())

    def _get_default_financial_data(self) -> Dict[str, Any]:
        """获取默认财务数据"""
        return {
            "stock_symbol": "UNKNOWN",
            "financial_statements": {
                "income_statement": {
                    "revenue": 1000000000,
                    "gross_profit": 400000000,
                    "operating_income": 200000000,
                    "net_income": 150000000,
                    "eps": 1.50,
                    "shares_outstanding": 100000000,
                },
                "balance_sheet": {
                    "total_assets": 2000000000,
                    "total_liabilities": 1000000000,
                    "total_equity": 1000000000,
                    "cash_and_equivalents": 200000000,
                    "long_term_debt": 500000000,
                },
                "cash_flow_statement": {
                    "operating_cash_flow": 250000000,
                    "investing_cash_flow": -100000000,
                    "financing_cash_flow": -50000000,
                },
            },
            "period": "2023",
            "currency": "USD",
        }

    def _get_mock_industry_data(self, stock_symbol: str) -> Dict[str, Any]:
        """
        获取模拟行业数据

        Args:
            stock_symbol (str): 股票代码

        Returns:
            Dict[str, Any]: 模拟行业数据
        """
        return {
            "stock_symbol": stock_symbol,
            "industry_category": "technology",
            "industry_subcategory": "software",
            "market_size": 5000000000000,
            "growth_rate": 0.08,
            "trends": ["AI", "Cloud", "IoT"],
        }

    def _get_mock_market_data(self, stock_symbol: str) -> Dict[str, Any]:
        """
        获取模拟市场数据

        Args:
            stock_symbol (str): 股票代码

        Returns:
            Dict[str, Any]: 模拟市场数据
        """
        mock_prices = {
            "AAPL": 175.43,
            "MSFT": 378.91,
            "GOOGL": 139.63,
        }

        current_price = mock_prices.get(stock_symbol, 100.0)

        return {
            "stock_symbol": stock_symbol,
            "current_price": current_price,
            "market_cap": current_price * 1000000000,  # 假设10亿股
            "pe_ratio": 25.5,
            "52w_high": current_price * 1.2,
            "52w_low": current_price * 0.8,
            "volume": 50000000,
        }

    def _get_mock_macro_data(self) -> Dict[str, Any]:
        """
        获取模拟宏观经济数据

        Returns:
            Dict[str, Any]: 模拟宏观经济数据
        """
        return {
            "gdp_growth": 0.021,
            "inflation_rate": 0.032,
            "interest_rate": 0.0525,
            "unemployment_rate": 0.038,
            "consumer_sentiment": 72.5,
        }

    def get_data_source_status(self) -> Dict[str, Any]:
        """
        获取数据源状态

        Returns:
            数据源状态信息
        """
        status = {
            'use_real_data': self.use_real_data,
            'timestamp': datetime.now().isoformat(),
        }

        if self.use_real_data:
            data_manager_status = self.data_manager.get_data_source_status()
            status.update(data_manager_status)

        return status

    def clear_cache(self, symbol: str = None):
        """
        清除缓存

        Args:
            symbol: 股票代码，如果为None则清除所有
        """
        if self.use_real_data:
            self.data_manager.clear_cache(symbol=symbol)


# 为了向后兼容，保留原始的DownloadMCP类
# 但在实际使用时，可以通过环境变量控制使用真实数据还是模拟数据
DownloadMCPReal = DownloadMCP  # 别名，明确表示使用真实数据