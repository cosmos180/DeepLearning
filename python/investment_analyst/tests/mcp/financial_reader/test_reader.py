#!/usr/bin/env python3
"""
财报阅读MCP单元测试
"""

import unittest
from mcp.financial_reader.reader import FinancialReaderMCP


class TestFinancialReaderMCP(unittest.TestCase):
    """财报阅读MCP测试类"""

    def setUp(self):
        """测试初始化"""
        self.reader = FinancialReaderMCP()

    def test_init(self):
        """测试初始化"""
        self.assertIsInstance(self.reader.key_financial_metrics, list)
        self.assertIsInstance(self.reader.financial_ratios, dict)
        self.assertGreater(len(self.reader.key_financial_metrics), 0)
        self.assertGreater(len(self.reader.financial_ratios), 0)

    def test_extract_key_metrics(self):
        """测试提取关键指标"""
        # 模拟财务报表数据
        financial_statements = {
            "income_statement": {
                "revenue": 1000000,
                "gross_profit": 600000,
                "operating_income": 300000,
                "net_income": 200000,
                "eps": 2.5,
                "shares_outstanding": 100000,
            },
            "balance_sheet": {
                "total_assets": 2000000,
                "total_liabilities": 1200000,
                "total_equity": 800000,
                "cash_and_equivalents": 150000,
                "long_term_debt": 500000,
            },
            "cash_flow": {
                "operating_cash_flow": 250000,
                "investing_cash_flow": -100000,
                "financing_cash_flow": -50000,
            },
        }

        extracted_metrics = self.reader._extract_key_metrics(financial_statements)

        # 检查提取的指标
        self.assertEqual(extracted_metrics["revenue"], 1000000)
        self.assertEqual(extracted_metrics["gross_profit"], 600000)
        self.assertEqual(extracted_metrics["net_income"], 200000)
        self.assertEqual(extracted_metrics["total_assets"], 2000000)
        self.assertEqual(extracted_metrics["total_equity"], 800000)
        self.assertEqual(extracted_metrics["operating_cash_flow"], 250000)

    def test_calculate_financial_ratios(self):
        """测试计算财务比率"""
        # 模拟提取的数据
        extracted_data = {
            "revenue": 1000000.0,
            "gross_profit": 600000.0,
            "operating_income": 300000.0,
            "net_income": 200000.0,
            "total_assets": 2000000.0,
            "total_liabilities": 1200000.0,
            "total_equity": 800000.0,
            "operating_cash_flow": 250000.0,
            "investing_cash_flow": -100000.0,
        }

        calculated_ratios = self.reader._calculate_financial_ratios(extracted_data)

        # 检查计算的比率
        self.assertIn("gross_margin", calculated_ratios)
        self.assertIn("operating_margin", calculated_ratios)
        self.assertIn("net_margin", calculated_ratios)
        self.assertIn("debt_to_equity", calculated_ratios)
        self.assertIn("roe", calculated_ratios)
        self.assertIn("roa", calculated_ratios)
        self.assertIn("free_cash_flow", calculated_ratios)

        # 验证具体值
        self.assertEqual(calculated_ratios["gross_margin"], 0.6)  # 600000/1000000
        self.assertEqual(calculated_ratios["operating_margin"], 0.3)  # 300000/1000000
        self.assertEqual(calculated_ratios["net_margin"], 0.2)  # 200000/1000000
        self.assertEqual(calculated_ratios["debt_to_equity"], 1.5)  # 1200000/800000
        self.assertEqual(calculated_ratios["roe"], 0.25)  # 200000/800000
        self.assertEqual(calculated_ratios["roa"], 0.1)  # 200000/2000000
        self.assertEqual(
            calculated_ratios["free_cash_flow"], 150000
        )  # 250000 + (-100000)

    def test_normalize_data(self):
        """测试数据标准化"""
        # 模拟原始数据
        raw_data = {"revenue": 1000000, "company_name": "Test Corp", "is_public": True}

        normalized_data = self.reader._normalize_data(raw_data)

        # 检查标准化后的数据
        self.assertIsInstance(normalized_data["revenue"], float)
        self.assertEqual(normalized_data["revenue"], 1000000.0)
        self.assertEqual(normalized_data["company_name"], "Test Corp")
        self.assertEqual(normalized_data["is_public"], True)

    def test_get_extracted_metrics(self):
        """测试获取提取的指标列表"""
        metrics_list = self.reader.get_extracted_metrics()
        self.assertIsInstance(metrics_list, list)
        self.assertGreater(len(metrics_list), 0)

        # 检查是否包含关键指标
        self.assertIn("revenue", metrics_list)
        self.assertIn("gross_margin", metrics_list)
        self.assertIn("roe", metrics_list)

    def test_extract_financial_data(self):
        """测试提取财务数据"""
        # 模拟原始数据
        raw_data = {
            "stock_symbol": "TEST",
            "timestamp": "2023-01-01T00:00:00Z",
            "financial_statements": {
                "income_statement": {
                    "revenue": 1000000,
                    "gross_profit": 600000,
                    "operating_income": 300000,
                    "net_income": 200000,
                    "eps": 2.5,
                    "shares_outstanding": 100000,
                },
                "balance_sheet": {
                    "total_assets": 2000000,
                    "total_liabilities": 1200000,
                    "total_equity": 800000,
                    "cash_and_equivalents": 150000,
                    "long_term_debt": 500000,
                },
                "cash_flow": {
                    "operating_cash_flow": 250000,
                    "investing_cash_flow": -100000,
                    "financing_cash_flow": -50000,
                },
            },
        }

        result = self.reader.extract_financial_data(raw_data)

        # 检查返回结果结构
        self.assertIn("stock_symbol", result)
        self.assertIn("extracted_data", result)
        self.assertIn("calculated_ratios", result)
        self.assertIn("extraction_status", result)
        self.assertIn("timestamp", result)

        # 检查具体值
        self.assertEqual(result["stock_symbol"], "TEST")
        self.assertEqual(result["extraction_status"], "success")
        self.assertEqual(result["timestamp"], "2023-01-01T00:00:00Z")

        # 检查提取的数据
        extracted_data = result["extracted_data"]
        self.assertGreater(len(extracted_data), 0)
        self.assertIn("revenue", extracted_data)
        self.assertIn("net_income", extracted_data)

        # 检查计算的比率
        calculated_ratios = result["calculated_ratios"]
        self.assertGreater(len(calculated_ratios), 0)
        self.assertIn("gross_margin", calculated_ratios)
        self.assertIn("roe", calculated_ratios)


if __name__ == "__main__":
    unittest.main()
