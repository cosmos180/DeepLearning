#!/usr/bin/env python3
"""
数据整理MCP单元测试
"""

import unittest
from mcp.report_generator.generator import ReportGeneratorMCP


class TestReportGeneratorMCP(unittest.TestCase):
    """数据整理MCP测试类"""

    def setUp(self):
        """测试初始化"""
        self.generator = ReportGeneratorMCP()

    def test_init(self):
        """测试初始化"""
        self.assertIsInstance(self.generator.report_structure, dict)
        self.assertIsInstance(self.generator.rating_scale, dict)
        self.assertGreater(len(self.generator.report_structure), 0)
        self.assertGreater(len(self.generator.rating_scale), 0)

    def test_get_company_name(self):
        """测试获取公司名称"""
        # 测试已知股票
        apple_name = self.generator._get_company_name("AAPL")
        self.assertEqual(apple_name, "Apple Inc.")

        microsoft_name = self.generator._get_company_name("MSFT")
        self.assertEqual(microsoft_name, "Microsoft Corporation")

        # 测试未知股票
        unknown_name = self.generator._get_company_name("UNKNOWN")
        self.assertEqual(unknown_name, "UNKNOWN Corporation")

    def test_derive_investment_thesis(self):
        """测试推导投资论点"""
        # 模拟财务数据和行业数据
        financial_data = {
            "roe": 0.20,  # 20%
            "revenue_growth": 0.15,  # 15%
            "free_cash_flow": 1000000,
        }

        industry_data = {"growth_rate": 0.10}  # 10%

        thesis_points = self.generator._derive_investment_thesis(
            financial_data, industry_data
        )

        # 检查论点内容
        self.assertIsInstance(thesis_points, list)
        self.assertGreater(len(thesis_points), 0)

        # 检查是否包含预期的论点
        self.assertIn("高股东回报率，显示良好的资本配置能力", thesis_points)
        self.assertIn("收入增长超越行业平均水平", thesis_points)
        self.assertIn("正自由现金流，显示健康的经营状况", thesis_points)

    def test_identify_key_risks(self):
        """测试识别主要风险"""
        # 模拟财务数据和行业数据
        financial_data = {"debt_to_equity": 1.5}

        industry_data = {"regulatory_risk": "high"}

        risks = self.generator._identify_key_risks(financial_data, industry_data)

        # 检查风险内容
        self.assertIsInstance(risks, list)
        self.assertGreater(len(risks), 0)

        # 检查是否包含预期的风险
        self.assertIn("高负债率可能增加财务风险", risks)
        self.assertIn("行业监管风险较高", risks)

    def test_formulate_recommendation(self):
        """测试制定推荐建议"""
        # 模拟财务数据和同业对比数据
        financial_data = {"roe": 0.20, "net_margin": 0.15}  # 20%  # 15%

        peer_comparison = {}  # 简化处理

        recommendation = self.generator._formulate_recommendation(
            financial_data, peer_comparison
        )

        # 检查推荐建议
        self.assertIsInstance(recommendation, str)
        self.assertGreater(len(recommendation), 0)
        self.assertIn("强烈推荐买入", recommendation)

    def test_calculate_rating_and_target_price(self):
        """测试计算投资评级和目标价格"""
        # 模拟数据
        financial_data = {
            "roe": 0.20,  # 20%
            "debt_to_equity": 0.3,
            "revenue_growth": 0.15,  # 15%
            "current_price": 150.0,
        }

        peer_comparison = {}  # 简化处理
        industry_data = {}  # 简化处理

        rating, target_price = self.generator._calculate_rating_and_target_price(
            financial_data, peer_comparison, industry_data
        )

        # 检查评级和目标价格
        self.assertIn(rating, ["strong_buy", "buy", "hold", "sell"])
        self.assertIsInstance(target_price, (int, float))
        self.assertGreater(target_price, 0)

    def test_get_rating_description(self):
        """测试获取评级描述"""
        # 测试已知评级
        strong_buy_desc = self.generator.get_rating_description("strong_buy")
        self.assertEqual(strong_buy_desc, "强烈买入")

        buy_desc = self.generator.get_rating_description("buy")
        self.assertEqual(buy_desc, "买入")

        # 测试未知评级
        unknown_desc = self.generator.get_rating_description("unknown_rating")
        self.assertEqual(unknown_desc, "未知")

    def test_format_report_output(self):
        """测试格式化报告输出"""
        # 模拟报告数据
        report_data = {
            "rating": "strong_buy",
            "target_price": 200.0,
            "executive_summary": {"company_overview": {"name": "Test Company"}},
            "financial_analysis": {
                "income_statement": {"revenue": 1000000000},
                "key_ratios": {"net_margin": 0.15, "roe": 0.20},
            },
        }

        formatted_output = self.generator.format_report_output(report_data)

        # 检查格式化输出
        self.assertIsInstance(formatted_output, str)
        self.assertGreater(len(formatted_output), 0)
        self.assertIn("投资分析报告", formatted_output)
        self.assertIn("Test Company", formatted_output)
        self.assertIn("强烈买入", formatted_output)
        self.assertIn("200.00", formatted_output)

    def test_generate_executive_summary(self):
        """测试生成执行摘要"""
        # 模拟数据
        stock_symbol = "TEST"
        financial_data = {"current_price": 150.0, "market_cap": 1000000000}

        peer_comparison = {}
        industry_data = {}

        exec_summary = self.generator._generate_executive_summary(
            stock_symbol, financial_data, peer_comparison, industry_data
        )

        # 检查执行摘要结构
        self.assertIn("company_overview", exec_summary)
        self.assertIn("investment_thesis", exec_summary)
        self.assertIn("key_risks", exec_summary)
        self.assertIn("recommendation", exec_summary)

        # 检查公司概览
        company_overview = exec_summary["company_overview"]
        self.assertEqual(company_overview["symbol"], "TEST")
        self.assertEqual(company_overview["current_price"], 150.0)

    def test_generate_report(self):
        """测试生成报告"""
        # 模拟数据
        stock_symbol = "TEST"

        financial_data = {
            "validated_data": {
                "revenue": 1000000000,
                "net_income": 200000000,
                "total_assets": 2000000000,
                "total_equity": 1000000000,
                "roe": 0.20,
                "net_margin": 0.20,
                "current_price": 150.0,
                "market_cap": 1000000000,
            }
        }

        external_data = {
            "peer_comparison_data": {},
            "industry_data": {"market_size": 5000000000000, "growth_rate": 0.10},
            "macro_economic_data": {"gdp_growth": 0.03, "inflation_rate": 0.02},
        }

        industry_analysis = {"category": "technology", "subcategory": "software"}

        result = self.generator.generate_report(
            stock_symbol, financial_data, external_data, industry_analysis
        )

        # 检查返回结果结构
        self.assertIn("stock_symbol", result)
        self.assertIn("company_name", result)
        self.assertIn("report_date", result)
        self.assertIn("executive_summary", result)
        self.assertIn("financial_analysis", result)
        self.assertIn("industry_analysis", result)
        self.assertIn("valuation_analysis", result)
        self.assertIn("risk_analysis", result)
        self.assertIn("outlook", result)
        self.assertIn("rating", result)
        self.assertIn("target_price", result)
        self.assertIn("status", result)

        # 检查具体值
        self.assertEqual(result["stock_symbol"], "TEST")
        self.assertEqual(result["status"], "success")
        self.assertGreater(len(result["report_date"]), 0)
        self.assertIn(result["rating"], ["strong_buy", "buy", "hold", "sell"])
        self.assertGreater(result["target_price"], 0)


if __name__ == "__main__":
    unittest.main()
