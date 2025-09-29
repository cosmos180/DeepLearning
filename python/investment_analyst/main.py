"""
Author       : bughero bughero2012@gmail.com
Date         : 2025-09-29 11:22:38
LastEditors  : bughero bughero2012@gmail.com
LastEditTime : 2025-09-29 11:22:47
FilePath     : /DeepLearning/python/investment_analyst/main.py
Description  :

Copyright (c) 2025 by @Me, All Rights Reserved.
"""

#!/usr/bin/env python3
"""
顶级投资分析师系统主入口
"""

from workflow.orchestrator import WorkflowOrchestrator
from client.client import InvestmentClient


def main():
    # 创建客户端
    client = InvestmentClient()

    # 运行分析流程
    result = client.run_analysis("AAPL")

    # 输出结果
    print("分析完成，结果如下：")
    print(result)


if __name__ == "__main__":
    main()
