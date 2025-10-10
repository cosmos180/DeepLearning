#!/usr/bin/env python3
"""
投资分析报告演示脚本
展示不同股票的分析报告和表格格式
"""

import os
import sys
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from client.client import InvestmentClient


def demo_analysis_report(symbol: str):
    """
    演示单个股票的分析报告

    Args:
        symbol: 股票代码
    """
    print(f"\n{'='*80}")
    print(f"🎯 {symbol} 投资分析报告演示")
    print(f"{'='*80}")
    print(f"⏰ 演示时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    try:
        # 创建客户端
        client = InvestmentClient()

        # 运行分析
        print(f"🔍 正在分析 {symbol}...")
        result = client.run_analysis(symbol)

        if result.get("status") == "success":
            print(f"✅ {symbol} 分析完成")
            print(f"⏱️ 执行时间: {result.get('execution_time', 0)*1000:.2f}ms")
            print(f"📊 推荐评级: {result.get('rating', 'N/A')}")
            print(f"🎯 目标价格: ${result.get('target_price', 'N/A')}")
            print()

            # 生成详细报告
            print("📋 详细分析报告:")
            report = client.get_analysis_report(symbol)
            print(report)
        else:
            print(f"❌ {symbol} 分析失败: {result.get('error', '未知错误')}")

    except Exception as e:
        print(f"❌ 演示 {symbol} 时发生错误: {e}")


def demo_comparison_table():
    """
    演示多股票对比表格
    """
    print(f"\n{'='*80}")
    print("📊 多股票对比分析演示")
    print(f"{'='*80}")

    symbols = ["AAPL", "MSFT", "GOOGL", "AMZN", "META"]
    results = {}

    client = InvestmentClient()

    # 获取所有股票的分析结果
    for symbol in symbols:
        try:
            print(f"🔍 分析 {symbol}...")
            result = client.run_analysis(symbol)
            if result.get("status") == "success":
                results[symbol] = result
                print(f"✅ {symbol} 分析完成")
            else:
                print(f"❌ {symbol} 分析失败")
        except Exception as e:
            print(f"❌ {symbol} 分析出错: {e}")

    # 创建对比表格
    if results:
        print(f"\n📈 股票对比分析:")
        print("-" * 80)

        # 表头
        headers = ["指标"] + list(results.keys())
        table_data = []

        # 添加各项指标到表格
        metrics = [
            ("推荐评级", lambda r: _format_rating(r.get("rating", "N/A"))),
            ("目标价格", lambda r: f"${r.get('target_price', 'N/A')}"),
            (
                "市值",
                lambda r: _format_currency(
                    r.get("executive_summary", {})
                    .get("company_overview", {})
                    .get("market_cap", 0)
                ),
            ),
            (
                "收入增长率",
                lambda r: f"{r.get('financial_analysis', {}).get('income_statement', {}).get('revenue_growth', 0)*100:.1f}%",
            ),
            (
                "毛利率",
                lambda r: f"{r.get('financial_analysis', {}).get('key_ratios', {}).get('gross_margin', 0)*100:.1f}%",
            ),
            (
                "净利润率",
                lambda r: f"{r.get('financial_analysis', {}).get('key_ratios', {}).get('net_margin', 0)*100:.1f}%",
            ),
            (
                "ROE",
                lambda r: f"{r.get('financial_analysis', {}).get('key_ratios', {}).get('roe', 0)*100:.1f}%",
            ),
            (
                "负债权益比",
                lambda r: f"{r.get('financial_analysis', {}).get('key_ratios', {}).get('debt_to_equity', 0):.2f}",
            ),
        ]

        for metric_name, metric_func in metrics:
            row = [metric_name]
            for symbol in symbols:
                if symbol in results:
                    row.append(metric_func(results[symbol]))
                else:
                    row.append("N/A")
            table_data.append(row)

        # 打印表格
        _print_table(table_data, headers)

    print(f"\n✅ 对比分析完成")


def demo_financial_ratios():
    """
    演示财务比率对比表格
    """
    print(f"\n{'='*80}")
    print("💰 财务比率详细对比")
    print(f"{'='*80}")

    symbols = ["AAPL", "MSFT", "GOOGL"]
    results = {}

    client = InvestmentClient()

    # 获取分析结果
    for symbol in symbols:
        try:
            result = client.run_analysis(symbol)
            if result.get("status") == "success":
                results[symbol] = result
        except Exception as e:
            print(f"❌ {symbol} 分析出错: {e}")

    if results:
        print(f"\n📊 关键财务比率对比:")
        print("-" * 80)

        # 损益表比率
        income_ratios = []
        income_headers = ["损益表比率"] + symbols

        for ratio_name, ratio_key in [
            ("毛利率", "gross_margin"),
            ("营业利润率", "operating_margin"),
            ("净利润率", "net_margin"),
        ]:
            row = [ratio_name]
            for symbol in symbols:
                if symbol in results:
                    value = (
                        results[symbol]
                        .get("financial_analysis", {})
                        .get("key_ratios", {})
                        .get(ratio_key, 0)
                    )
                    row.append(f"{value*100:.1f}%")
                else:
                    row.append("N/A")
            income_ratios.append(row)

        _print_table(income_ratios, income_headers)

        # 资产负债表比率
        balance_ratios = []
        balance_headers = ["资产负债表比率"] + symbols

        for ratio_name, ratio_key in [
            ("ROE", "roe"),
            ("ROA", "roa"),
            ("负债权益比", "debt_to_equity"),
        ]:
            row = [ratio_name]
            for symbol in symbols:
                if symbol in results:
                    value = (
                        results[symbol]
                        .get("financial_analysis", {})
                        .get("key_ratios", {})
                        .get(ratio_key, 0)
                    )
                    if ratio_key == "debt_to_equity":
                        row.append(f"{value:.2f}")
                    else:
                        row.append(f"{value*100:.1f}%")
                else:
                    row.append("N/A")
            balance_ratios.append(row)

        _print_table(balance_ratios, balance_headers)


def demo_industry_comparison():
    """
    演示行业对比表格
    """
    print(f"\n{'='*80}")
    print("🏭 行业对比分析")
    print(f"{'='*80}")

    # 选择AAPL进行详细的行业对比分析
    symbol = "AAPL"

    try:
        client = InvestmentClient()
        result = client.run_analysis(symbol)

        if result.get("status") == "success":
            competitive_data = result.get("industry_analysis", {}).get(
                "competitive_landscape", {}
            )

            if competitive_data:
                print(f"\n📊 {symbol} 行业对比分析:")
                print("-" * 80)

                # 创建行业对比表格
                competitors = competitive_data.copy()
                headers = ["指标"] + list(competitors.keys())
                table_data = []

                # 行业指标
                metrics = [
                    ("收入增长率", "revenue_growth", "{:.1f}%"),
                    ("毛利率", "gross_margin", "{:.1f}%"),
                    ("营业利润率", "operating_margin", "{:.1f}%"),
                    ("净利润率", "net_margin", "{:.1f}%"),
                    ("PE比率", "pe_ratio", "{:.0f}"),
                    ("负债权益比", "debt_to_equity", "{:.2f}"),
                    ("投入资本回报率", "roic", "{:.1f}%"),
                    ("市场份额", "market_share", "{:.1f}%"),
                ]

                for metric_name, metric_key, format_str in metrics:
                    row = [metric_name]
                    for company in headers[1:]:  # 跳过"指标"列头
                        if company in competitors:
                            value = competitors[company].get(metric_key, 0)
                            if isinstance(value, (int, float)):
                                row.append(
                                    format_str.format(
                                        value * 100 if value < 1 else value
                                    )
                                )
                            else:
                                row.append(str(value))
                        else:
                            row.append("N/A")
                    table_data.append(row)

                _print_table(table_data, headers)

                # 添加行业位置分析
                print(f"\n📈 {symbol} 行业位置:")
                symbol_data = competitors.get(symbol, {})

                print(
                    f"🎯 收入增长率排名: {_get_ranking(symbol_data, competitors, 'revenue_growth')}"
                )
                print(
                    f"💰 净利润率排名: {_get_ranking(symbol_data, competitors, 'net_margin')}"
                )
                print(
                    f"📊 PE比率排名: {_get_ranking(symbol_data, competitors, 'pe_ratio', ascending=True)}"
                )
                print(f"💎 ROIC排名: {_get_ranking(symbol_data, competitors, 'roic')}")

        else:
            print(f"❌ {symbol} 分析失败")

    except Exception as e:
        print(f"❌ 行业对比分析出错: {e}")


def _format_currency(amount):
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


def _format_rating(rating):
    """格式化评级"""
    rating_map = {
        "buy": "🟢 买入",
        "hold": "🟡 持有",
        "sell": "🔴 卖出",
        "strong_buy": "🚀 强烈买入",
        "strong_sell": "💣 强烈卖出",
    }
    return rating_map.get(rating.lower(), rating)


def _print_table(data, headers):
    """打印表格"""
    if not data:
        print("无数据")
        return

    # 计算列宽
    max_widths = [len(str(h)) for h in headers]
    for row in data:
        for i, cell in enumerate(row):
            if i < len(max_widths):
                max_widths[i] = max(max_widths[i], len(str(cell)))

    # 打印表头
    header_line = " | ".join(f"{h:<{max_widths[i]}}" for i, h in enumerate(headers))
    print(header_line)
    print("-" * len(header_line))

    # 打印数据行
    for row in data:
        line = " | ".join(
            f"{str(row[i]) if i < len(row) else '':<{max_widths[i]}}"
            for i in range(len(max_widths))
        )
        print(line)


def _get_ranking(target_data, all_data, metric, ascending=False):
    """获取排名"""
    try:
        values = []
        for company, data in all_data.items():
            value = data.get(metric, 0)
            if isinstance(value, (int, float)):
                values.append((company, value))

        # 排序
        values.sort(key=lambda x: x[1], reverse=not ascending)

        # 找到目标公司的排名
        for i, (company, value) in enumerate(values):
            if company == all_data:
                return f"第 {i+1} 名"

        return "N/A"
    except:
        return "N/A"


def main():
    """主演示函数"""
    print("🎯 投资分析报告演示系统")
    print("=" * 80)
    print("本演示将展示:")
    print("1. 单个股票的详细分析报告")
    print("2. 多股票对比分析表格")
    print("3. 财务比率详细对比")
    print("4. 行业竞争对比分析")
    print("=" * 80)

    # 演示1: 单个股票分析报告
    demo_analysis_report("AMD")

    # 演示2: 多股票对比
    demo_comparison_table()

    # 演示3: 财务比率对比
    demo_financial_ratios()

    # 演示4: 行业对比
    demo_industry_comparison()

    print(f"\n{'='*80}")
    print("🎉 演示完成！")
    print("💡 您可以看到，报告现在采用了清晰的表格格式展示")
    print("📊 包含了详细的财务数据、行业对比和投资建议")
    print("🔧 系统支持真实数据集成（Yahoo Finance）")
    print("⚡ 具备完整的错误处理和故障转移机制")
    print("=" * 80)


if __name__ == "__main__":
    main()
