#!/usr/bin/env python3
"""
财报阅读MCP
负责从原始数据中提取关键指标
"""

from typing import Dict, Any, List
import pandas as pd


class FinancialReaderMCP:
    """财报阅读MCP类"""

    def __init__(self):
        """初始化财报阅读MCP"""
        # 定义需要提取的关键指标
        self.key_financial_metrics = [
            "revenue",
            "gross_profit",
            "operating_income",
            "net_income",
            "eps",
            "total_assets",
            "total_liabilities",
            "total_equity",
            "cash_and_equivalents",
            "long_term_debt",
            "operating_cash_flow",
            "investing_cash_flow",
            "financing_cash_flow",
            "shares_outstanding",
        ]

        # 定义财务比率计算公式
        self.financial_ratios = {
            "gross_margin": lambda data: (
                data.get("gross_profit", 0) / data.get("revenue", 1)
                if data.get("revenue", 0) != 0
                else 0
            ),
            "operating_margin": lambda data: (
                data.get("operating_income", 0) / data.get("revenue", 1)
                if data.get("revenue", 0) != 0
                else 0
            ),
            "net_margin": lambda data: (
                data.get("net_income", 0) / data.get("revenue", 1)
                if data.get("revenue", 0) != 0
                else 0
            ),
            "debt_to_equity": lambda data: (
                data.get("total_liabilities", 0) / data.get("total_equity", 1)
                if data.get("total_equity", 0) != 0
                else 0
            ),
            "current_ratio": lambda data: (
                data.get("total_assets", 0) / data.get("total_liabilities", 1)
                if data.get("total_liabilities", 0) != 0
                else 0
            ),
            "roe": lambda data: (
                data.get("net_income", 0) / data.get("total_equity", 1)
                if data.get("total_equity", 0) != 0
                else 0
            ),
            "roa": lambda data: (
                data.get("net_income", 0) / data.get("total_assets", 1)
                if data.get("total_assets", 0) != 0
                else 0
            ),
            "free_cash_flow": lambda data: data.get("operating_cash_flow", 0)
            + data.get("investing_cash_flow", 0),
        }

    def extract_financial_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        从原始数据中提取财务指标

        Args:
            raw_data (Dict[str, Any]): 原始数据

        Returns:
            Dict[str, Any]: 提取的财务数据
        """
        try:
            # 获取财务报表数据
            financial_statements = raw_data.get("financial_statements", {})

            # 提取关键财务指标
            extracted_data = self._extract_key_metrics(financial_statements)

            # 计算财务比率
            calculated_ratios = self._calculate_financial_ratios(extracted_data)

            # 合并数据
            extracted_data.update(calculated_ratios)

            return {
                "stock_symbol": raw_data.get("stock_symbol", ""),
                "extracted_data": extracted_data,
                "calculated_ratios": calculated_ratios,
                "extraction_status": "success",
                "timestamp": raw_data.get("timestamp", ""),
            }

        except Exception as e:
            return {
                "stock_symbol": raw_data.get("stock_symbol", ""),
                "error": str(e),
                "extraction_status": "failed",
                "timestamp": raw_data.get("timestamp", ""),
            }

    def _extract_key_metrics(
        self, financial_statements: Dict[str, Any]
    ) -> Dict[str, float]:
        """
        提取关键财务指标

        Args:
            financial_statements (Dict[str, Any]): 财务报表数据

        Returns:
            Dict[str, float]: 提取的关键指标
        """
        extracted_metrics = {}

        # 从损益表提取数据
        income_statement = financial_statements.get("income_statement", {})
        for metric in [
            "revenue",
            "gross_profit",
            "operating_income",
            "net_income",
            "eps",
            "shares_outstanding",
        ]:
            extracted_metrics[metric] = income_statement.get(metric, 0.0)

        # 从资产负债表提取数据
        balance_sheet = financial_statements.get("balance_sheet", {})
        for metric in [
            "total_assets",
            "total_liabilities",
            "total_equity",
            "cash_and_equivalents",
            "long_term_debt",
        ]:
            extracted_metrics[metric] = balance_sheet.get(metric, 0.0)

        # 从现金流量表提取数据
        cash_flow = financial_statements.get("cash_flow", {})
        for metric in [
            "operating_cash_flow",
            "investing_cash_flow",
            "financing_cash_flow",
        ]:
            extracted_metrics[metric] = cash_flow.get(metric, 0.0)

        return extracted_metrics

    def _calculate_financial_ratios(
        self, extracted_data: Dict[str, float]
    ) -> Dict[str, float]:
        """
        计算财务比率

        Args:
            extracted_data (Dict[str, float]): 提取的财务数据

        Returns:
            Dict[str, float]: 计算的财务比率
        """
        calculated_ratios = {}

        # 计算所有定义的财务比率
        for ratio_name, ratio_formula in self.financial_ratios.items():
            try:
                calculated_ratios[ratio_name] = ratio_formula(extracted_data)
            except Exception:
                calculated_ratios[ratio_name] = 0.0

        return calculated_ratios

    def _normalize_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        标准化数据格式

        Args:
            data (Dict[str, Any]): 原始数据

        Returns:
            Dict[str, Any]: 标准化后的数据
        """
        normalized_data = {}

        # 确保所有数值都是浮点数
        for key, value in data.items():
            if isinstance(value, (int, float)):
                normalized_data[key] = float(value)
            else:
                normalized_data[key] = value

        return normalized_data

    def add_custom_metric(self, metric_name: str, calculation_formula):
        """
        添加自定义指标计算公式

        Args:
            metric_name (str): 指标名称
            calculation_formula (function): 计算公式函数
        """
        self.financial_ratios[metric_name] = calculation_formula

    def get_extracted_metrics(self) -> List[str]:
        """
        获取所有可提取的指标列表

        Returns:
            List[str]: 指标列表
        """
        return self.key_financial_metrics + list(self.financial_ratios.keys())
