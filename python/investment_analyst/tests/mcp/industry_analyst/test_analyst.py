"""
Author       : bughero bughero2012@gmail.com
Date         : 2025-09-29 12:02:17
LastEditors  : bughero bughero2012@gmail.com
LastEditTime : 2025-09-29 12:02:42
FilePath     : /DeepLearning/python/investment_analyst/tests/mcp/industry_analyst/test_analyst.py
Description  :

Copyright (c) 2025 by @Me, All Rights Reserved.
"""

#!/usr/bin/env python3
"""
顶级行业分析师MCP单元测试
"""

import unittest
from mcp.industry_analyst.analyst import IndustryAnalystMCP


class TestIndustryAnalystMCP(unittest.TestCase):
    """顶级行业分析师MCP测试类"""

    def setUp(self):
        """测试初始化"""
        self.analyst = IndustryAnalystMCP()

    def test_init(self):
        """测试初始化"""
        self.assertIsInstance(self.analyst.industry_categories, dict)
        self.assertIsInstance(self.analyst.industry_key_metrics, dict)
        self.assertGreater(len(self.analyst.industry_categories), 0)
        self.assertGreater(len(self.analyst.industry_key_metrics), 0)

    def test_determine_industry(self):
        """测试行业确定功能"""
        # 测试已知股票
        industry_info = self.analyst._determine_industry("AAPL")
        self.assertEqual(industry_info["category"], "technology")
        self.assertEqual(industry_info["subcategory"], "consumer_electronics")

        industry_info = self.analyst._determine_industry("JPM")
        self.assertEqual(industry_info["category"], "finance")
        self.assertEqual(industry_info["subcategory"], "banking")

        # 测试未知股票
        industry_info = self.analyst._determine_industry("UNKNOWN")
        self.assertEqual(industry_info["category"], "technology")
        self.assertEqual(industry_info["subcategory"], "general")

    def test_define_analysis_dimensions(self):
        """测试分析维度定义"""
        # 测试技术行业
        tech_info = {"category": "technology", "subcategory": "software"}
        dimensions = self.analyst._define_analysis_dimensions(tech_info)
        self.assertIn("financial_performance", dimensions)
        self.assertIn("innovation_capability", dimensions)
        self.assertIn("product_pipeline", dimensions)

        # 测试金融行业
        finance_info = {"category": "finance", "subcategory": "banking"}
        dimensions = self.analyst._define_analysis_dimensions(finance_info)
        self.assertIn("risk_management", dimensions)
        self.assertIn("regulatory_compliance", dimensions)

    def test_get_benchmark_companies(self):
        """测试获取对标公司"""
        # 测试技术行业
        tech_benchmarks = self.analyst._get_benchmark_companies("technology")
        self.assertIn("AAPL", tech_benchmarks)
        self.assertIn("MSFT", tech_benchmarks)

        # 测试金融行业
        finance_benchmarks = self.analyst._get_benchmark_companies("finance")
        self.assertIn("JPM", finance_benchmarks)
        self.assertIn("GS", finance_benchmarks)

        # 测试未知行业
        unknown_benchmarks = self.analyst._get_benchmark_companies("unknown")
        self.assertEqual(unknown_benchmarks, [])

    def test_analyze_industry(self):
        """测试行业分析"""
        result = self.analyst.analyze_industry("AAPL")

        # 检查返回结果结构
        self.assertIn("stock_symbol", result)
        self.assertIn("industry", result)
        self.assertIn("analysis_dimensions", result)
        self.assertIn("key_metrics", result)
        self.assertIn("benchmark_companies", result)

        # 检查具体值
        self.assertEqual(result["stock_symbol"], "AAPL")
        self.assertEqual(result["industry"]["category"], "technology")
        self.assertGreater(len(result["analysis_dimensions"]), 0)
        self.assertGreater(len(result["key_metrics"]), 0)
        self.assertGreater(len(result["benchmark_companies"]), 0)


if __name__ == "__main__":
    unittest.main()
