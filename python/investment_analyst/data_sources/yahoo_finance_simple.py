#!/usr/bin/env python3
"""
简化版Yahoo Finance数据提供者
使用requests和yfinance的公共API获取数据
"""

import logging
import requests
import json
from typing import Dict, Any, Optional
from datetime import datetime
import time

from .base import BaseDataProvider
from utils.retry import retry_on_failure, rate_limiter
from utils.data_validation import validate_data_pipeline

logger = logging.getLogger(__name__)


class YahooFinanceSimpleProvider(BaseDataProvider):
    """简化版Yahoo Finance数据提供者"""

    def __init__(self, **kwargs):
        super().__init__("yahoo_finance_simple", **kwargs)

        # 配置参数
        self.timeout = kwargs.get('timeout', 30)
        self.rate_limit = kwargs.get('rate_limit', 30)  # 保守的速率限制

        # Yahoo Finance API端点
        self.base_url = "https://query1.finance.yahoo.com"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

        logger.info("简化版Yahoo Finance数据提供者初始化完成")

    @retry_on_failure(max_retries=3, delay=1.0, backoff=2.0)
    @rate_limiter(calls_per_second=2)
    def get_market_data(self, symbol: str) -> Dict[str, Any]:
        """
        获取市场数据

        Args:
            symbol: 股票代码

        Returns:
            市场数据
        """
        symbol = self._normalize_symbol(symbol)

        if not self._validate_symbol(symbol):
            return self.handle_error(symbol, ValueError(f"无效的股票代码: {symbol}"))

        try:
            logger.info(f"从Yahoo Finance获取 {symbol} 的市场数据")

            # 构建查询URL
            url = f"{self.base_url}/v8/finance/chart/{symbol}"

            # 添加查询参数
            params = {
                'interval': '1d',
                'range': '1y',
                'includePrePost': 'true',
                'events': 'div%7Csplit'
            }

            response = requests.get(
                url,
                params=params,
                headers=self.headers,
                timeout=self.timeout
            )
            response.raise_for_status()

            data = response.json()

            # 解析响应数据
            chart_data = data.get('chart', {}).get('result', [])
            if not chart_data:
                return self.handle_error(symbol, ValueError("无法获取图表数据"))

            result = chart_data[0]

            # 获取元数据
            meta = result.get('meta', {})
            if not meta:
                return self.handle_error(symbol, ValueError("无法获取元数据"))

            # 提取关键市场数据
            current_price = meta.get('regularMarketPrice', 0)
            previous_close = meta.get('previousClose', 0)

            market_data = {
                'current_price': float(current_price) if current_price else 0,
                'previous_close': float(previous_close) if previous_close else 0,
                'price_change': float(current_price - previous_close) if current_price and previous_close else 0,
                'price_change_percent': ((current_price / previous_close) - 1) * 100 if current_price and previous_close else 0,
                '52w_high': float(meta.get('fiftyTwoWeekHigh', 0)),
                '52w_low': float(meta.get('fiftyTwoWeekLow', 0)),
                'volume': int(meta.get('regularMarketVolume', 0)),
                'market_cap': int(meta.get('marketCap', 0)),
                'average_volume': int(meta.get('averageDailyVolume3Month', 0)),
                'pe_ratio': meta.get('trailingPE'),
                'dividend_yield': meta.get('dividendYield'),
                'beta': meta.get('beta'),
                'currency': meta.get('currency', 'USD'),
            }

            # 验证市场数据
            validation_result = validate_data_pipeline(market_data, "market")
            if not validation_result['is_valid']:
                logger.warning(f"市场数据验证失败: {validation_result['errors']}")

            return self._create_success_response(symbol, {
                'market_data': validation_result['cleaned_data'],
                'validation_warnings': validation_result.get('warnings', []),
                'data_type': 'market_data'
            })

        except Exception as e:
            logger.error(f"获取 {symbol} 市场数据时发生错误: {e}")
            return self.handle_error(symbol, e)

    @retry_on_failure(max_retries=3, delay=1.0, backoff=2.0)
    @rate_limiter(calls_per_second=2)
    def get_company_info(self, symbol: str) -> Dict[str, Any]:
        """
        获取公司基本信息

        Args:
            symbol: 股票代码

        Returns:
            公司信息
        """
        symbol = self._normalize_symbol(symbol)

        if not self._validate_symbol(symbol):
            return self.handle_error(symbol, ValueError(f"无效的股票代码: {symbol}"))

        try:
            logger.info(f"从Yahoo Finance获取 {symbol} 的公司信息")

            # 使用搜索API获取公司信息
            url = f"{self.base_url}/v1/finance/search"
            params = {
                'q': symbol,
                'quotesCount': 1,
                'newsCount': 0
            }

            response = requests.get(
                url,
                params=params,
                headers=self.headers,
                timeout=self.timeout
            )
            response.raise_for_status()

            data = response.json()

            # 解析搜索结果
            quotes = data.get('quotes', [])
            if not quotes:
                return self.handle_error(symbol, ValueError("无法找到公司信息"))

            quote = quotes[0]

            company_info = {
                'name': quote.get('longname', quote.get('shortname', '')),
                'symbol': quote.get('symbol', symbol),
                'exchange': quote.get('exchange', ''),
                'sector': quote.get('sectorDisp', ''),
                'industry': quote.get('industryDisp', ''),
                'market_cap': int(quote.get('marketCap', 0)),
                'currency': quote.get('currency', 'USD'),
            }

            return self._create_success_response(symbol, {
                'company_info': company_info,
                'data_type': 'company_info'
            })

        except Exception as e:
            logger.error(f"获取 {symbol} 公司信息时发生错误: {e}")
            return self.handle_error(symbol, e)

    def get_financial_statements(self, symbol: str, period: str = "annual") -> Dict[str, Any]:
        """
        获取财务报表数据
        注意：简化版本暂不支持财务报表，返回模拟数据

        Args:
            symbol: 股票代码
            period: 报告周期

        Returns:
            财务报表数据（模拟）
        """
        logger.warning(f"简化版Yahoo Finance提供者暂不支持财务报表，为 {symbol} 返回模拟数据")

        # 返回基本的模拟财务数据
        mock_financial_data = {
            'financial_statements': {
                'income_statement': {
                    'data': {
                        'revenue': 1000000000,  # 10亿
                        'gross_profit': 400000000,  # 4亿
                        'operating_income': 200000000,  # 2亿
                        'net_income': 150000000,  # 1.5亿
                        'eps': 1.50,
                    }
                },
                'balance_sheet': {
                    'data': {
                        'total_assets': 2000000000,  # 20亿
                        'total_liabilities': 1000000000,  # 10亿
                        'total_equity': 1000000000,  # 10亿
                        'cash_and_equivalents': 200000000,  # 2亿
                    }
                },
                'cash_flow_statement': {
                    'data': {
                        'operating_cash_flow': 250000000,  # 2.5亿
                        'investing_cash_flow': -100000000,  # -1亿
                        'financing_cash_flow': -50000000,  # -5000万
                    }
                }
            },
            'period': '2023',
            'currency': 'USD',
            'data_source': 'mock_yahoo_simple'
        }

        return self._create_success_response(symbol, {
            'financial_statements': mock_financial_data,
            'period': period,
            'data_type': 'financial_statements',
            'note': '模拟数据，简化版Yahoo Finance提供者暂不支持真实财务报表'
        })

    def get_comprehensive_data(self, symbol: str) -> Dict[str, Any]:
        """
        获取综合数据

        Args:
            symbol: 股票代码

        Returns:
            综合数据
        """
        symbol = self._normalize_symbol(symbol)

        try:
            logger.info(f"获取 {symbol} 的综合数据")

            # 分别获取各种数据
            market_data = self.get_market_data(symbol)
            company_info = self.get_company_info(symbol)
            financial_data = self.get_financial_statements(symbol)

            # 合并数据
            comprehensive_data = {
                'stock_symbol': symbol,
                'data_source': self.name,
                'status': 'success',
                'timestamp': datetime.now().isoformat(),
            }

            # 添加成功获取的数据
            if market_data.get('status') == 'success':
                comprehensive_data['market_data'] = market_data.get('market_data', {})

            if company_info.get('status') == 'success':
                comprehensive_data['company_info'] = company_info.get('company_info', {})

            if financial_data.get('status') == 'success':
                comprehensive_data['financial_statements'] = financial_data.get('financial_statements', {})

            # 添加验证警告
            warnings = []
            if 'validation_warnings' in market_data:
                warnings.extend(market_data['validation_warnings'])

            if warnings:
                comprehensive_data['validation_warnings'] = warnings

            return comprehensive_data

        except Exception as e:
            logger.error(f"获取 {symbol} 综合数据时发生错误: {e}")
            return self.handle_error(symbol, e)


# 测试函数
def test_yahoo_simple_provider():
    """测试简化版Yahoo Finance数据提供者"""
    provider = YahooFinanceSimpleProvider()

    # 测试股票代码
    test_symbols = ['AAPL', 'MSFT']

    for symbol in test_symbols:
        print(f"\n=== 测试 {symbol} ===")

        try:
            # 测试市场数据
            market_data = provider.get_market_data(symbol)
            print(f"市场数据: {market_data.get('status', 'unknown')}")
            if market_data.get('status') == 'success':
                price = market_data['market_data'].get('current_price', 0)
                print(f"当前价格: ${price:.2f}")

            # 等待一下避免速率限制
            time.sleep(1)

        except Exception as e:
            print(f"测试 {symbol} 时发生错误: {e}")


if __name__ == "__main__":
    # 设置日志
    logging.basicConfig(level=logging.INFO)

    # 运行测试
    test_yahoo_simple_provider()