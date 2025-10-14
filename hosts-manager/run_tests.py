#!/usr/bin/env python3
"""
测试运行脚本
"""

import sys
import os
import subprocess
from pathlib import Path

def run_tests():
    """运行测试套件"""
    print("🧪 Hosts 管理系统测试工具")
    print("=" * 40)

    # 确保在正确的目录
    script_dir = Path(__file__).parent
    os.chdir(script_dir)

    # 检查测试文件是否存在
    test_file = script_dir / 'tests' / 'test_app.py'
    if not test_file.exists():
        print(f"❌ 测试文件不存在: {test_file}")
        return False

    try:
        # 运行测试
        result = subprocess.run([
            sys.executable, str(test_file)
        ], capture_output=True, text=True)

        print(result.stdout)
        if result.stderr:
            print("错误输出:")
            print(result.stderr)

        return result.returncode == 0

    except Exception as e:
        print(f"❌ 运行测试失败: {e}")
        return False

if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)