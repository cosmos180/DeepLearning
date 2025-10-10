#!/usr/bin/env python3
"""
Yahoo Finance数据提供者
使用yfinance库获取真实的财务和市场数据
"""

import logging
import pandas as pd
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import time

try:
    import yfinance as yf
    YFINANCE_AVAILABLE = True
except ImportError:
    YFINANCE_AVAILABLE = False
    logging.warning("yfinance库未安装，Yahoo Finance数据提供者不可用")

from .base import BaseDataProvider
from utils.retry import retry_on_failure, rate_limiter
from utils.data_validation import validate_data_pipeline

logger = logging.getLogger(__name__)


class YahooFinanceProvider(BaseDataProvider):
    """Yahoo Finance数据提供者"""

    def __init__(self, **kwargs):
        super().__init__("yahoo_finance", **kwargs)

        if not YFINANCE_AVAILABLE:
            raise ImportError("yfinance库未安装，请运行: pip install yfinance")

        # 配置参数
        self.timeout = kwargs.get('timeout', 30)
        self.rate_limit = kwargs.get('rate_limit', 2000)  # 每分钟请求数

        logger.info("Yahoo Finance数据提供者初始化完成")

    @retry_on_failure(max_retries=3, delay=1.0, backoff=2.0)
    @rate_limiter(calls_per_second=30)  # 保守的速率限制
    def get_financial_statements(self, symbol: str, period: str = "annual") -> Dict[str, Any]:
        """
        获取财务报表数据

        Args:
            symbol: 股票代码
            period: 报告周期 (annual/quarterly)

        Returns:
            财务报表数据
        """
        symbol = self._normalize_symbol(symbol)

        if not self._validate_symbol(symbol):
            return self.handle_error(symbol, ValueError(f"无效的股票代码: {symbol}"))

        try:
            logger.info(f"从Yahoo Finance获取 {symbol} 的财务报表数据")

            # 创建股票对象
            ticker = yf.Ticker(symbol)

            # 获取财务报表
            financial_statements = {}

            # 损益表
            income_stmt = ticker.financials
            if income_stmt is not None and not income_stmt.empty:
                financial_statements['income_statement'] = self._convert_financial_statement(
                    income_stmt, period
                )

            # 资产负债表
            balance_sheet = ticker.balance_sheet
            if balance_sheet is not None and not balance_sheet.empty:
                financial_statements['balance_sheet'] = self._convert_financial_statement(
                    balance_sheet, period
                )

            # 现金流量表
            cash_flow = ticker.cash_flow
            if cash_flow is not None and not cash_flow.empty:
                financial_statements['cash_flow_statement'] = self._convert_financial_statement(
                    cash_flow, period
                )

            # 如果没有获取到数据，尝试季度数据
            if not financial_statements and period == "annual":
                logger.info(f"年度数据不可用，尝试获取 {symbol} 的季度数据")
                return self.get_financial_statements(symbol, "quarterly")

            if not financial_statements:
                return self.handle_error(symbol, ValueError("无法获取财务报表数据"))

            return self._create_success_response(symbol, {
                'financial_statements': financial_statements,
                'period': period,
                'data_type': 'financial_statements'
            })

        except Exception as e:
            logger.error(f"获取 {symbol} 财务报表时发生错误: {e}")
            return self.handle_error(symbol, e)

    @retry_on_failure(max_retries=3, delay=1.0, backoff=2.0)
    @rate_limiter(calls_per_second=30)
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

            ticker = yf.Ticker(symbol)

            # 获取历史价格数据
            hist = ticker.history(period="1y")
            if hist is None or hist.empty:
                return self.handle_error(symbol, ValueError("无法获取历史价格数据"))

            # 获取公司信息
            info = ticker.info or {}

            # 计算关键市场指标
            current_price = float(hist['Close'].iloc[-1])

            market_data = {
                'current_price': current_price,
                'price_change': float(hist['Close'].iloc[-1] - hist['Close'].iloc[-2]) if len(hist) > 1 else 0,
                'price_change_percent': ((hist['Close'].iloc[-1] / hist['Close'].iloc[-2]) - 1) * 100 if len(hist) > 1 else 0,
                'volume': int(hist['Volume'].iloc[-1]) if not pd.isna(hist['Volume'].iloc[-1]) else 0,
                '52w_high': float(hist['High'].max()),
                '52w_low': float(hist['Low'].min()),
                'market_cap': info.get('marketCap', 0),
                'average_volume': int(hist['Volume'].mean()) if not pd.isna(hist['Volume'].mean()) else 0,
                'beta': info.get('beta', None),
                'pe_ratio': info.get('trailingPE', None),
                'dividend_yield': info.get('dividendYield', None),
                '52w_return': ((hist['Close'].iloc[-1] / hist['Close'].iloc[0]) - 1) * 100 if len(hist) > 1 else 0,
            }

            # 验证市场数据
            validation_result = validate_data_pipeline(market_data, "market")
            if not validation_result['is_valid']:
                logger.warning(f"市场数据验证失败: {validation_result['errors']}")

            return self._create_success_response(symbol, {
                'market_data': validation_result['cleaned_data'],
                'validation_warnings': validation_result['warnings'],
                'data_type': 'market_data'
            })

        except Exception as e:
            logger.error(f"获取 {symbol} 市场数据时发生错误: {e}")
            return self.handle_error(symbol, e)

    @retry_on_failure(max_retries=3, delay=1.0, backoff=2.0)
    @rate_limiter(calls_per_second=30)
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

            ticker = yf.Ticker(symbol)
            info = ticker.info or {}

            company_info = {
                'name': info.get('longName', info.get('shortName', '')),
                'symbol': info.get('symbol', symbol),
                'sector': info.get('sector', ''),
                'industry': info.get('industry', ''),
                'country': info.get('country', ''),
                'currency': info.get('currency', 'USD'),
                'exchange': info.get('exchange', ''),
                'market_cap': info.get('marketCap', 0),
                'enterprise_value': info.get('enterpriseValue', 0),
                'employees': info.get('fullTimeEmployees', 0),
                'website': info.get('website', ''),
                'business_summary': info.get('longBusinessSummary', ''),
                'ipo_date': info.get('ipoDate', ''),
                'shares_outstanding': info.get('sharesOutstanding', 0),
            }

            # 添加分析师预测
            if 'recommendationKey' in info:
                company_info['analyst_recommendation'] = info['recommendationKey']

            if 'targetMeanPrice' in info:
                company_info['analyst_price_target'] = info['targetMeanPrice']

            return self._create_success_response(symbol, {
                'company_info': company_info,
                'data_type': 'company_info'
            })

        except Exception as e:
            logger.error(f"获取 {symbol} 公司信息时发生错误: {e}")
            return self.handle_error(symbol, e)

    def _convert_financial_statement(self, df: pd.DataFrame, period: str) -> Dict[str, Any]:
        """
        转换财务报表DataFrame为字典格式

        Args:
            df: Yahoo Finance返回的DataFrame
            period: 报告周期

        Returns:
            标准化的财务报表字典
        """
        if df is None or df.empty:
            return {}

        try:
            # 获取最新期间的数据
            if len(df.columns) > 0:
                latest_period = df.columns[0]
                latest_data = df[latest_period]
            else:
                return {}

            # 转换为字典并清理数据
            financial_data = {}

            for index, value in latest_data.items():
                if pd.isna(value):
                    financial_data[index] = 0.0
                else:
                    # 确保数值类型
                    try:
                        financial_data[index] = float(value)
                    except (ValueError, TypeError):
                        financial_data[index] = 0.0

            # 标准化常见的财务字段名
            field_mapping = {
                # 损益表字段
                'Total Revenue': 'revenue',
                'Revenue': 'revenue',
                'Gross Profit': 'gross_profit',
                'Operating Income': 'operating_income',
                'Net Income': 'net_income',
                'Net Income From Continuing Ops': 'net_income',
                'Earnings Per Share': 'eps',
                'Diluted EPS': 'eps',

                # 资产负债表字段
                'Total Assets': 'total_assets',
                'Total Liabilities': 'total_liabilities',
                'Total Stockholder Equity': 'total_equity',
                'Total Current Assets': 'current_assets',
                'Total Current Liabilities': 'current_liabilities',
                'Cash And Cash Equivalents': 'cash_and_equivalents',
                'Long Term Debt': 'long_term_debt',

                # 现金流量表字段
                'Operating Cash Flow': 'operating_cash_flow',
                'Investing Cash Flow': 'investing_cash_flow',
                'Financing Cash Flow': 'financing_cash_flow',
                'Free Cash Flow': 'free_cash_flow',
                'Capital Expenditure': 'capital_expenditure',
            }

            # 应用字段映射
            standardized_data = {}
            for original_field, value in financial_data.items():
                # 查找匹配的标准字段名
                standard_field = field_mapping.get(original_field, original_field.lower().replace(' ', '_'))
                standardized_data[standard_field] = value

            return {
                'data': standardized_data,
                'period': latest_period,
                'currency': 'USD',  # Yahoo Finance默认美元
                'statement_type': self._determine_statement_type(list(standardized_data.keys())),
            }

        except Exception as e:
            logger.error(f"转换财务报表时发生错误: {e}")
            return {}

    def _determine_statement_type(self, fields: List[str]) -> str:
        """
        根据字段判断财务报表类型

        Args:
            fields: 财务报表字段列表

        Returns:
            报表类型
        """
        fields_lower = [field.lower() for field in fields]

        if any('revenue' in field or 'income' in field for field in fields_lower):
            return 'income_statement'
        elif any('assets' in field or 'liabilities' in field or 'equity' in field for field in fields_lower):
            return 'balance_sheet'
        elif any('cash flow' in field or 'operating cash' in field for field in fields_lower):
            return 'cash_flow_statement'
        else:
            return 'unknown'

    def get_comprehensive_data(self, symbol: str) -> Dict[str, Any]:
        """
        获取综合数据（财务、市场、公司信息）

        Args:
            symbol: 股票代码

        Returns:
            综合数据
        """
        symbol = self._normalize_symbol(symbol)

        try:
            logger.info(f"获取 {symbol} 的综合数据")

            # 并行获取各种数据
            financial_data = self.get_financial_statements(symbol)
            market_data = self.get_market_data(symbol)
            company_info = self.get_company_info(symbol)

            # 合并数据
            comprehensive_data = {
                'stock_symbol': symbol,
                'data_source': self.name,
                'status': 'success',
                'timestamp': datetime.now().isoformat(),
            }

            # 添加成功获取的数据
            if financial_data.get('status') == 'success':
                comprehensive_data['financial_statements'] = financial_data.get('financial_statements', {})

            if market_data.get('status') == 'success':
                comprehensive_data['market_data'] = market_data.get('market_data', {})

            if company_info.get('status') == 'success':
                comprehensive_data['company_info'] = company_info.get('company_info', {})

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
def test_yahoo_finance_provider():
    """测试Yahoo Finance数据提供者"""
    if not YFINANCE_AVAILABLE:
        print("yfinance库未安装，无法测试")
        return

    provider = YahooFinanceProvider()

    # 测试股票代码
    test_symbols = ['AAPL', 'MSFT', 'GOOGL']

    for symbol in test_symbols:
        print(f"\n=== 测试 {symbol} ===")

        try:
            # 测试市场数据
            market_data = provider.get_market_data(symbol)
            print(f"市场数据: {market_data.get('status', 'unknown')}")
            if market_data.get('status') == 'success':
                price = market_data['market_data'].get('current_price', 0)
                print(f"当前价格: ${price:.2f}")

            # 测试公司信息
            company_info = provider.get_company_info(symbol)
            print(f"公司信息: {company_info.get('status', 'unknown')}")
            if company_info.get('status') == 'success':
                name = company_info['company_info'].get('name', 'Unknown')
                print(f"公司名称: {name}")

            # 等待一下避免速率限制
            time.sleep(1)

        except Exception as e:
            print(f"测试 {symbol} 时发生错误: {e}")


if __name__ == "__main__":
    # 设置日志
    logging.basicConfig(level=logging.INFO)

    # 运行测试
    test_yahoo_finance_provider()