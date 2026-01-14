"""
DCF模型单元测试 - 测试核心计算正确性
"""

import unittest
import sys
import os

# 添加路径以便导入模块
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dcf_revised import (
    DCFParameters, DCFResults, WACCCalculator,
    FCForecaster, DCFModel, SensitivityAnalyzer,
    RelativeValuation, ValuationOrchestrator,
    create_tencent_template, create_apple_template,
)

class TestWACCCalculator(unittest.TestCase):
    """测试WACC计算器"""

    def test_basic_wacc_calculation(self):
        """测试基本WACC计算"""
        params = DCFParameters(
            risk_free_rate=0.03,
            market_risk_premium=0.06,
            beta=1.2,
            cost_of_debt=0.04,
            tax_rate=0.25,
            equity_weight=0.8,
            debt_weight=0.2
        )

        wacc = WACCCalculator.calculate(params)

        # 手动计算验证：
        # ke = 0.03 + 1.2 * 0.06 = 0.102
        # kd_after_tax = 0.04 * (1 - 0.25) = 0.03
        # wacc = 0.8 * 0.102 + 0.2 * 0.03 = 0.0876
        self.assertAlmostEqual(wacc, 0.0876, places=3)

    def test_tencent_wacc(self):
        """测试腾讯WACC计算是否匹配原版结果"""
        params = create_tencent_template()
        wacc = WACCCalculator.calculate(params)

        # 原版结果：9.30%
        self.assertAlmostEqual(wacc, 0.0930, places=3)


class TestFCForecaster(unittest.TestCase):
    """测试FCF预测器"""

    def test_basic_forecast(self):
        """测试基本预测功能"""
        params = DCFParameters(
            revenue_0=1000,
            forecast_years=3,
            revenue_growth_rates=[0.10, 0.08, 0.06],
            fcf_margins=[0.25, 0.26, 0.27]
        )

        revenue, fcf = FCForecaster().forecast(params)

        # 第1年：营收 = 1000 * 1.10 = 1100，FCF = 1100 * 0.25 = 275
        self.assertAlmostEqual(revenue[0], 1100.0, places=2)
        self.assertAlmostEqual(fcf[0], 275.0, places=2)

        # 第2年：营收 = 1100 * 1.08 = 1188，FCF = 1188 * 0.26 = 308.88
        self.assertAlmostEqual(revenue[1], 1188.0, places=2)

    def test_default_forecast(self):
        """测试默认预测参数"""
        params = DCFParameters(
            revenue_0=1000,
            forecast_years=3
        )

        revenue, fcf = FCForecaster().forecast(params)

        # 应该使用默认增长率和利润率
        self.assertEqual(len(revenue), 3)
        self.assertEqual(len(fcf), 3)
        self.assertGreater(revenue[0], 0)
        self.assertGreater(fcf[0], 0)


class TestDCFModel(unittest.TestCase):
    """测试核心DCF模型"""

    def test_tencent_valuation(self):
        """测试腾讯估值并验证修复的BUG"""
        params = create_tencent_template()

        results = DCFModel.calculate(params)

        # 验证结果类型
        self.assertIsInstance(results, DCFResults)
        self.assertGreater(results.per_share_value, 0)
        self.assertGreater(results.enterprise_value, 0)
        self.assertGreater(results.equity_value, 0)

        # 验证股权价值计算正确
        # 腾讯：net_debt = -1024（净现金）
        # 正确公式：Equity Value = EV - (-1024) = EV + 1024
        expected_equity_value = results.enterprise_value + 1024.0 + 8000.0
        self.assertAlmostEqual(
            results.equity_value,
            expected_equity_value,
            places=2,
            msg="股权价值计算错误：净现金应该增加股权价值"
        )

        # 验证原版结果：DCF每股价值 557.83 CNY（原版）
        # 修正后结果：579.38 CNY（增值约21.55元，因为正确加上了净现金）
        self.assertAlmostEqual(results.per_share_value, 579.38, places=2)

    def test_enterprise_value_composition(self):
        """验证企业价值构成"""
        params = DCFParameters(
            revenue_0=1000,
            forecast_years=5,
            revenue_growth_rates=[0.10] * 5,
            fcf_margins=[0.25] * 5,
            perpetual_growth_rate=0.03,
            net_debt=0,
            investment_value=0,
            shares_outstanding=1,
            risk_free_rate=0.03,
            market_risk_premium=0.06,
            beta=1.0,
            cost_of_debt=0.04,
            equity_weight=1.0,
            debt_weight=0.0
        )

        results = DCFModel.calculate(params)

        # 企业价值 = 预测期现值 + 终值现值
        self.assertAlmostEqual(
            results.enterprise_value,
            results.pv_forecast + results.pv_terminal,
            places=2
        )

        # 终值占比
        self.assertGreater(results.terminal_share, 0)
        self.assertLess(results.terminal_share, 100)


