#!/usr/bin/env python3
"""
数据验证MCP
负责校验、交叉验证和单位统一
"""

from typing import Dict, Any, List, Tuple
import pandas as pd


class DataValidatorMCP:
    """数据验证MCP类"""

    def __init__(self):
        """初始化数据验证MCP"""
        # 定义数据验证规则
        self.validation_rules = {
            "revenue": {"min": 0, "max": 1e15, "type": "float"},
            "gross_profit": {"min": -1e15, "max": 1e15, "type": "float"},
            "operating_income": {"min": -1e15, "max": 1e15, "type": "float"},
            "net_income": {"min": -1e15, "max": 1e15, "type": "float"},
            "eps": {"min": -10000, "max": 10000, "type": "float"},
            "total_assets": {"min": 0, "max": 1e15, "type": "float"},
            "total_liabilities": {"min": 0, "max": 1e15, "type": "float"},
            "total_equity": {"min": -1e15, "max": 1e15, "type": "float"},
            "debt_to_equity": {"min": 0, "max": 100, "type": "float"},
            "gross_margin": {"min": -10, "max": 10, "type": "float"},
            "operating_margin": {"min": -10, "max": 10, "type": "float"},
            "net_margin": {"min": -10, "max": 10, "type": "float"},
            "roe": {"min": -10, "max": 10, "type": "float"},
            "roa": {"min": -10, "max": 10, "type": "float"},
            "current_ratio": {"min": 0, "max": 100, "type": "float"},
        }

        # 定义单位转换规则
        self.unit_conversion_rules = {
            "thousands": 1000,
            "millions": 1000000,
            "billions": 1000000000,
            "percent_as_decimal": 0.01,
            "percent_as_is": 1,
        }

    def validate_data(self, financial_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        验证财务数据

        Args:
            financial_data (Dict[str, Any]): 财务数据

        Returns:
            Dict[str, Any]: 验证结果
        """
        try:
            # 获取提取的数据
            extracted_data = financial_data.get("extracted_data", {})
            calculated_ratios = financial_data.get("calculated_ratios", {})

            # 合并所有数据
            all_data = {**extracted_data, **calculated_ratios}

            # 执行数据验证
            validation_results = self._perform_validation(all_data)

            # 执行数据交叉验证
            cross_validation_results = self._perform_cross_validation(all_data)

            # 统一数据单位
            unified_data = self._unify_units(all_data)

            return {
                "stock_symbol": financial_data.get("stock_symbol", ""),
                "validated_data": unified_data,
                "validation_results": validation_results,
                "cross_validation_results": cross_validation_results,
                "validation_status": "success",
                "timestamp": financial_data.get("timestamp", ""),
            }

        except Exception as e:
            return {
                "stock_symbol": financial_data.get("stock_symbol", ""),
                "error": str(e),
                "validation_status": "failed",
                "timestamp": financial_data.get("timestamp", ""),
            }

    def _perform_validation(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行数据验证

        Args:
            data (Dict[str, Any]): 待验证的数据

        Returns:
            Dict[str, Any]: 验证结果
        """
        validation_results = {}

        for key, value in data.items():
            # 检查是否有对应的验证规则
            if key in self.validation_rules:
                rule = self.validation_rules[key]
                is_valid, error_message = self._validate_value(value, rule)
                validation_results[key] = {
                    "valid": is_valid,
                    "error": error_message,
                    "value": value,
                }
            else:
                # 没有验证规则的字段默认为有效
                validation_results[key] = {"valid": True, "error": None, "value": value}

        return validation_results

    def _validate_value(self, value: Any, rule: Dict[str, Any]) -> Tuple[bool, str]:
        """
        验证单个值

        Args:
            value (Any): 待验证的值
            rule (Dict[str, Any]): 验证规则

        Returns:
            Tuple[bool, str]: (是否有效, 错误信息)
        """
        # 类型检查
        if rule["type"] == "float":
            if not isinstance(value, (int, float)):
                return False, f"期望浮点数类型，实际为 {type(value)}"

            # 范围检查
            if value < rule["min"] or value > rule["max"]:
                return False, f"值 {value} 超出范围 [{rule['min']}, {rule['max']}]"

        return True, ""

    def _perform_cross_validation(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行数据交叉验证

        Args:
            data (Dict[str, Any]): 待验证的数据

        Returns:
            Dict[str, Any]: 交叉验证结果
        """
        cross_validation_results = {}

        # 验证资产负债表平衡: 资产 = 负债 + 所有者权益
        total_assets = data.get("total_assets", 0)
        total_liabilities = data.get("total_liabilities", 0)
        total_equity = data.get("total_equity", 0)

        balance_check = abs(total_assets - (total_liabilities + total_equity))
        cross_validation_results["balance_sheet_balance"] = {
            "valid": balance_check < 1e-6,
            "difference": balance_check,
            "assets": total_assets,
            "liabilities_plus_equity": total_liabilities + total_equity,
        }

        # 验证现金流: 经营现金流 + 投资现金流 + 融资现金流 = 现金净变化
        operating_cf = data.get("operating_cash_flow", 0)
        investing_cf = data.get("investing_cash_flow", 0)
        financing_cf = data.get("financing_cash_flow", 0)
        cash_change = data.get("cash_and_equivalents", 0)  # 简化处理

        cash_flow_check = abs(
            (operating_cf + investing_cf + financing_cf) - cash_change
        )
        cross_validation_results["cash_flow_consistency"] = {
            "valid": cash_flow_check < 1e-6,
            "difference": cash_flow_check,
            "total_cf": operating_cf + investing_cf + financing_cf,
            "cash_change": cash_change,
        }

        # 验证利润率逻辑: 毛利率 >= 营业利润率 >= 净利润率
        gross_margin = data.get("gross_margin", 0)
        operating_margin = data.get("operating_margin", 0)
        net_margin = data.get("net_margin", 0)

        margin_logic_check = gross_margin >= operating_margin >= net_margin
        cross_validation_results["margin_logic"] = {
            "valid": margin_logic_check,
            "gross_margin": gross_margin,
            "operating_margin": operating_margin,
            "net_margin": net_margin,
        }

        return cross_validation_results

    def _unify_units(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        统一数据单位

        Args:
            data (Dict[str, Any]): 原始数据

        Returns:
            Dict[str, Any]: 统一单位后的数据
        """
        unified_data = {}

        # 复制所有数据
        for key, value in data.items():
            unified_data[key] = value

        # 特殊处理百分比数据
        percentage_fields = [
            "gross_margin",
            "operating_margin",
            "net_margin",
            "roe",
            "roa",
        ]
        for field in percentage_fields:
            if field in unified_data:
                # 确保百分比数据在合理范围内
                if unified_data[field] > 10:  # 可能是以百分比形式存储的
                    unified_data[field] = unified_data[field] * 0.01

        return unified_data

    def add_validation_rule(
        self, field_name: str, min_val: float, max_val: float, data_type: str
    ):
        """
        添加新的验证规则

        Args:
            field_name (str): 字段名称
            min_val (float): 最小值
            max_val (float): 最大值
            data_type (str): 数据类型
        """
        self.validation_rules[field_name] = {
            "min": min_val,
            "max": max_val,
            "type": data_type,
        }

    def get_validation_report(self, validation_results: Dict[str, Any]) -> str:
        """
        生成验证报告

        Args:
            validation_results (Dict[str, Any]): 验证结果

        Returns:
            str: 验证报告
        """
        report = "=== 数据验证报告 ===\n"

        invalid_count = 0
        for field, result in validation_results.items():
            if not result["valid"]:
                invalid_count += 1
                report += f"{field}: 无效 - {result['error']}\n"

        if invalid_count == 0:
            report += "所有数据验证通过\n"
        else:
            report += f"共发现 {invalid_count} 个数据问题\n"

        return report
