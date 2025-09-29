#!/usr/bin/env python3
"""
指标对齐MCP单元测试
"""

import unittest
from mcp.indicator_alignment.aligner import IndicatorAlignmentMCP


class TestIndicatorAlignmentMCP(unittest.TestCase):
    """指标对齐MCP测试类"""

    def setUp(self):
        """测试初始化"""
        self.aligner = IndicatorAlignmentMCP()

    def test_init(self):
        """测试初始化"""
        self.assertIsInstance(self.aligner.financial_mapping_rules, dict)
        self.assertIsInstance(self.aligner.unit_conversion_rules, dict)
        self.assertGreater(len(self.aligner.financial_mapping_rules), 0)
        self.assertGreater(len(self.aligner.unit_conversion_rules), 0)

    def test_determine_unit_conversion(self):
        """测试单位转换确定"""
        # 测试货币类指标
        currency_conversion = self.aligner._determine_unit_conversion("revenue")
        self.assertEqual(currency_conversion["default_unit"], "millions")
        self.assertEqual(currency_conversion["conversion_factor"], 1000000)

        # 测试百分比类指标
        percent_conversion = self.aligner._determine_unit_conversion("gross_margin")
        self.assertEqual(percent_conversion["default_unit"], "percent")
        self.assertEqual(percent_conversion["conversion_factor"], 0.01)

        # 测试其他类型指标
        other_conversion = self.aligner._determine_unit_conversion("shares_outstanding")
        self.assertEqual(other_conversion["default_unit"], "unit")
        self.assertEqual(other_conversion["conversion_factor"], 1)

    def test_define_validation_rules(self):
        """测试验证规则定义"""
        # 测试利润率类指标
        margin_rules = self.aligner._define_validation_rules("gross_margin")
        self.assertEqual(margin_rules["min_value"], -1.0)
        self.assertEqual(margin_rules["max_value"], 5.0)
        self.assertEqual(margin_rules["data_type"], "float")

        # 测试债务比率类指标
        debt_rules = self.aligner._define_validation_rules("debt_to_equity")
        self.assertEqual(debt_rules["min_value"], 0.0)
        self.assertEqual(debt_rules["max_value"], 10.0)

        # 测试收入增长类指标
        growth_rules = self.aligner._define_validation_rules("revenue_growth")
        self.assertEqual(growth_rules["min_value"], -1.0)
        self.assertEqual(growth_rules["max_value"], 10.0)

    def test_add_mapping_rule(self):
        """测试添加映射规则"""
        # 添加新的映射规则
        self.aligner.add_mapping_rule("test_metric", ["alternative1", "alternative2"])

        # 验证规则已添加
        rule = self.aligner.get_mapping_rule("test_metric")
        self.assertIn("alternative1", rule)
        self.assertIn("alternative2", rule)

    def test_get_mapping_rule(self):
        """测试获取映射规则"""
        # 测试获取已存在的规则
        revenue_rules = self.aligner.get_mapping_rule("revenue")
        self.assertIn("total_revenue", revenue_rules)
        self.assertIn("sales", revenue_rules)

        # 测试获取不存在的规则
        unknown_rules = self.aligner.get_mapping_rule("unknown_metric")
        self.assertEqual(unknown_rules, ["unknown_metric"])

    def test_align_indicators(self):
        """测试指标对齐"""
        # 模拟行业分析结果
        industry_analysis = {
            "industry": {"category": "technology", "subcategory": "software"},
            "key_metrics": ["revenue", "gross_margin", "roe"],
        }

        result = self.aligner.align_indicators(industry_analysis)

        # 检查返回结果结构
        self.assertIn("industry", result)
        self.assertIn("aligned_indicators", result)
        self.assertIn("mapping_rules", result)
        self.assertIn("unit_rules", result)

        # 检查对齐的指标
        aligned_indicators = result["aligned_indicators"]
        self.assertIn("revenue", aligned_indicators)
        self.assertIn("gross_margin", aligned_indicators)
        self.assertIn("roe", aligned_indicators)

        # 检查每个指标的结构
        for metric in ["revenue", "gross_margin", "roe"]:
            self.assertIn("possible_names", aligned_indicators[metric])
            self.assertIn("unit_conversion", aligned_indicators[metric])
            self.assertIn("validation_rules", aligned_indicators[metric])


if __name__ == "__main__":
    unittest.main()
