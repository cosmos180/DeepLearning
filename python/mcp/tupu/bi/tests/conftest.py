"""
Pytest 配置文件
自动加载 .env 环境变量
"""
import os
from pathlib import Path


# 尝试加载 .env 文件
try:
    from dotenv import load_dotenv

    # 获取项目根目录（tests 目录的父目录）
    root_dir = Path(__file__).parent.parent
    env_file = root_dir / ".env"

    if env_file.exists():
        load_dotenv(env_file)
        print(f"\n[pytest] 已加载环境变量文件: {env_file}")
    else:
        print(f"\n[pytest] 未找到 .env 文件: {env_file}")
except ImportError:
    # 如果没有安装 python-dotenv，忽略
    print("\n[pytest] 未安装 python-dotenv，跳过 .env 加载")
    pass
