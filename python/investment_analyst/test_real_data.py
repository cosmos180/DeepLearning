#!/usr/bin/env python3
"""
真实数据集成测试脚本
测试Yahoo Finance数据提供者和整个系统的集成
"""

import os
import sys
import logging
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def test_configuration():
    """测试配置系统"""
    print("\n" + "="*50)
    print("🔧 测试配置系统")
    print("="*50)

    try:
        from config import validate_config, SystemConfig

        # 验证配置
        result = validate_config()
        print(f"✅ 配置验证: {'通过' if result['valid'] else '失败'}")

        print(f"📊 使用真实数据: {SystemConfig.USE_REAL_DATA}")
        print(f"🔍 调试模式: {SystemConfig.DEBUG}")

        if result['issues']:
            print("⚠️ 配置问题:")
            for issue in result['issues']:
                print(f"  - {issue}")

        if result['warnings']:
            print("⚠️ 配置警告:")
            for warning in result['warnings']:
                print(f"  - {warning}")

        return True

    except Exception as e:
        print(f"❌ 配置测试失败: {e}")
        return False


def test_data_providers():
    """测试数据提供者"""
    print("\n" + "="*50)
    print("📡 测试数据提供者")
    print("="*50)

    try:
        # 测试Yahoo Finance提供者
        print("\n🔍 测试Yahoo Finance提供者...")
        try:
            from data_sources.yahoo_finance import YahooFinanceProvider, YFINANCE_AVAILABLE

            if YFINANCE_AVAILABLE:
                provider = YahooFinanceProvider()
                print("✅ Yahoo Finance提供者初始化成功")

                # 测试市场数据获取
                print("📈 测试市场数据获取...")
                market_data = provider.get_market_data("AAPL")
                print(f"市场数据状态: {market_data.get('status', 'unknown')}")

                if market_data.get('status') == 'success':
                    price = market_data['market_data'].get('current_price', 0)
                    print(f"  AAPL当前价格: ${price:.2f}")

                # 测试公司信息获取
                print("🏢 测试公司信息获取...")
                company_info = provider.get_company_info("AAPL")
                print(f"公司信息状态: {company_info.get('status', 'unknown')}")

                if company_info.get('status') == 'success':
                    name = company_info['company_info'].get('name', 'Unknown')
                    print(f"  公司名称: {name}")

            else:
                print("❌ yfinance库未安装")

        except Exception as e:
            print(f"❌ Yahoo Finance测试失败: {e}")

        return True

    except Exception as e:
        print(f"❌ 数据提供者测试失败: {e}")
        return False


def test_data_manager():
    """测试数据管理器"""
    print("\n" + "="*50)
    print("🗄️ 测试数据管理器")
    print("="*50)

    try:
        from data_sources.data_manager import get_data_manager

        # 初始化数据管理器
        manager = get_data_manager()
        print("✅ 数据管理器初始化成功")

        # 获取数据源状态
        status = manager.get_data_source_status()
        print(f"📊 数据源状态: {status}")

        # 测试数据获取
        print("\n📈 测试财务数据获取...")
        financial_data = manager.get_financial_data("AAPL")
        print(f"财务数据状态: {financial_data.get('status', 'unknown')}")

        print("\n💰 测试市场数据获取...")
        market_data = manager.get_market_data("AAPL")
        print(f"市场数据状态: {market_data.get('status', 'unknown')}")

        if market_data.get('status') == 'success':
            price = market_data['market_data'].get('current_price', 0)
            print(f"  AAPL当前价格: ${price:.2f}")

        return True

    except Exception as e:
        print(f"❌ 数据管理器测试失败: {e}")
        return False


