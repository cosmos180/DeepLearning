"""
Author       : bughero bughero2012@gmail.com
Date         : 2025-09-29 11:24:07
LastEditors  : bughero bughero2012@gmail.com
LastEditTime : 2025-09-29 11:24:18
FilePath     : /DeepLearning/python/investment_analyst/client/client.py
Description  :

Copyright (c) 2025 by @Me, All Rights Reserved.
"""

#!/usr/bin/env python3
"""
投资分析师客户端
"""

from workflow.orchestrator import WorkflowOrchestrator


class InvestmentClient:
    """投资分析师客户端类"""

    def __init__(self):
        """初始化客户端"""
        self.orchestrator = WorkflowOrchestrator()

    def run_analysis(self, stock_symbol: str) -> dict:
        """
        运行股票分析

        Args:
            stock_symbol (str): 股票代码

        Returns:
            dict: 分析结果
        """
        # 调用工作流协调器执行分析
        result = self.orchestrator.execute_analysis(stock_symbol)
        return result

    def get_analysis_report(self, stock_symbol: str) -> str:
        """
        获取分析报告

        Args:
            stock_symbol (str): 股票代码

        Returns:
            str: 分析报告内容
        """
        # 获取分析结果并生成报告
        result = self.run_analysis(stock_symbol)
        return self._format_report(result)

    def _format_report(self, result: dict) -> str:
        """
        格式化分析报告

        Args:
            result (dict): 分析结果

        Returns:
            str: 格式化的报告
        """
        report = []

        # 标题和基本信息
        report.append("=" * 80)
        report.append("📊 投资分析报告")
        report.append("=" * 80)
        report.append("")

        # 基本信息
        basic_info = [
            ("股票代码", result.get('stock_symbol', 'N/A')),
            ("分析时间", result.get('analysis_time', 'N/A')),
            ("执行时间", f"{result.get('execution_time', 0)*1000:.2f}ms"),
            ("推荐评级", self._format_rating(result.get('rating', 'N/A'))),
            ("目标价格", f"${result.get('target_price', 'N/A')}"),
            ("风险等级", self._format_risk_level(result.get('risk_analysis', {}).get('financial_risks', []))),
        ]

        report.append("📋 基本信息")
        report.append("-" * 40)
        report.append(self._format_table(basic_info, 2))
        report.append("")

        # 公司概览
        company_overview = result.get('executive_summary', {}).get('company_overview', {})
        if company_overview:
            company_info = [
                ("公司名称", company_overview.get('name', 'N/A')),
                ("当前价格", f"${company_overview.get('current_price', 0):.2f}" if company_overview.get('current_price') else 'N/A'),
                ("市值", self._format_currency(company_overview.get('market_cap', 0))),
            ]

            report.append("🏢 公司概览")
            report.append("-" * 40)
            report.append(self._format_table(company_info, 2))
            report.append("")

        # 财务分析
        financial_data = result.get('financial_analysis', {})
        if financial_data:
            report.append("💰 财务分析")
            report.append("-" * 40)

            # 损益表
            income_stmt = financial_data.get('income_statement', {})
            if income_stmt:
                income_data = [
                    ("营业收入", self._format_currency(income_stmt.get('revenue', 0))),
                    ("毛利润", self._format_currency(income_stmt.get('gross_profit', 0))),
                    ("营业利润", self._format_currency(income_stmt.get('operating_income', 0))),
                    ("净利润", self._format_currency(income_stmt.get('net_income', 0))),
                    ("每股收益", f"${income_stmt.get('eps', 0):.2f}"),
                    ("收入增长率", f"{income_stmt.get('revenue_growth', 0)*100:.1f}%"),
                ]

                report.append("📈 损益表")
                report.append(self._format_table(income_data, 2))
                report.append("")

            # 关键财务比率
            key_ratios = financial_data.get('key_ratios', {})
            if key_ratios:
                ratio_data = [
                    ("毛利率", f"{key_ratios.get('gross_margin', 0)*100:.1f}%"),
                    ("营业利润率", f"{key_ratios.get('operating_margin', 0)*100:.1f}%"),
                    ("净利润率", f"{key_ratios.get('net_margin', 0)*100:.1f}%"),
                    ("ROE", f"{key_ratios.get('roe', 0)*100:.1f}%"),
                    ("ROA", f"{key_ratios.get('roa', 0)*100:.1f}%"),
                    ("负债权益比", f"{key_ratios.get('debt_to_equity', 0):.2f}"),
                ]

                report.append("📊 关键财务比率")
                report.append(self._format_table(ratio_data, 2))
                report.append("")

        # 行业分析
        industry_data = result.get('industry_analysis', {})
        if industry_data:
            industry = industry_data.get('industry', {})
            industry_info = [
                ("行业类别", industry.get('category', 'N/A')),
                ("细分行业", industry.get('subcategory', 'N/A')),
                ("市场规模", self._format_currency(industry_data.get('market_position', {}).get('market_size', 0))),
                ("增长率", f"{industry_data.get('market_position', {}).get('growth_rate', 0)*100:.1f}%"),
            ]

            report.append("🏭 行业分析")
            report.append("-" * 40)
            report.append(self._format_table(industry_info, 2))
            report.append("")

        # 竞争对手对比
        competitive_data = result.get('industry_analysis', {}).get('competitive_landscape', {})
        if competitive_data and result.get('stock_symbol') in competitive_data:
            report.append("🏆 竞争对手对比")
            report.append("-" * 40)

            # 创建对比表格
            competitors = competitive_data.copy()
            symbol = result.get('stock_symbol')

            peer_comparison = []
            headers = ["指标", symbol] + [k for k in competitors.keys() if k != symbol]

            # 添加各项指标
            metrics = [
                ("收入增长率", "revenue_growth", "{:.1f}%"),
                ("毛利率", "gross_margin", "{:.1f}%"),
                ("营业利润率", "operating_margin", "{:.1f}%"),
                ("净利润率", "net_margin", "{:.1f}%"),
                ("PE比率", "pe_ratio", "{:.0f}"),
                ("负债权益比", "debt_to_equity", "{:.2f}"),
                ("投入资本回报率", "roic", "{:.1f}%"),
            ]

            for metric_name, metric_key, format_str in metrics:
                row = [metric_name]
                for company in [symbol] + [k for k in competitors.keys() if k != symbol]:
                    if company in competitors:
                        value = competitors[company].get(metric_key, 0)
                        if isinstance(value, (int, float)):
                            row.append(format_str.format(value * 100 if value < 1 else value))
                        else:
                            row.append(str(value))
                    else:
                        row.append("N/A")
                peer_comparison.append(row)

            report.append(self._format_table(peer_comparison, headers=headers))
            report.append("")

        # 投资建议
        executive_summary = result.get('executive_summary', {})
        if executive_summary:
            investment_thesis = executive_summary.get('investment_thesis', [])
            key_risks = executive_summary.get('key_risks', [])
            recommendation = executive_summary.get('recommendation', '')

            report.append("💡 投资建议")
            report.append("-" * 40)
            if recommendation:
                report.append(f"📌 {recommendation}")
                report.append("")

            if investment_thesis:
                report.append("✅ 投资亮点:")
                for point in investment_thesis:
                    report.append(f"   • {point}")
                report.append("")

            if key_risks:
                report.append("⚠️ 主要风险:")
                for risk in key_risks:
                    report.append(f"   • {risk}")
                report.append("")

        # 风险分析
        risk_analysis = result.get('risk_analysis', {})
        if risk_analysis:
            report.append("⚠️ 风险分析")
            report.append("-" * 40)

            business_risks = risk_analysis.get('business_risks', [])
            financial_risks = risk_analysis.get('financial_risks', [])
            market_risks = risk_analysis.get('market_risks', [])

            if business_risks:
                report.append("🏢 业务风险:")
                for risk in business_risks:
                    report.append(f"   • {risk}")
                report.append("")

            if financial_risks:
                report.append("💰 财务风险:")
                for risk in financial_risks:
                    report.append(f"   • {risk}")
                report.append("")

            if market_risks:
                report.append("📈 市场风险:")
                for risk in market_risks:
                    report.append(f"   • {risk}")
                report.append("")

        # 展望
        outlook = result.get('outlook', {})
        if outlook:
            report.append("🔮 未来展望")
            report.append("-" * 40)

            growth_drivers = outlook.get('growth_drivers', [])
            catalysts = outlook.get('catalysts', [])

            if growth_drivers:
                report.append("🚀 增长动力:")
                for driver in growth_drivers:
                    report.append(f"   • {driver}")
                report.append("")

            if catalysts:
                report.append("⚡ 催化因素:")
                for catalyst in catalysts:
                    report.append(f"   • {catalyst}")
                report.append("")

        # 数据来源
        source_data = result.get('source_data', {})
        if source_data:
            report.append("📋 数据来源")
            report.append("-" * 40)
            report.append(f"财务数据: {source_data.get('financial_data', {}).get('validation_status', 'N/A')}")
            report.append(f"外部数据: {source_data.get('external_data', {}).get('status', 'N/A')}")
            report.append("")

        report.append("=" * 80)
        report.append("报告生成完成")
        report.append("=" * 80)

        return "\n".join(report)

    def _format_table(self, data, indent=0, headers=None):
        """格式化表格"""
        if not data:
            return "无数据"

        # 确定列宽
        if headers:
            max_widths = [len(str(h)) for h in headers]
            for row in data:
                for i, cell in enumerate(row):
                    if i < len(max_widths):
                        max_widths[i] = max(max_widths[i], len(str(cell)))
        else:
            # 两列格式
            max_widths = [0, 0]
            for key, value in data:
                max_widths[0] = max(max_widths[0], len(str(key)))
                max_widths[1] = max(max_widths[1], len(str(value)))

        # 构建表格
        lines = []
        indent_str = " " * indent

        if headers:
            # 添加表头
            header_line = indent_str + " | ".join(
                f"{h:<{max_widths[i]}}" for i, h in enumerate(headers)
            )
            lines.append(header_line)
            lines.append(indent_str + "-" * len(header_line))

        # 添加数据行
        if headers:
            for row in data:
                line = indent_str + " | ".join(
                    f"{str(row[i]) if i < len(row) else '':<{max_widths[i]}}"
                    for i in range(len(max_widths))
                )
                lines.append(line)
        else:
            for key, value in data:
                line = indent_str + f"{str(key):<{max_widths[0]}} | {str(value):<{max_widths[1]}}"
                lines.append(line)

        return "\n".join(lines)

    def _format_currency(self, amount):
        """格式化货币"""
        if amount >= 1e12:
            return f"${amount/1e12:.1f}T"
        elif amount >= 1e9:
            return f"${amount/1e9:.1f}B"
        elif amount >= 1e6:
            return f"${amount/1e6:.1f}M"
        elif amount >= 1e3:
            return f"${amount/1e3:.1f}K"
        else:
            return f"${amount:.2f}"

    def _format_rating(self, rating):
        """格式化评级"""
        rating_map = {
            'buy': '🟢 买入',
            'hold': '🟡 持有',
            'sell': '🔴 卖出',
            'strong_buy': '🚀 强烈买入',
            'strong_sell': '💣 强烈卖出',
        }
        return rating_map.get(rating.lower(), rating)

    def _format_risk_level(self, risks):
        """格式化风险等级"""
        if not risks:
            return "🟢 低风险"
        elif len(risks) <= 2:
            return "🟡 中风险"
        else:
            return "🔴 高风险"
