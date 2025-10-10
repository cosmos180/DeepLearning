#!/usr/bin/env python3
"""
配置管理模块
负责管理数据源配置、API密钥和系统设置
"""

import os
from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()


@dataclass
class DataSourceConfig:
    """数据源配置类"""
    name: str
    enabled: bool
    api_key: Optional[str] = None
    rate_limit: int = 100  # requests per minute
    timeout: int = 30  # seconds
    retry_attempts: int = 3


class DataSources:
    """数据源配置管理"""

    # 财务数据源配置
    FINANCIAL: List[DataSourceConfig] = [
        DataSourceConfig(
            name="yahoo",
            enabled=True,
            rate_limit=2000,  # Yahoo Finance 没有严格的限制
            timeout=30
        ),
        DataSourceConfig(
            name="financial_modeling_prep",
            enabled=os.getenv("FMP_API_KEY") is not None,
            api_key=os.getenv("FMP_API_KEY"),
            rate_limit=250,  # 免费版每天250次
            timeout=30
        ),
        DataSourceConfig(
            name="alpha_vantage",
            enabled=os.getenv("ALPHA_VANTAGE_API_KEY") is not None,
            api_key=os.getenv("ALPHA_VANTAGE_API_KEY"),
            rate_limit=5,  # 免费版每分钟5次
            timeout=30
        ),
    ]

    # 宏观数据源配置
    MACRO: List[DataSourceConfig] = [
        DataSourceConfig(
            name="fred",
            enabled=os.getenv("FRED_API_KEY") is not None,
            api_key=os.getenv("FRED_API_KEY"),
            rate_limit=120,  # 每分钟120次
            timeout=30
        ),
        DataSourceConfig(
            name="world_bank",
            enabled=True,
            rate_limit=100,
            timeout=30
        ),
    ]


class CacheConfig:
    """缓存配置"""

    # Redis配置
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    REDIS_ENABLED = os.getenv("REDIS_ENABLED", "false").lower() == "true"

    # 缓存过期时间（秒）
    CACHE_DURATION = {
        "financial_data": 3600,      # 1小时
        "market_data": 60,           # 1分钟
        "macro_data": 86400,         # 24小时
        "industry_data": 604800,     # 7天
        "company_info": 3600,        # 1小时
    }

    # 缓存键前缀
    CACHE_KEYS = {
        "financial_data": "fin:",
        "market_data": "mkt:",
        "macro_data": "macro:",
        "industry_data": "ind:",
        "company_info": "info:",
    }


class LoggingConfig:
    """日志配置"""

    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOG_FILE = os.getenv("LOG_FILE", "investment_analyst.log")

    # 是否启用性能监控
    ENABLE_PERFORMANCE_MONITORING = os.getenv("ENABLE_PERFORMANCE_MONITORING", "true").lower() == "true"


class SystemConfig:
    """系统配置"""

    # 调试模式
    DEBUG = os.getenv("DEBUG", "false").lower() == "true"

    # 是否使用真实数据
    USE_REAL_DATA = os.getenv("USE_REAL_DATA", "true").lower() == "true"

    # 数据源优先级
    DATA_SOURCE_PRIORITY = {
        "financial": ["yahoo", "financial_modeling_prep", "alpha_vantage"],
        "macro": ["fred", "world_bank"],
        "market": ["yahoo", "financial_modeling_prep"],
    }

    # 默认股票列表（用于测试）
    DEFAULT_STOCKS = ["AAPL", "MSFT", "GOOGL", "AMZN", "META"]

    # 请求超时设置
    DEFAULT_TIMEOUT = int(os.getenv("DEFAULT_TIMEOUT", "30"))

    # 并发请求数量限制
    MAX_CONCURRENT_REQUESTS = int(os.getenv("MAX_CONCURRENT_REQUESTS", "5"))


def get_data_source_config(source_type: str, source_name: str) -> Optional[DataSourceConfig]:
    """
    获取指定数据源的配置

    Args:
        source_type (str): 数据源类型 (financial/macro)
        source_name (str): 数据源名称

    Returns:
        Optional[DataSourceConfig]: 数据源配置，如果未找到返回None
    """
    sources = getattr(DataSources, source_type.upper(), [])
    for source in sources:
        if source.name == source_name:
            return source
    return None


def is_data_source_enabled(source_type: str, source_name: str) -> bool:
    """
    检查数据源是否启用

    Args:
        source_type (str): 数据源类型
        source_name (str): 数据源名称

    Returns:
        bool: 是否启用
    """
    config = get_data_source_config(source_type, source_name)
    return config is not None and config.enabled


def get_enabled_data_sources(source_type: str) -> List[str]:
    """
    获取启用的数据源列表

    Args:
        source_type (str): 数据源类型

    Returns:
        List[str]: 启用的数据源名称列表
    """
    sources = getattr(DataSources, source_type.upper(), [])
    return [source.name for source in sources if source.enabled]


def validate_config() -> Dict[str, Any]:
    """
    验证配置的有效性

    Returns:
        Dict[str, Any]: 验证结果
    """
    issues = []
    warnings = []

    # 检查必需的环境变量
    if SystemConfig.USE_REAL_DATA:
        if not get_enabled_data_sources("financial"):
            issues.append("No financial data sources enabled")

        if not get_enabled_data_sources("macro"):
            warnings.append("No macro data sources enabled")

    # 检查Redis配置
    if CacheConfig.REDIS_ENABLED:
        try:
            import redis
            client = redis.from_url(CacheConfig.REDIS_URL)
            client.ping()
        except Exception as e:
            warnings.append(f"Redis connection failed: {e}")

    return {
        "valid": len(issues) == 0,
        "issues": issues,
        "warnings": warnings,
        "enabled_sources": {
            "financial": get_enabled_data_sources("financial"),
            "macro": get_enabled_data_sources("macro"),
        }
    }


if __name__ == "__main__":
    # 验证配置并输出结果
    validation_result = validate_config()

    print("=== 配置验证结果 ===")
    print(f"配置有效: {validation_result['valid']}")

    if validation_result['issues']:
        print("\n⚠️  配置问题:")
        for issue in validation_result['issues']:
            print(f"  - {issue}")

    if validation_result['warnings']:
        print("\n⚠️  配置警告:")
        for warning in validation_result['warnings']:
            print(f"  - {warning}")

    print(f"\n启用的数据源:")
    print(f"  财务数据: {validation_result['enabled_sources']['financial']}")
    print(f"  宏观数据: {validation_result['enabled_sources']['macro']}")

    if SystemConfig.USE_REAL_DATA:
        print("\n✅ 系统将使用真实数据源")
    else:
        print("\n📊 系统将使用模拟数据源")