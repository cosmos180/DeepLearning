#!/usr/bin/env python3
"""
外部数据MCP单元测试
"""

import unittest
from mcp.external_data.external import ExternalDataMCP


class TestExternalDataMCP(unittest.TestCase):
    """外部数据MCP测试类"""

    def setUp(self):
        """测试初始化"""
        self.external_data = ExternalDataMCP()

    def test_init(self):
        """测试初始化"""
        self.assertIsInstance(self.external_data.industry_sources, dict)
        self.assertIsInstance(self.external_data.macro_indicators, list)
        self.assertIsInstance(self.external_data.peer_comparison_metrics, list)
        self.assertGreater(len(self.external_data.industry_sources), 0)
        self.assertGreater(len(self.external_data.macro_indicators), 0)
        self.assertGreater(len(self.external_data.peer_comparison_metrics), 0)

    def test_get_mock_industry_data(self):
        """测试获取模拟行业数据"""
        # 测试技术行业
        tech_data = self.external_data._get_mock_industry_data("technology", "software")
        self.assertIn("market_size", tech_data)
        self.assertIn("growth_rate", tech_data)
        self.assertIn("key_trends", tech_data)
        self.assertGreater(tech_data["market_size"], 0)
        self.assertGreater(len(tech_data["key_trends"]), 0)

        # 测试金融行业
        finance_data = self.external_data._get_mock_industry_data("finance", "banking")
        self.assertIn("market_size", finance_data)
        self.assertIn("regulatory_risk", finance_data)

        # 测试未知行业
        unknown_data = self.external_data._get_mock_industry_data("unknown", "general")
        self.assertIn("market_size", unknown_data)
        self.assertEqual(unknown_data["market_size"], 0)

    def test_get_mock_macro_data(self):
        """测试获取模拟宏观经济数据"""
        macro_data = self.external_data._get_mock_macro_data()
        self.assertIn("gdp_growth", macro_data)
        self.assertIn("inflation_rate", macro_data)
        self.assertIn("interest_rate", macro_data)
        self.assertIn("unemployment_rate", macro_data)
        self.assertIn("consumer_sentiment", macro_data)

        # 检查具体值
        self.assertGreaterEqual(macro_data["gdp_growth"], 0)
        self.assertGreaterEqual(macro_data["inflation_rate"], 0)
        self.assertGreaterEqual(macro_data["interest_rate"], 0)
        self.assertGreaterEqual(macro_data["unemployment_rate"], 0)

    def test_generate_peer_metrics(self):
        """测试生成同业指标"""
        # 测试为不同公司生成指标
        company_a_metrics = self.external_data._generate_peer_metrics(
            "COMPANY_A", "technology"
        )
        company_b_metrics = self.external_data._generate_peer_metrics(
            "COMPANY_B", "technology"
        )

        # 检查指标结构
        self.assertIn("revenue_growth", company_a_metrics)
        self.assertIn("gross_margin", company_a_metrics)
        self.assertIn("operating_margin", company_a_metrics)
        self.assertIn("net_margin", company_a_metrics)
        self.assertIn("market_share", company_a_metrics)
        self.assertIn("pe_ratio", company_a_metrics)
        self.assertIn("debt_to_equity", company_a_metrics)
        self.assertIn("roic", company_a_metrics)

        # 检查值范围
        self.assertGreaterEqual(company_a_metrics["revenue_growth"], 0.05)
        self.assertLessEqual(company_a_metrics["revenue_growth"], 0.15)
        self.assertGreaterEqual(company_a_metrics["gross_margin"], 0.35)
        self.assertLessEqual(company_a_metrics["gross_margin"], 0.55)

    def test_calculate_industry_percentiles(self):
        """测试计算行业百分位数"""
        # 模拟同业数据
        peer_data = {
            "COMPANY_A": {
                "revenue_growth": 0.10,
                "gross_margin": 0.45,
                "operating_margin": 0.20,
                "net_margin": 0.15,
            },
            "COMPANY_B": {
                "revenue_growth": 0.08,
                "gross_margin": 0.42,
                "operating_margin": 0.18,
                "net_margin": 0.12,
            },
        }

        percentiles = self.external_data._calculate_industry_percentiles(peer_data)

        # 检查返回结构
        self.assertIn("median", percentiles)
        self.assertIn("75th_percentile", percentiles)
        self.assertIn("25th_percentile", percentiles)

        # 检查具体指标
        median_data = percentiles["median"]
        self.assertIn("revenue_growth", median_data)
        self.assertIn("gross_margin", median_data)
        self.assertIn("operating_margin", median_data)
        self.assertIn("net_margin", median_data)

    def test_add_industry_source(self):
        """测试添加行业数据源"""
        # 添加新的行业数据源
        self.external_data.add_industry_source("test_industry", "Test Source")

        # 验证数据源已添加
        self.assertIn("test_industry", self.external_data.industry_sources)
        self.assertIn(
            "Test Source", self.external_data.industry_sources["test_industry"]
        )

        # 测试添加到新行业的数据源
        self.external_data.add_industry_source("new_industry", "New Source")
        self.assertIn("new_industry", self.external_data.industry_sources)
        self.assertIn("New Source", self.external_data.industry_sources["new_industry"])

    def test_get_available_indicators(self):
        """测试获取可用指标"""
        available_indicators = self.external_data.get_available_indicators()

        # 检查返回结构
        self.assertIn("macro_indicators", available_indicators)
        self.assertIn("peer_comparison_metrics", available_indicators)

        # 检查具体指标
        macro_indicators = available_indicators["macro_indicators"]
        peer_metrics = available_indicators["peer_comparison_metrics"]

        self.assertIsInstance(macro_indicators, list)
        self.assertIsInstance(peer_metrics, list)
        self.assertGreater(len(macro_indicators), 0)
        self.assertGreater(len(peer_metrics), 0)

        # 检查是否包含关键指标
        self.assertIn("gdp_growth", macro_indicators)
        self.assertIn("revenue_growth", peer_metrics)

    def test_get_external_data(self):
        """测试获取外部数据"""
        # 模拟行业分析结果
        industry_analysis = {
            "category": "technology",
            "subcategory": "software",
            "benchmark_companies": ["AAPL", "MSFT", "GOOGL"],
        }

        result = self.external_data.get_external_data("TEST", industry_analysis)

        # 检查返回结果结构
        self.assertIn("stock_symbol", result)
        self.assertIn("industry_data", result)
        self.assertIn("macro_economic_data", result)
        self.assertIn("peer_comparison_data", result)
        self.assertIn("timestamp", result)
        self.assertIn("status", result)

        # 检查具体值
        self.assertEqual(result["stock_symbol"], "TEST")
        self.assertEqual(result["status"], "success")
        self.assertGreater(len(result["timestamp"]), 0)

        # 检查各部分数据
        self.assertIn("market_size", result["industry_data"])
        self.assertIn("growth_rate", result["industry_data"])
        self.assertIn("key_trends", result["industry_data"])

        self.assertIn("gdp_growth", result["macro_economic_data"])
        self.assertIn("inflation_rate", result["macro_economic_data"])
        self.assertIn("interest_rate", result["macro_economic_data"])

        peer_comparison = result["peer_comparison_data"]
        self.assertIn("benchmark_companies", peer_comparison)
        self.assertIn("peer_metrics", peer_comparison)
        self.assertIn("industry_percentiles", peer_comparison)


if __name__ == "__main__":
    unittest.main()
