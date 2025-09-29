#!/usr/bin/env python3
"""
指标对齐MCP
负责财报字段映射规则
"""

from typing import Dict, List, Any


class IndicatorAlignmentMCP:
    """指标对齐MCP类"""

    def __init__(self):
        """初始化指标对齐MCP"""
        # 定义财报字段映射规则
        self.financial_mapping_rules = {
            # 收入相关指标
            "revenue": ["total_revenue", "sales", "revenue", "total_sales"],
            "revenue_growth": [
                "revenue_growth_rate",
                "sales_growth",
                "yoy_revenue_growth",
            ],
            # 利润相关指标
            "gross_profit": ["gross_profit", "gross_income"],
            "gross_margin": ["gross_margin", "gross_profit_margin"],
            "operating_income": ["operating_income", "ebit"],
            "net_income": ["net_income", "net_profit", "net_earnings"],
            "eps": ["eps", "earnings_per_share"],
            # 资产负债相关指标
            "total_assets": ["total_assets", "assets"],
            "total_liabilities": ["total_liabilities", "liabilities"],
            "total_equity": ["total_equity", "shareholders_equity", "equity"],
            "debt_to_equity": ["debt_to_equity", "debt_equity_ratio"],
            # 现金流相关指标
            "operating_cash_flow": ["operating_cash_flow", "cash_flow_from_operations"],
            "free_cash_flow": ["free_cash_flow", "fcf"],
            # 效率相关指标
            "roe": ["roe", "return_on_equity"],
            "roa": ["roa", "return_on_assets"],
            "asset_turnover": ["asset_turnover", "asset_turnover_ratio"],
            # 行业特定指标
            "rd_intensity": [
                "rd_intensity",
                "r_d_intensity",
                "research_development_intensity",
            ],
            "same_store_sales": ["same_store_sales", "comparable_store_sales"],
            "market_share": ["market_share", "market_penetration"],
            "inventory_turnover": ["inventory_turnover", "inventory_turnover_ratio"],
            "capex_efficiency": ["capex_efficiency", "capital_expenditure_efficiency"],
        }

        # 单位转换规则
        self.unit_conversion_rules = {
            "thousands": 1000,
            "millions": 1000000,
            "billions": 1000000000,
            "percent": 0.01,
        }

    def align_indicators(self, industry_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        对齐指标并定义映射规则

        Args:
            industry_analysis (Dict[str, Any]): 行业分析结果

        Returns:
            Dict[str, Any]: 指标对齐结果
        """
        # 获取行业关键指标
        key_metrics = industry_analysis.get("key_metrics", [])

        # 为每个关键指标定义映射规则
        aligned_indicators = {}
        for metric in key_metrics:
            aligned_indicators[metric] = {
                "possible_names": self.financial_mapping_rules.get(metric, [metric]),
                "unit_conversion": self._determine_unit_conversion(metric),
                "validation_rules": self._define_validation_rules(metric),
            }

        return {
            "industry": industry_analysis.get("industry", {}),
            "aligned_indicators": aligned_indicators,
            "mapping_rules": self.financial_mapping_rules,
            "unit_rules": self.unit_conversion_rules,
        }

    def _determine_unit_conversion(self, metric: str) -> Dict[str, Any]:
        """
        确定单位转换规则

        Args:
            metric (str): 指标名称

        Returns:
            Dict[str, Any]: 单位转换规则
        """
        # 根据指标类型确定默认单位
        currency_metrics = [
            "revenue",
            "gross_profit",
            "net_income",
            "operating_income",
            "total_assets",
            "total_liabilities",
            "total_equity",
        ]
        percentage_metrics = [
            "gross_margin",
            "roe",
            "roa",
            "debt_to_equity",
            "asset_turnover",
            "rd_intensity",
        ]

        if metric in currency_metrics:
            return {
                "default_unit": "millions",
                "conversion_factor": self.unit_conversion_rules["millions"],
            }
        elif metric in percentage_metrics:
            return {
                "default_unit": "percent",
                "conversion_factor": self.unit_conversion_rules["percent"],
            }
        else:
            return {"default_unit": "unit", "conversion_factor": 1}

    def _define_validation_rules(self, metric: str) -> Dict[str, Any]:
        """
        定义验证规则

        Args:
            metric (str): 指标名称

        Returns:
            Dict[str, Any]: 验证规则
        """
        # 根据指标类型定义验证规则
        validation_rules = {"min_value": None, "max_value": None, "data_type": "float"}

        # 为不同指标定义合理的范围
        if metric in ["gross_margin", "roe", "roa"]:
            validation_rules["min_value"] = -1.0
            validation_rules["max_value"] = 5.0  # 500%
        elif metric in ["debt_to_equity"]:
            validation_rules["min_value"] = 0.0
            validation_rules["max_value"] = 10.0
        elif metric in ["revenue_growth"]:
            validation_rules["min_value"] = -1.0  # -100%
            validation_rules["max_value"] = 10.0  # 1000%

        return validation_rules

    def add_mapping_rule(self, standard_name: str, alternative_names: List[str]):
        """
        添加新的映射规则

        Args:
            standard_name (str): 标准名称
            alternative_names (List[str]): 替代名称列表
        """
        if standard_name in self.financial_mapping_rules:
            self.financial_mapping_rules[standard_name].extend(alternative_names)
        else:
            self.financial_mapping_rules[standard_name] = alternative_names

    def get_mapping_rule(self, standard_name: str) -> List[str]:
        """
        获取映射规则

        Args:
            standard_name (str): 标准名称

        Returns:
            List[str]: 映射规则
        """
        return self.financial_mapping_rules.get(standard_name, [standard_name])
