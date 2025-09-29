"""
Author       : bughero bughero2012@gmail.com
Date         : 2025-09-29 12:07:59
LastEditors  : bughero bughero2012@gmail.com
LastEditTime : 2025-09-29 12:08:09
FilePath     : /DeepLearning/python/investment_analyst/run_tests.py
Description  :

Copyright (c) 2025 by @Me, All Rights Reserved.
"""

#!/usr/bin/env python3
"""
运行所有单元测试的脚本
"""

import unittest
import sys
import os


def run_all_tests():
    """运行所有测试"""
    # 添加项目根目录到Python路径
    project_root = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, project_root)

    # 发现并运行所有测试
    loader = unittest.TestLoader()
    start_dir = os.path.join(project_root, "tests")
    suite = loader.discover(start_dir, pattern="test_*.py")

    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # 返回测试结果
    return result.wasSuccessful()


if __name__ == "__main__":
    print("开始运行所有单元测试...")
    print("=" * 50)

    success = run_all_tests()

    print("=" * 50)
    if success:
        print("所有测试通过!")
        sys.exit(0)
    else:
        print("部分测试失败!")
        sys.exit(1)