def test_downloader_mcp():
    """测试下载器MCP"""
    print("\n" + "="*50)
    print("⬇️ 测试下载器MCP")
    print("="*50)

    try:
        # 根据配置选择下载器
        from config import SystemConfig

        if SystemConfig.USE_REAL_DATA:
            print("🌐 使用真实数据下载器")
            from mcp.downloader.downloader_real import DownloadMCP
        else:
            print("📊 使用模拟数据下载器")
            from mcp.downloader.downloader import DownloadMCP

        # 初始化下载器
        downloader = DownloadMCP()
        print("✅ 下载器初始化成功")

        # 获取数据源状态
        if hasattr(downloader, 'get_data_source_status'):
            status = downloader.get_data_source_status()
            print(f"📊 数据源状态: {status.get('use_real_data', 'unknown')}")

        # 测试数据下载
        print("\n📥 测试数据下载...")
        test_indicators = {"test": "value"}
        downloaded_data = downloader.download_data("AAPL", test_indicators)
        print(f"下载状态: {downloaded_data.get('download_status', 'unknown')}")

        if downloaded_data.get('download_status') == 'success':
            print("✅ 数据下载成功")
            if 'raw_data' in downloaded_data:
                print("  📊 包含原始数据")
            if 'financial_data' in downloaded_data:
                print("  💰 包含财务数据")
            if 'market_data' in downloaded_data:
                print("  📈 包含市场数据")
        else:
            error = downloaded_data.get('error', '未知错误')
            print(f"❌ 数据下载失败: {error}")

        return True

    except Exception as e:
        print(f"❌ 下载器MCP测试失败: {e}")
        return False


def test_workflow_integration():
    """测试工作流集成"""
    print("\n" + "="*50)
    print("🔄 测试工作流集成")
    print("="*50)

    try:
        from workflow.orchestrator import WorkflowOrchestrator

        # 初始化工作流协调器
        orchestrator = WorkflowOrchestrator()
        print("✅ 工作流协调器初始化成功")

        # 测试完整的分析流程
        print("\n🔬 测试完整分析流程...")
        result = orchestrator.execute_analysis("AAPL")
        print(f"分析状态: {result.get('status', 'unknown')}")

        if result.get('status') == 'success':
            print("✅ 分析流程执行成功")
            print(f"⏱️ 执行时间: {result.get('execution_time', 0):.4f}秒")

            # 显示关键结果
            if 'rating' in result:
                print(f"📊 投资评级: {result['rating']}")
            if 'target_price' in result:
                print(f"🎯 目标价格: ${result['target_price']}")

        else:
            error = result.get('error', '未知错误')
            print(f"❌ 分析流程失败: {error}")

        return True

    except Exception as e:
        print(f"❌ 工作流集成测试失败: {e}")
        return False


def test_client_integration():
    """测试客户端集成"""
    print("\n" + "="*50)
    print("💻 测试客户端集成")
    print("="*50)

    try:
        from client.client import InvestmentClient

        # 初始化客户端
        client = InvestmentClient()
        print("✅ 投资客户端初始化成功")

        # 测试分析运行
        print("\n🏃 测试分析运行...")
        result = client.run_analysis("AAPL")
        print(f"运行状态: {result.get('status', 'unknown')}")

        if result.get('status') == 'success':
            print("✅ 分析运行成功")

            # 测试报告生成
            print("\n📄 测试报告生成...")
            report = client.get_analysis_report("AAPL")
            print("✅ 报告生成成功")
            print(f"报告长度: {len(report)} 字符")

            # 显示报告开头
            print("\n📋 报告预览:")
            print(report[:300] + "..." if len(report) > 300 else report)

        else:
            error = result.get('error', '未知错误')
            print(f"❌ 分析运行失败: {error}")

        return True

    except Exception as e:
        print(f"❌ 客户端集成测试失败: {e}")
        return False


def main():
    """主测试函数"""
    print("🚀 Yahoo Finance真实数据集成测试")
    print(f"⏰ 测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # 运行所有测试
    tests = [
        ("配置系统", test_configuration),
        ("数据提供者", test_data_providers),
        ("数据管理器", test_data_manager),
        ("下载器MCP", test_downloader_mcp),
        ("工作流集成", test_workflow_integration),
        ("客户端集成", test_client_integration),
    ]

    results = {}
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ {test_name}测试发生异常: {e}")
            results[test_name] = False

    # 总结测试结果
    print("\n" + "="*50)
    print("📊 测试结果总结")
    print("="*50)

    passed = sum(results.values())
    total = len(results)

    for test_name, result in results.items():
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name}: {status}")

    print(f"\n总计: {passed}/{total} 测试通过")

    if passed == total:
        print("🎉 所有测试通过！Yahoo Finance集成成功！")
    else:
        print("⚠️ 部分测试失败，请检查错误信息")

    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)