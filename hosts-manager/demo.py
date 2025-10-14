#!/usr/bin/env python3
"""
Hosts 管理系统演示脚本
"""

import sys
import os
import tempfile
from pathlib import Path

# 添加 backend 目录到 Python 路径
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_path)

def demo():
    """演示 hosts 管理功能"""
    print("🚀 Hosts 文件管理系统演示")
    print("=" * 50)

    # 创建临时 hosts 文件
    with tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix='.hosts') as f:
        f.write("""# Demo hosts file
127.0.0.1       localhost
192.168.1.1     router.local
192.168.1.100   server1.local database.local
# End of file
""")
        f.flush()
        temp_hosts_path = f.name

    try:
        # 导入并使用 HostsManager
        from app import HostsManager

        print(f"📁 使用临时 hosts 文件: {temp_hosts_path}")
        manager = HostsManager(temp_hosts_path)

        # 读取现有条目
        print("\n📋 读取现有条目:")
        entries = manager.read_hosts()
        for i, entry in enumerate(entries, 1):
            print(f"  {i}. {entry['ip']} -> {entry['hostname']}")

        # 添加新条目
        print("\n➕ 添加新条目:")
        test_ip = "10.0.0.100"
        test_host = "demo.local"
        success, message = manager.add_entry(test_ip, test_host)
        print(f"  结果: {message}")

        if success:
            # 验证条目已添加
            print("\n🔍 验证新条目:")
            new_entries = manager.read_hosts()
            for entry in new_entries:
                if entry['ip'] == test_ip and entry['hostname'] == test_host:
                    print(f"  ✅ 找到新条目: {entry['ip']} -> {entry['hostname']}")

        # 删除条目
        print("\n🗑️  删除条目:")
        success, message = manager.remove_entry("192.168.1.1", "router.local")
        print(f"  结果: {message}")

        # 显示最终状态
        print("\n📊 最终条目列表:")
        final_entries = manager.read_hosts()
        for i, entry in enumerate(final_entries, 1):
            print(f"  {i}. {entry['ip']} -> {entry['hostname']}")

        # 显示统计信息
        print(f"\n📈 统计信息:")
        print(f"  总条目数: {len(final_entries)}")
        unique_ips = set(entry['ip'] for entry in final_entries)
        unique_hosts = set(entry['hostname'] for entry in final_entries)
        print(f"  唯一 IP 数: {len(unique_ips)}")
        print(f"  唯一主机名数: {len(unique_hosts)}")

        # 验证功能
        print("\n🧪 功能验证:")

        # 测试 IP 验证
        test_ips = ["192.168.1.1", "invalid.ip", "256.256.256.256"]
        for ip in test_ips:
            is_valid = manager._validate_ip(ip)
            status = "✅" if is_valid else "❌"
            print(f"  {status} IP '{ip}': {'有效' if is_valid else '无效'}")

        # 测试主机名验证
        test_hosts = ["example.local", "-invalid", "valid-host.com"]
        for host in test_hosts:
            is_valid = manager._validate_hostname(host)
            status = "✅" if is_valid else "❌"
            print(f"  {status} 主机名 '{host}': {'有效' if is_valid else '无效'}")

        print("\n✅ 演示完成！")
        print("\n📝 启动 Web 界面:")
        print("  python3 run.py")
        print("  然后访问: http://localhost:5000")

    except Exception as e:
        print(f"❌ 演示失败: {e}")
        import traceback
        traceback.print_exc()

    finally:
        # 清理临时文件
        if os.path.exists(temp_hosts_path):
            os.unlink(temp_hosts_path)
            print(f"\n🧹 已清理临时文件: {temp_hosts_path}")

        # 清理备份目录
        backup_dir = os.path.join(os.path.dirname(temp_hosts_path), 'hosts_backups')
        if os.path.exists(backup_dir):
            import shutil
            shutil.rmtree(backup_dir)
            print(f"🧹 已清理备份目录: {backup_dir}")

if __name__ == '__main__':
    demo()