class TestRelativeValuation(unittest.TestCase):
    """测试相对估值"""

    def test_pe_valuation(self):
        """测试PE估值法"""
        params = create_tencent_template()

        peers = [{'name': '行业平均', 'pe_ratio': 18, 'ev_ebitda_ratio': 12}]
        results = RelativeValuation.calculate(params, peers, current_price=400)

        self.assertIn('pe_valuation', results)
        self.assertIn('ev_ebitda_valuation', results)
        self.assertIn('current_price', results)

        # 应该计算折让/溢价
        self.assertIn('average_relative_value', results)
        self.assertIn('discount_to_relative', results)


class TestValuationOrchestrator(unittest.TestCase):
    """测试估值协调器"""

    def test_full_workflow(self):
        """测试完整工作流程"""
        params = create_tencent_template()
        orchestrator = ValuationOrchestrator(params)

        # 1. 运行DCF
        results = orchestrator.run_dcf()
        self.assertIsInstance(results, DCFResults)

        # 2. 运行敏感性分析
        sensitivity = orchestrator.run_sensitivity_analysis()
        self.assertIn('wacc_growth_matrix', sensitivity)

        # 3. 运行相对估值
        relative = orchestrator.run_relative_valuation(current_price=400)
        self.assertIn('pe_valuation', relative)
        self.assertIn('ev_ebitda_valuation', relative)

        # 4. 生成报告
        report = orchestrator.generate_report('text')
        self.assertIsInstance(report, str)
        self.assertIn('腾讯控股 DCF估值报告', report)
        self.assertIn('企业价值', report)

    def test_config_save_load(self):
        """测试配置保存和加载"""
        params = create_tencent_template()
        orchestrator = ValuationOrchestrator(params)

        # 保存配置
        config_file = 'test_config.json'
        orchestrator.save_config(config_file, format='json')

        # 验证文件存在
        import os
        self.assertTrue(os.path.exists(config_file))

        # 加载配置
        loaded_orchestrator = ValuationOrchestrator.load_config(config_file, format='json')

        # 验证加载的参数
        self.assertEqual(loaded_orchestrator.params.company_name, params.company_name)
        self.assertEqual(loaded_orchestrator.params.revenue_0, params.revenue_0)

        # 清理
        os.remove(config_file)


class TestEdgeCases(unittest.TestCase):
    """测试边界情况"""

    def test_high_growth_low_margin(self):
        """测试高增长低利润率场景"""
        params = DCFParameters(
            revenue_0=1000,
            forecast_years=3,
            revenue_growth_rates=[0.50, 0.40, 0.30],  # 高增长
            fcf_margins=[0.05, 0.06, 0.07],           # 低利润率
            perpetual_growth_rate=0.05,
            net_debt=0,
            shares_outstanding=1
        )

        results = DCFModel.calculate(params)
        self.assertGreater(results.per_share_value, 0)

    def test_negative_net_debt(self):
        """测试净现金情况"""
        params = DCFParameters(
            revenue_0=1000,
            forecast_years=3,
            net_debt=-500,  # 净现金500
            shares_outstanding=1
        )

        results = DCFModel.calculate(params)

        # 股权价值应该大于企业价值（因为净现金）
        self.assertGreater(results.equity_value, results.enterprise_value)


# ============================================================================
# 运行测试
# ============================================================================

if __name__ == '__main__':
    print("="*70)
    print("运行DCF模型单元测试")
    print("="*70)

    unittest.main(verbosity=2)
