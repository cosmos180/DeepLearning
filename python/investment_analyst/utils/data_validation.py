#!/usr/bin/env python3
"""
数据验证工具
用于验证和清洗财务数据
"""

import logging
import pandas as pd
from typing import Dict, Any, List, Optional, Union
from datetime import datetime

logger = logging.getLogger(__name__)


class DataValidationError(Exception):
    """数据验证错误"""
    pass


class FinancialDataValidator:
    """财务数据验证器"""

    # 必需的财务字段
    REQUIRED_FINANCIAL_FIELDS = [
        'revenue',
        'gross_profit',
        'operating_income',
        'net_income',
        'total_assets',
        'total_liabilities',
        'total_equity'
    ]

    # 可选的财务字段
    OPTIONAL_FINANCIAL_FIELDS = [
        'eps',
        'shares_outstanding',
        'cash_and_equivalents',
        'long_term_debt',
        'operating_cash_flow',
        'investing_cash_flow',
        'financing_cash_flow'
    ]

    # 合理的财务比率范围
    VALID_RATIOS = {
        'gross_margin': (0, 1),
        'operating_margin': (-1, 1),
        'net_margin': (-1, 1),
        'roe': (-10, 10),  # Return on Equity
        'roa': (-2, 2),   # Return on Assets
        'debt_to_equity': (0, 10),
        'current_ratio': (0, 10),
        'pe_ratio': (0, 1000)
    }

    @classmethod
    def validate_financial_data(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        验证财务数据的完整性和合理性

        Args:
            data: 原始财务数据

        Returns:
            验证后的数据，包含验证结果和清洗后的数据
        """
        validation_result = {
            'is_valid': True,
            'errors': [],
            'warnings': [],
            'cleaned_data': data.copy(),
            'validation_timestamp': datetime.now().isoformat()
        }

        try:
            # 检查必需字段
            missing_fields = cls._check_required_fields(data)
            if missing_fields:
                validation_result['errors'].append(
                    f"缺少必需字段: {missing_fields}"
                )
                validation_result['is_valid'] = False

            # 数据类型验证和清洗
            cleaned_data = cls._clean_and_validate_types(data)
            validation_result['cleaned_data'] = cleaned_data

            # 业务逻辑验证
            cls._validate_business_logic(cleaned_data, validation_result)

            # 计算衍生指标
            derived_metrics = cls._calculate_derived_metrics(cleaned_data)
            validation_result['cleaned_data'].update(derived_metrics)

            # 验证财务比率
            cls._validate_financial_ratios(validation_result['cleaned_data'], validation_result)

            return validation_result

        except Exception as e:
            logger.error(f"数据验证过程中发生错误: {e}")
            validation_result['is_valid'] = False
            validation_result['errors'].append(f"验证过程错误: {str(e)}")
            return validation_result

    @classmethod
    def _check_required_fields(cls, data: Dict[str, Any]) -> List[str]:
        """检查必需字段"""
        missing_fields = []
        for field in cls.REQUIRED_FINANCIAL_FIELDS:
            if field not in data or data[field] is None:
                missing_fields.append(field)
        return missing_fields

    @classmethod
    def _clean_and_validate_types(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """清洗数据并验证类型"""
        cleaned_data = {}

        for key, value in data.items():
            try:
                if isinstance(value, str):
                    # 尝试将字符串转换为数字
                    if value.replace(',', '').replace('-', '').replace('.', '').isdigit():
                        cleaned_value = float(value.replace(',', ''))
                    else:
                        cleaned_value = value
                elif isinstance(value, (int, float)):
                    cleaned_value = float(value)
                elif pd.isna(value) if hasattr(value, '__iter__') else False:
                    cleaned_value = 0.0
                else:
                    cleaned_value = value

                cleaned_data[key] = cleaned_value

            except (ValueError, TypeError) as e:
                logger.warning(f"无法清洗字段 {key}: {value}, 错误: {e}")
                cleaned_data[key] = 0.0

        return cleaned_data

    @classmethod
    def _validate_business_logic(cls, data: Dict[str, Any], validation_result: Dict[str, Any]):
        """验证业务逻辑"""
        # 检查资产负债表平衡
        if all(key in data for key in ['total_assets', 'total_liabilities', 'total_equity']):
            calculated_assets = data['total_liabilities'] + data['total_equity']
            actual_assets = data['total_assets']
            difference = abs(calculated_assets - actual_assets)

            # 允许小的差异（四舍五入误差）
            tolerance = max(actual_assets * 0.001, 1000000)  # 0.1%或100万

            if difference > tolerance:
                validation_result['warnings'].append(
                    f"资产负债表不平衡: 资产({actual_assets:,.0f}) != "
                    f"负债+权益({calculated_assets:,.0f}), 差异: {difference:,.0f}"
                )

        # 检查收入的合理性
        if 'revenue' in data and data['revenue'] <= 0:
            validation_result['warnings'].append("收入为负数或零，可能存在问题")

        # 检查毛利的合理性
        if all(key in data for key in ['revenue', 'gross_profit']):
            if data['gross_profit'] > data['revenue']:
                validation_result['warnings'].append("毛利大于收入，数据可能错误")

    @classmethod
    def _calculate_derived_metrics(cls, data: Dict[str, Any]) -> Dict[str, float]:
        """计算衍生财务指标"""
        derived_metrics = {}

        try:
            # 毛利率
            if 'revenue' in data and 'gross_profit' in data and data['revenue'] > 0:
                derived_metrics['gross_margin'] = data['gross_profit'] / data['revenue']

            # 营业利润率
            if 'revenue' in data and 'operating_income' in data and data['revenue'] > 0:
                derived_metrics['operating_margin'] = data['operating_income'] / data['revenue']

            # 净利润率
            if 'revenue' in data and 'net_income' in data and data['revenue'] > 0:
                derived_metrics['net_margin'] = data['net_income'] / data['revenue']

            # 股东权益回报率(ROE)
            if 'net_income' in data and 'total_equity' in data and data['total_equity'] > 0:
                derived_metrics['roe'] = data['net_income'] / data['total_equity']

            # 资产回报率(ROA)
            if 'net_income' in data and 'total_assets' in data and data['total_assets'] > 0:
                derived_metrics['roa'] = data['net_income'] / data['total_assets']

            # 负债权益比
            if 'total_liabilities' in data and 'total_equity' in data and data['total_equity'] > 0:
                derived_metrics['debt_to_equity'] = data['total_liabilities'] / data['total_equity']

            # 流动比率
            if 'current_assets' in data and 'current_liabilities' in data:
                if data['current_liabilities'] > 0:
                    derived_metrics['current_ratio'] = data['current_assets'] / data['current_liabilities']

            # 自由现金流
            if all(key in data for key in ['operating_cash_flow', 'investing_cash_flow']):
                derived_metrics['free_cash_flow'] = (
                    data['operating_cash_flow'] + data['investing_cash_flow']
                )

        except Exception as e:
            logger.warning(f"计算衍生指标时发生错误: {e}")

        return derived_metrics

    @classmethod
    def _validate_financial_ratios(cls, data: Dict[str, Any], validation_result: Dict[str, Any]):
        """验证财务比率的合理性"""
        for ratio, (min_val, max_val) in cls.VALID_RATIOS.items():
            if ratio in data:
                value = data[ratio]
                if not (min_val <= value <= max_val):
                    validation_result['warnings'].append(
                        f"{ratio} 值 {value:.4f} 超出合理范围 [{min_val}, {max_val}]"
                    )


class MarketDataValidator:
    """市场数据验证器"""

    @classmethod
    def validate_market_data(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        验证市场数据

        Args:
            data: 市场数据

        Returns:
            验证结果
        """
        validation_result = {
            'is_valid': True,
            'errors': [],
            'warnings': [],
            'cleaned_data': data.copy(),
            'validation_timestamp': datetime.now().isoformat()
        }

        try:
            # 检查必需字段
            required_fields = ['current_price', 'market_cap']
            missing_fields = [field for field in required_fields
                            if field not in data or data[field] is None]

            if missing_fields:
                validation_result['errors'].append(f"缺少必需字段: {missing_fields}")
                validation_result['is_valid'] = False

            # 验证价格合理性
            if 'current_price' in data:
                price = data['current_price']
                if not isinstance(price, (int, float)) or price <= 0:
                    validation_result['errors'].append(f"无效的价格: {price}")
                    validation_result['is_valid'] = False
                elif price > 1000000:  # 价格超过100万通常有问题
                    validation_result['warnings'].append(f"价格异常高: {price}")

            # 验证市值合理性
            if 'market_cap' in data:
                market_cap = data['market_cap']
                if not isinstance(market_cap, (int, float)) or market_cap < 0:
                    validation_result['errors'].append(f"无效的市值: {market_cap}")
                    validation_result['is_valid'] = False

            return validation_result

        except Exception as e:
            logger.error(f"市场数据验证错误: {e}")
            validation_result['is_valid'] = False
            validation_result['errors'].append(f"验证过程错误: {str(e)}")
            return validation_result


def validate_data_pipeline(data: Dict[str, Any], data_type: str = "financial") -> Dict[str, Any]:
    """
    数据管道验证入口

    Args:
        data: 要验证的数据
        data_type: 数据类型 (financial/market/company_info)

    Returns:
        验证结果
    """
    if data_type == "financial":
        return FinancialDataValidator.validate_financial_data(data)
    elif data_type == "market":
        return MarketDataValidator.validate_market_data(data)
    else:
        return {
            'is_valid': True,
            'errors': [],
            'warnings': [f"未知的数据类型: {data_type}"],
            'cleaned_data': data,
            'validation_timestamp': datetime.now().isoformat()
        }


if __name__ == "__main__":
    # 测试用例
    test_financial_data = {
        'revenue': 394328000000,
        'gross_profit': 170782000000,
        'operating_income': 114301000000,
        'net_income': 99803000000,
        'total_assets': 352755000000,
        'total_liabilities': 287912000000,
        'total_equity': 64843000000,
        'eps': '6.11',  # 字符串类型
        'shares_outstanding': 16319400000
    }

    test_market_data = {
        'current_price': 150.25,
        'market_cap': 2500000000000,
        '52w_high': 198.23,
        '52w_low': 124.17
    }

    # 测试财务数据验证
    print("=== 财务数据验证测试 ===")
    result = validate_data_pipeline(test_financial_data, "financial")
    print(f"验证结果: {'通过' if result['is_valid'] else '失败'}")
    if result['errors']:
        print(f"错误: {result['errors']}")
    if result['warnings']:
        print(f"警告: {result['warnings']}")
    print(f"衍生指标: {list(result['cleaned_data'].keys())}")

    # 测试市场数据验证
    print("\n=== 市场数据验证测试 ===")
    result = validate_data_pipeline(test_market_data, "market")
    print(f"验证结果: {'通过' if result['is_valid'] else '失败'}")
    if result['errors']:
        print(f"错误: {result['errors']}")
    if result['warnings']:
        print(f"警告: {result['warnings']}")