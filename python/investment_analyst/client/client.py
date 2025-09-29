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
        report = "=== 投资分析报告 ===\n"
        report += f"股票代码: {result.get('stock_symbol', 'N/A')}\n"
        report += f"分析时间: {result.get('analysis_time', 'N/A')}\n"
        report += f"推荐评级: {result.get('rating', 'N/A')}\n"
        report += f"目标价格: {result.get('target_price', 'N/A')}\n"
        report += f"风险等级: {result.get('risk_level', 'N/A')}\n"
        report += "\n详细分析:\n"

        # 添加详细分析内容
        if "detailed_analysis" in result:
            for key, value in result["detailed_analysis"].items():
                report += f"{key}: {value}\n"

        return report
