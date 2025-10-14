#!/usr/bin/env python3
"""
Web 界面测试脚本
"""

import requests
import time
import subprocess
import sys
import os
from threading import Thread

def start_server():
    """在后台启动服务器"""
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    env = os.environ.copy()
    env['PYTHONPATH'] = os.path.join(os.getcwd(), 'backend')
    subprocess.run([sys.executable, 'run.py'], env=env)

def test_web_interface():
    """测试 Web 界面"""
    print("🧪 测试 Web 界面...")

    # 启动服务器线程
    server_thread = Thread(target=start_server, daemon=True)
    server_thread.start()

    # 等待服务器启动
    print("⏳ 等待服务器启动...")
    time.sleep(3)

    try:
        # 测试主页
        print("🌐 测试主页访问...")
        response = requests.get('http://localhost:5000', timeout=10)

        if response.status_code == 200:
            print("✅ 主页访问成功")
            print(f"   状态码: {response.status_code}")
            print(f"   内容长度: {len(response.text)} 字符")

            # 检查关键内容
            if 'Hosts 文件管理系统' in response.text:
                print("✅ 页面标题正确")
            if '添加新条目' in response.text:
                print("✅ 添加功能存在")
            if '当前 Hosts 条目' in response.text:
                print("✅ 条目列表存在")

        else:
            print(f"❌ 主页访问失败，状态码: {response.status_code}")
            return False

        # 测试 API 接口
        print("🔌 测试 API 接口...")
        api_response = requests.get('http://localhost:5000/api/entries', timeout=10)

        if api_response.status_code == 200:
            print("✅ API 接口正常")
            entries = api_response.json()
            print(f"   获取到 {len(entries)} 个条目")
        else:
            print(f"❌ API 接口失败，状态码: {api_response.status_code}")

        # 测试健康检查
        print("💓 测试健康检查...")
        health_response = requests.get('http://localhost:5000/health', timeout=10)

        if health_response.status_code == 200:
            print("✅ 健康检查正常")
            health_data = health_response.json()
            print(f"   状态: {health_data.get('status')}")
        else:
            print(f"❌ 健康检查失败，状态码: {health_response.status_code}")

        return True

    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到服务器，请确保服务器已启动")
        return False
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

if __name__ == '__main__':
    print("🚀 Hosts 管理系统 Web 界面测试")
    print("=" * 50)

    success = test_web_interface()

    if success:
        print("\n✅ 所有测试通过！")
        print("\n📝 启动命令:")
        print("   python run.py")
        print("\n🌐 访问地址:")
        print("   http://localhost:5000")
    else:
        print("\n❌ 测试失败")
        sys.exit(1)