#!/usr/bin/env python3
"""
Hosts 文件管理系统启动脚本
"""

import sys
import os
import argparse
import subprocess
from pathlib import Path

def check_python_version():
    """检查 Python 版本"""
    if sys.version_info < (3, 6):
        print("❌ 错误: 需要 Python 3.6 或更高版本")
        print(f"   当前版本: {sys.version}")
        sys.exit(1)

def check_dependencies():
    """检查依赖是否安装"""
    try:
        import flask
        print("✅ Flask 已安装")
    except ImportError:
        print("❌ Flask 未安装，正在安装...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ 依赖安装完成")

def check_ip_file_permission():
    """检查是否有权限修改 IP 文件"""
    ip_file_path = os.path.join(os.path.dirname(__file__), 'ip_list.txt')

    if os.path.exists(ip_file_path):
        if os.access(ip_file_path, os.W_OK):
            print(f"✅ 有权限修改 IP 文件: {ip_file_path}")
        else:
            print(f"⚠️  警告: 没有权限修改 IP 文件: {ip_file_path}")
            print("   提示: 请检查文件权限")
    else:
        print(f"ℹ️  信息: IP 文件不存在，将自动创建: {ip_file_path}")

def start_server(host='0.0.0.0', port=5000, debug=False):
    """启动服务器"""
    print(f"\n🚀 启动 IP 地址管理系统...")
    print(f"📡 服务地址: http://{host}:{port}")
    print(f"🔧 调试模式: {'开启' if debug else '关闭'}")
    print(f"📂 工作目录: {os.path.abspath('.')}")
    print("🛑 按 Ctrl+C 停止服务器\n")

    # 添加 backend 目录到 Python 路径
    backend_path = os.path.join(os.path.dirname(__file__), 'backend')
    if backend_path not in sys.path:
        sys.path.insert(0, backend_path)

    try:
        from app import app
        app.run(host=host, port=port, debug=debug)
    except ImportError as e:
        print(f"❌ 导入应用失败: {e}")
        print("   请确保在正确的目录中运行此脚本")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description='Hosts 文件管理系统')
    parser.add_argument('--host', default='0.0.0.0', help='服务器主机地址 (默认: 0.0.0.0)')
    parser.add_argument('--port', type=int, default=5000, help='服务器端口 (默认: 5000)')
    parser.add_argument('--debug', action='store_true', help='启用调试模式')
    parser.add_argument('--check-only', action='store_true', help='仅检查环境和依赖，不启动服务器')
    parser.add_argument('--install-deps', action='store_true', help='安装依赖包')

    args = parser.parse_args()

    print("=" * 60)
    print("🌐 IP 地址管理系统")
    print("=" * 60)

    # 检查 Python 版本
    check_python_version()

    # 安装依赖（如果指定）
    if args.install_deps:
        print("📦 安装依赖包...")
        check_dependencies()
        print("✅ 依赖安装完成")
        return

    # 检查依赖
    print("🔍 检查环境...")
    check_dependencies()

    # 检查权限
    check_ip_file_permission()

    if args.check_only:
        print("\n✅ 环境检查完成")
        return

    # 启动服务器
    try:
        start_server(
            host=args.host,
            port=args.port,
            debug=args.debug
        )
    except KeyboardInterrupt:
        print("\n\n👋 服务器已停止")

if __name__ == '__main__':
    main()