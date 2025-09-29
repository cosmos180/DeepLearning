#!/usr/bin/env python3
"""
外部数据MCP
负责获取行业、宏观和同业对比数据
"""

from typing import Dict, Any, List
import json
from datetime import datetime


class ExternalDataMCP:
    """外部数据MCP类"""

    def __init__(self):
        """初始化外部数据MCP"""
        # 行业数据源
        self.industry_sources = {
            "technology": ["Gartner", "IDC", "Statista"],
            "finance": ["S&P Global", "Moody's", "Fitch"],
            "healthcare": ["IQVIA", "EvaluatePharma", "Frost & Sullivan"],
            "consumer": ["Nielsen", "Euromonitor", "Mintel"],
            "energy": ["IEA", "EIA", "Wood Mackenzie"],
            "industrial": ["McKinsey", "BCG", "Deloitte"],
        }

        # 宏观经济指标
        self.macro_indicators = [
            "gdp_growth",
            "inflation_rate",
            "interest_rate",
            "unemployment_rate",
            "consumer_sentiment",
            "pmi",
            "currency_exchange_rates",
            "commodity_prices",
        ]

        # 同业对比指标
        self.peer_comparison_metrics = [
            "revenue_growth",
            "profit_margins",
            "market_share",
            "valuation_multiples",
            "operating_efficiency",
            "financial_health",
        ]

    def get_external_data(
        self, stock_symbol: str, industry_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        获取外部数据

        Args:
            stock_symbol (str): 股票代码
            industry_analysis (Dict[str, Any]): 行业分析结果

        Returns:
            Dict[str, Any]: 外部数据
        """
        try:
            # 获取行业数据
            industry_data = self._get_industry_data(industry_analysis)

            # 获取宏观经济数据
            macro_data = self._get_macro_economic_data()

            # 获取同业对比数据
            peer_comparison_data = self._get_peer_comparison_data(
                stock_symbol, industry_analysis
            )

            return {
                "stock_symbol": stock_symbol,
                "industry_data": industry_data,
                "macro_economic_data": macro_data,
                "peer_comparison_data": peer_comparison_data,
                "timestamp": datetime.now().isoformat(),
                "status": "success",
            }

        except Exception as e:
            return {
                "stock_symbol": stock_symbol,
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
                "status": "failed",
            }

    def _get_industry_data(self, industry_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        获取行业数据

        Args:
            industry_analysis (Dict[str, Any]): 行业分析结果

        Returns:
            Dict[str, Any]: 行业数据
        """
        industry_category = industry_analysis.get("category", "technology")
        sub_category = industry_analysis.get("subcategory", "general")

        # 模拟行业数据获取
        return self._get_mock_industry_data(industry_category, sub_category)

    def _get_macro_economic_data(self) -> Dict[str, Any]:
        """
        获取宏观经济数据

        Returns:
            Dict[str, Any]: 宏观经济数据
        """
        # 模拟宏观经济数据获取
        return self._get_mock_macro_data()

    def _get_peer_comparison_data(
        self, stock_symbol: str, industry_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        获取同业对比数据

        Args:
            stock_symbol (str): 股票代码
            industry_analysis (Dict[str, Any]): 行业分析结果

        Returns:
            Dict[str, Any]: 同业对比数据
        """
        industry_category = industry_analysis.get("category", "technology")
        benchmark_companies = industry_analysis.get("benchmark_companies", [])

        # 确保包含当前股票
        if stock_symbol not in benchmark_companies:
            benchmark_companies.append(stock_symbol)

        # 模拟同业对比数据获取
        return self._get_mock_peer_comparison_data(
            benchmark_companies, industry_category
        )

    def _get_mock_industry_data(
        self, industry_category: str, sub_category: str
    ) -> Dict[str, Any]:
        """
        获取模拟行业数据

        Args:
            industry_category (str): 行业类别
            sub_category (str): 子行业类别

        Returns:
            Dict[str, Any]: 模拟行业数据
        """
        mock_industry_data = {
            "technology": {
                "market_size": 5000000000000,  # 5万亿美元
                "growth_rate": 0.08,  # 8%
                "cagr_5y": 0.075,  # 5年复合增长率
                "market_concentration": 0.35,  # 市场集中度
                "regulatory_risk": "medium",
                "key_trends": ["AI", "Cloud", "IoT", "Cybersecurity"],
                "barriers_to_entry": "high",
            },
            "finance": {
                "market_size": 12000000000000,  # 12万亿美元
                "growth_rate": 0.04,  # 4%
                "cagr_5y": 0.038,  # 5年复合增长率
                "market_concentration": 0.25,  # 市场集中度
                "regulatory_risk": "high",
                "key_trends": ["Digital Banking", "Fintech", "ESG", "Blockchain"],
                "barriers_to_entry": "very_high",
            },
            "healthcare": {
                "market_size": 8000000000000,  # 8万亿美元
                "growth_rate": 0.06,  # 6%
                "cagr_5y": 0.058,  # 5年复合增长率
                "market_concentration": 0.15,  # 市场集中度
                "regulatory_risk": "high",
                "key_trends": [
                    "Personalized Medicine",
                    "Telemedicine",
                    "AI Diagnostics",
                    "Biotech",
                ],
                "barriers_to_entry": "high",
            },
        }

        return mock_industry_data.get(
            industry_category, self._get_default_industry_data()
        )

    def _get_mock_macro_data(self) -> Dict[str, Any]:
        """
        获取模拟宏观经济数据

        Returns:
            Dict[str, Any]: 模拟宏观经济数据
        """
        return {
            "gdp_growth": 0.021,  # 2.1%
            "inflation_rate": 0.032,  # 3.2%
            "interest_rate": 0.0525,  # 5.25%
            "unemployment_rate": 0.038,  # 3.8%
            "consumer_sentiment": 72.5,
            "pmi": 52.3,
            "usd_index": 103.4,
            "oil_price": 85.6,  # 美元/桶
            "gold_price": 1925.0,  # 美元/盎司
            "vix_volatility": 18.5,
        }

    def _get_mock_peer_comparison_data(
        self, benchmark_companies: List[str], industry_category: str
    ) -> Dict[str, Any]:
        """
        获取模拟同业对比数据

        Args:
            benchmark_companies (List[str]): 对标公司列表
            industry_category (str): 行业类别

        Returns:
            Dict[str, Any]: 模拟同业对比数据
        """
        # 为每个对标公司生成模拟数据
        peer_data = {}

        for company in benchmark_companies:
            peer_data[company] = self._generate_peer_metrics(company, industry_category)

        return {
            "benchmark_companies": benchmark_companies,
            "peer_metrics": peer_data,
            "industry_percentiles": self._calculate_industry_percentiles(peer_data),
        }

    def _generate_peer_metrics(
        self, company: str, industry_category: str
    ) -> Dict[str, float]:
        """
        为公司生成模拟同业指标

        Args:
            company (str): 公司代码
            industry_category (str): 行业类别

        Returns:
            Dict[str, float]: 公司指标
        """
        # 基于行业和公司生成不同的指标值
        base_metrics = {
            "revenue_growth": 0.05 + (hash(company) % 10) * 0.01,  # 5% - 15%
            "gross_margin": 0.35 + (hash(company) % 20) * 0.01,  # 35% - 55%
            "operating_margin": 0.15 + (hash(company) % 15) * 0.01,  # 15% - 30%
            "net_margin": 0.10 + (hash(company) % 12) * 0.01,  # 10% - 22%
            "market_share": 0.02 + (hash(company) % 8) * 0.01,  # 2% - 10%
            "pe_ratio": 15 + (hash(company) % 20),  # 15 - 35
            "debt_to_equity": 0.2 + (hash(company) % 5) * 0.1,  # 0.2 - 0.7
            "roic": 0.08 + (hash(company) % 12) * 0.01,  # 8% - 20%
        }

        return base_metrics

    def _calculate_industry_percentiles(
        self, peer_data: Dict[str, Dict[str, float]]
    ) -> Dict[str, Dict[str, float]]:
        """
        计算行业百分位数

        Args:
            peer_data (Dict[str, Dict[str, float]]): 同业数据

        Returns:
            Dict[str, Dict[str, float]]: 百分位数
        """
        if not peer_data:
            return {}

        # 简化处理，返回固定值
        return {
            "median": {
                "revenue_growth": 0.08,
                "gross_margin": 0.42,
                "operating_margin": 0.18,
                "net_margin": 0.13,
                "market_share": 0.05,
                "pe_ratio": 22,
                "debt_to_equity": 0.35,
                "roic": 0.12,
            },
            "75th_percentile": {
                "revenue_growth": 0.12,
                "gross_margin": 0.48,
                "operating_margin": 0.24,
                "net_margin": 0.18,
                "market_share": 0.08,
                "pe_ratio": 28,
                "debt_to_equity": 0.45,
                "roic": 0.16,
            },
            "25th_percentile": {
                "revenue_growth": 0.04,
                "gross_margin": 0.36,
                "operating_margin": 0.12,
                "net_margin": 0.08,
                "market_share": 0.03,
                "pe_ratio": 16,
                "debt_to_equity": 0.25,
                "roic": 0.08,
            },
        }

    def _get_default_industry_data(self) -> Dict[str, Any]:
        """
        获取默认行业数据

        Returns:
            Dict[str, Any]: 默认行业数据
        """
        return {
            "market_size": 0,
            "growth_rate": 0,
            "cagr_5y": 0,
            "market_concentration": 0,
            "regulatory_risk": "unknown",
            "key_trends": [],
            "barriers_to_entry": "unknown",
        }

    def add_industry_source(self, industry_category: str, source: str):
        """
        添加行业数据源

        Args:
            industry_category (str): 行业类别
            source (str): 数据源
        """
        if industry_category in self.industry_sources:
            self.industry_sources[industry_category].append(source)
        else:
            self.industry_sources[industry_category] = [source]

    def get_available_indicators(self) -> Dict[str, List[str]]:
        """
        获取可用的外部数据指标

        Returns:
            Dict[str, List[str]]: 可用指标分类
        """
        return {
            "macro_indicators": self.macro_indicators,
            "peer_comparison_metrics": self.peer_comparison_metrics,
        }
