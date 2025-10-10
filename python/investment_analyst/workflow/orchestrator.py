#!/usr/bin/env python3
"""
工作流协调器
负责调度和协调各个MCP模块的执行
"""

import time
from typing import Dict, Any
from datetime import datetime

# 导入各个MCP模块
from mcp.industry_analyst.analyst import IndustryAnalystMCP
from mcp.indicator_alignment.aligner import IndicatorAlignmentMCP
from mcp.financial_reader.reader import FinancialReaderMCP
from mcp.data_validator.validator import DataValidatorMCP
from mcp.external_data.external import ExternalDataMCP
from mcp.report_generator.generator import ReportGeneratorMCP

# 导入配置
from config import SystemConfig

# 根据配置选择下载器
if SystemConfig.USE_REAL_DATA:
    try:
        from mcp.downloader.downloader_real import DownloadMCP
        print("✅ 使用真实数据下载器")
    except ImportError as e:
        print(f"⚠️ 无法加载真实数据下载器，回退到模拟数据: {e}")
        from mcp.downloader.downloader import DownloadMCP
else:
    from mcp.downloader.downloader import DownloadMCP
    print("📊 使用模拟数据下载器")


class WorkflowOrchestrator:
    """工作流协调器类"""

    def __init__(self):
        """初始化工作流协调器"""
        self.industry_analyst = IndustryAnalystMCP()
        self.indicator_aligner = IndicatorAlignmentMCP()
        self.downloader = DownloadMCP()
        self.financial_reader = FinancialReaderMCP()
        self.data_validator = DataValidatorMCP()
        self.external_data = ExternalDataMCP()
        self.report_generator = ReportGeneratorMCP()

    def execute_analysis(self, stock_symbol: str) -> Dict[str, Any]:
        """
        执行完整的股票分析流程

        Args:
            stock_symbol (str): 股票代码

        Returns:
            Dict[str, Any]: 分析结果
        """
        try:
            # 记录开始时间
            start_time = time.time()

            # 步骤1: 行业分析
            industry_analysis = self.industry_analyst.analyze_industry(stock_symbol)

            # 步骤2: 指标对齐
            aligned_indicators = self.indicator_aligner.align_indicators(
                industry_analysis
            )

            # 步骤3: 数据下载
            raw_data = self.downloader.download_data(stock_symbol, aligned_indicators)

            # 步骤4: 财报阅读
            financial_data = self.financial_reader.extract_financial_data(raw_data)

            # 步骤5: 数据验证
            validated_data = self.data_validator.validate_data(financial_data)

            # 步骤6: 外部数据获取
            external_data = self.external_data.get_external_data(
                stock_symbol, industry_analysis
            )

            # 步骤7: 生成报告
            analysis_result = self.report_generator.generate_report(
                stock_symbol=stock_symbol,
                financial_data=validated_data,
                external_data=external_data,
                industry_analysis=industry_analysis,
            )

            # 添加执行时间和元数据
            analysis_result["execution_time"] = time.time() - start_time
            analysis_result["analysis_time"] = datetime.now().isoformat()

            return analysis_result

        except Exception as e:
            # 异常处理
            return {
                "stock_symbol": stock_symbol,
                "error": str(e),
                "analysis_time": datetime.now().isoformat(),
                "status": "failed",
            }

    def _handle_exception(self, step_name: str, exception: Exception) -> Dict[str, Any]:
        """
        处理执行过程中的异常

        Args:
            step_name (str): 步骤名称
            exception (Exception): 异常对象

        Returns:
            Dict[str, Any]: 错误信息
        """
        return {
            "step": step_name,
            "error": str(exception),
            "timestamp": datetime.now().isoformat(),
        }
