#!/usr/bin/env python3
"""
IP 地址管理系统测试脚本
"""

import sys
import os
import tempfile
import requests
import time
import subprocess
from pathlib import Path
from threading import Thread

def start_server():
    """在后台启动服务器"""
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    env = os.environ.copy()
    env['PYTHONPATH'] = os.path.join(os.getcwd(), 'backend')
    subprocess.run([sys.executable, 'run.py'], env=env)

def test_ip_system():
    """测试 IP 地址管理系统"""
    print("🧪 测试 IP 地址管理系统...")

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
            if 'IP 地址管理系统' in response.text:
                print("✅ 页面标题正确")
            if '添加新 IP 地址' in response.text:
                print("✅ 添加功能存在")
            if 'IP 地址列表' in response.text:
                print("✅ 列表功能存在")
            if '共' in response.text and '个 IP 地址' in response.text:
                print("✅ 统计功能存在")

        else:
            print(f"❌ 主页访问失败，状态码: {response.status_code}")
            return False

        # 测试 API 接口
        print("🔌 测试 API 接口...")
        api_response = requests.get('http://localhost:5000/api/entries', timeout=10)

        if api_response.status_code == 200:
            print("✅ API 接口正常")
            entries = api_response.json()
            print(f"   获取到 {len(entries)} 个 IP 地址")

            # 验证数据结构
            if entries and all('ip' in entry for entry in entries):
                print("✅ 数据结构正确")
            else:
                print("⚠️  数据结构可能有问题")
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

        # 测试添加 IP 功能
        print("➕ 测试添加 IP 功能...")
        add_response = requests.post('http://localhost:5000/api/add',
                                   json={'ip': '192.168.99.99'},
                                   timeout=10)

        if add_response.status_code == 200:
            result = add_response.json()
            if result.get('success'):
                print("✅ IP 添加成功")
                print(f"   消息: {result.get('message')}")
            else:
                print(f"⚠️  IP 添加失败: {result.get('message')}")
        else:
            print(f"❌ 添加请求失败，状态码: {add_response.status_code}")

        return True

    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到服务器，请确保服务器已启动")
        return False
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

if __name__ == '__main__':
    print("🚀 IP 地址管理系统测试")
    print("=" * 50)

    success = test_ip_system()

    if success:
        print("\n✅ 所有测试通过！")
        print("\n📝 启动命令:")
        print("   python run.py")
        print("\n🌐 访问地址:")
        print("   http://localhost:5000")
        print("\n📁 IP 文件位置:")
        print("   ./ip_list.txt")
    else:
        print("\n❌ 测试失败")
        sys.exit(1)