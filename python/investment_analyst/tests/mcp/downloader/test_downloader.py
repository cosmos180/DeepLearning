#!/usr/bin/env python3
"""
下载MCP单元测试
"""

import unittest
from mcp.downloader.downloader import DownloadMCP


class TestDownloadMCP(unittest.TestCase):
    """下载MCP测试类"""

    def setUp(self):
        """测试初始化"""
        self.downloader = DownloadMCP()

    def test_init(self):
        """测试初始化"""
        self.assertIsInstance(self.downloader.data_sources, dict)
        self.assertIsInstance(self.downloader.api_keys, dict)
        self.assertGreater(len(self.downloader.data_sources), 0)
        self.assertGreater(len(self.downloader.api_keys), 0)

    def test_get_mock_financial_data(self):
        """测试获取模拟财务数据"""
        # 测试已知股票
        apple_data = self.downloader._get_mock_financial_data("AAPL")
        self.assertIn("income_statement", apple_data)
        self.assertIn("balance_sheet", apple_data)
        self.assertIn("cash_flow", apple_data)

        # 检查收入数据
        income_stmt = apple_data["income_statement"]
        self.assertIn("revenue", income_stmt)
        self.assertIn("net_income", income_stmt)
        self.assertGreater(income_stmt["revenue"], 0)

        # 测试未知股票
        unknown_data = self.downloader._get_mock_financial_data("UNKNOWN")
        self.assertIn("income_statement", unknown_data)
        self.assertIn("balance_sheet", unknown_data)
        self.assertIn("cash_flow", unknown_data)

    def test_get_mock_industry_data(self):
        """测试获取模拟行业数据"""
        industry_data = self.downloader._get_mock_industry_data("AAPL")
        self.assertIn("industry_pe", industry_data)
        self.assertIn("sector", industry_data)
        self.assertIn("sub_sector", industry_data)
        self.assertGreater(industry_data["industry_pe"], 0)

    def test_get_mock_market_data(self):
        """测试获取模拟市场数据"""
        market_data = self.downloader._get_mock_market_data("AAPL")
        self.assertIn("current_price", market_data)
        self.assertIn("market_cap", market_data)
        self.assertIn("volume", market_data)
        self.assertGreater(market_data["current_price"], 0)

    def test_get_mock_macro_data(self):
        """测试获取模拟宏观经济数据"""
        macro_data = self.downloader._get_mock_macro_data()
        self.assertIn("gdp_growth", macro_data)
        self.assertIn("inflation_rate", macro_data)
        self.assertIn("interest_rate", macro_data)

    def test_add_data_source(self):
        """测试添加数据源"""
        # 添加新的数据源
        self.downloader.add_data_source(
            "test_source", "https://api.test.com/data", "TEST_KEY"
        )

        # 验证数据源已添加
        source_url = self.downloader.get_data_source("test_source")
        self.assertEqual(source_url, "https://api.test.com/data")

    def test_get_data_source(self):
        """测试获取数据源"""
        # 测试获取已存在的数据源
        financial_url = self.downloader.get_data_source("financial_statements")
        self.assertEqual(financial_url, "https://api.financial-data.com/statements")

        # 测试获取不存在的数据源
        unknown_url = self.downloader.get_data_source("unknown_source")
        self.assertEqual(unknown_url, "")

    def test_download_data(self):
        """测试下载数据"""
        # 模拟对齐的指标
        aligned_indicators = {
            "industry": {"category": "technology"},
            "aligned_indicators": {
                "revenue": {"possible_names": ["revenue", "sales"]},
                "net_income": {"possible_names": ["net_income", "net_profit"]},
            },
        }

        result = self.downloader.download_data("AAPL", aligned_indicators)

        # 检查返回结果结构
        self.assertIn("stock_symbol", result)
        self.assertIn("timestamp", result)
        self.assertIn("financial_statements", result)
        self.assertIn("industry_data", result)
        self.assertIn("market_data", result)
        self.assertIn("macro_economic_data", result)
        self.assertIn("status", result)

        # 检查具体值
        self.assertEqual(result["stock_symbol"], "AAPL")
        self.assertEqual(result["status"], "success")
        self.assertGreater(len(result["timestamp"]), 0)

        # 检查各部分数据
        self.assertIn("income_statement", result["financial_statements"])
        self.assertIn("balance_sheet", result["financial_statements"])
        self.assertIn("cash_flow", result["financial_statements"])

        self.assertIn("industry_pe", result["industry_data"])
        self.assertIn("sector", result["industry_data"])

        self.assertIn("current_price", result["market_data"])
        self.assertIn("market_cap", result["market_data"])

        self.assertIn("gdp_growth", result["macro_economic_data"])
        self.assertIn("inflation_rate", result["macro_economic_data"])


if __name__ == "__main__":
    unittest.main()
