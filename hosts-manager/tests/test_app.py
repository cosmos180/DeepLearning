#!/usr/bin/env python3
"""
Hosts 管理系统测试用例
"""

import unittest
import tempfile
import os
import sys
import json
from pathlib import Path

# 添加 backend 目录到 Python 路径
backend_path = os.path.join(os.path.dirname(__file__), '..', 'backend')
sys.path.insert(0, backend_path)

from app import HostsManager, app

class TestHostsManager(unittest.TestCase):
    """Hosts 管理器测试类"""

    def setUp(self):
        """测试前准备"""
        # 创建临时 hosts 文件
        self.temp_hosts = tempfile.NamedTemporaryFile(mode='w+', delete=False)
        self.temp_hosts.write("""# Test hosts file
127.0.0.1       localhost
192.168.1.1     router.local
192.168.1.100   server1.local server1
# Another comment
10.0.0.1        database.local
""")
        self.temp_hosts.flush()
        self.temp_hosts.close()

        # 创建 HostsManager 实例
        self.manager = HostsManager(self.temp_hosts.name)

    def tearDown(self):
        """测试后清理"""
        # 删除临时文件
        if os.path.exists(self.temp_hosts.name):
            os.unlink(self.temp_hosts.name)

        # 清理备份目录
        backup_dir = os.path.join(os.path.dirname(self.temp_hosts.name), 'hosts_backups')
        if os.path.exists(backup_dir):
            import shutil
            shutil.rmtree(backup_dir)

    def test_read_hosts(self):
        """测试读取 hosts 文件"""
        entries = self.manager.read_hosts()

        self.assertEqual(len(entries), 4)

        # 检查第一条目
        self.assertEqual(entries[0]['ip'], '127.0.0.1')
        self.assertEqual(entries[0]['hostname'], 'localhost')

        # 检查多主机名条目
        server_entries = [e for e in entries if e['ip'] == '192.168.1.100']
        self.assertEqual(len(server_entries), 2)
        self.assertIn(server_entries[0]['hostname'], ['server1.local', 'server1'])

    def test_validate_ip(self):
        """测试 IP 地址验证"""
        # 有效的 IPv4 地址
        self.assertTrue(self.manager._validate_ip('192.168.1.1'))
        self.assertTrue(self.manager._validate_ip('127.0.0.1'))
        self.assertTrue(self.manager._validate_ip('255.255.255.255'))
        self.assertTrue(self.manager._validate_ip('0.0.0.0'))

        # 有效的 IPv6 地址（简单测试）
        self.assertTrue(self.manager._validate_ip('::1'))
        self.assertTrue(self.manager._validate_ip('2001:db8::1'))

        # 无效的 IP 地址
        self.assertFalse(self.manager._validate_ip('256.256.256.256'))
        self.assertFalse(self.manager._validate_ip('192.168.1'))
        self.assertFalse(self.manager._validate_ip('not.an.ip'))
        self.assertFalse(self.manager._validate_ip(''))
        self.assertFalse(self.manager._validate_ip('192.168.1.1.1'))

    def test_validate_hostname(self):
        """测试主机名验证"""
        # 有效的主机名
        self.assertTrue(self.manager._validate_hostname('localhost'))
        self.assertTrue(self.manager._validate_hostname('example.com'))
        self.assertTrue(self.manager._validate_hostname('server.local'))
        self.assertTrue(self.manager._validate_hostname('test-server-01'))
        self.assertTrue(self.manager._validate_hostname('a'))

        # 无效的主机名
        self.assertFalse(self.manager._validate_hostname(''))
        self.assertFalse(self.manager._validate_hostname('-invalid'))
        self.assertFalse(self.manager._validate_hostname('invalid-'))
        self.assertFalse(self.manager._validate_hostname('..invalid'))
        self.assertFalse(self.manager._validate_hostname('invalid..com'))
        self.assertFalse(self.manager._validate_hostname('invalid..'))

    def test_add_entry(self):
        """测试添加条目"""
        # 添加新条目
        success, message = self.manager.add_entry('192.168.1.200', 'newhost.local')
        self.assertTrue(success)
        self.assertIn('成功添加', message)

        # 验证条目已添加
        entries = self.manager.read_hosts()
        new_entries = [e for e in entries if e['ip'] == '192.168.1.200' and e['hostname'] == 'newhost.local']
        self.assertEqual(len(new_entries), 1)

        # 尝试添加重复条目
        success, message = self.manager.add_entry('192.168.1.200', 'newhost.local')
        self.assertFalse(success)
        self.assertIn('已存在', message)

        # 测试无效 IP
        success, message = self.manager.add_entry('invalid.ip', 'test.local')
        self.assertFalse(success)
        self.assertIn('无效的 IP', message)

        # 测试无效主机名
        success, message = self.manager.add_entry('192.168.1.201', '')
        self.assertFalse(success)
        self.assertIn('无效的主机名', message)

    def test_remove_entry(self):
        """测试删除条目"""
        # 删除存在的条目
        success, message = self.manager.remove_entry('192.168.1.1', 'router.local')
        self.assertTrue(success)
        self.assertIn('成功删除', message)

        # 验证条目已删除
        entries = self.manager.read_hosts()
        removed_entries = [e for e in entries if e['ip'] == '192.168.1.1' and e['hostname'] == 'router.local']
        self.assertEqual(len(removed_entries), 0)

        # 尝试删除不存在的条目
        success, message = self.manager.remove_entry('192.168.1.999', 'nonexistent.local')
        self.assertFalse(success)
        self.assertIn('未找到条目', message)

    def test_backup_creation(self):
        """测试备份创建"""
        initial_backup_count = len(os.listdir(self.manager.backup_dir)) if os.path.exists(self.manager.backup_dir) else 0

        # 添加条目应该创建备份
        self.manager.add_entry('192.168.1.201', 'backup-test.local')

        # 检查备份是否创建
        self.assertTrue(os.path.exists(self.manager.backup_dir))
        new_backup_count = len(os.listdir(self.manager.backup_dir))
        self.assertEqual(new_backup_count, initial_backup_count + 1)


class TestFlaskApp(unittest.TestCase):
    """Flask 应用测试类"""

    def setUp(self):
        """测试前准备"""
        # 创建临时 hosts 文件
        self.temp_hosts = tempfile.NamedTemporaryFile(mode='w+', delete=False)
        self.temp_hosts.write("""127.0.0.1       localhost
192.168.1.1     test.local
""")
        self.temp_hosts.flush()
        self.temp_hosts.close()

        # 配置 Flask 测试环境
        app.config['TESTING'] = True
        self.client = app.test_client()

        # 替换 HostsManager 实例
        from app import hosts_manager
        hosts_manager.hosts_path = self.temp_hosts.name
        hosts_manager._ensure_backup_dir()

    def tearDown(self):
        """测试后清理"""
        if os.path.exists(self.temp_hosts.name):
            os.unlink(self.temp_hosts.name)

        # 清理备份目录
        backup_dir = os.path.join(os.path.dirname(self.temp_hosts.name), 'hosts_backups')
        if os.path.exists(backup_dir):
            import shutil
            shutil.rmtree(backup_dir)

    def test_index_page(self):
        """测试主页"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Hosts', response.data)

    def test_api_get_entries(self):
        """测试获取条目 API"""
        response = self.client.get('/api/entries')
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data)
        self.assertIsInstance(data, list)
        self.assertGreater(len(data), 0)

        # 检查返回的数据结构
        entry = data[0]
        self.assertIn('ip', entry)
        self.assertIn('hostname', entry)
        self.assertIn('line_num', entry)

    def test_api_add_entry(self):
        """测试添加条目 API"""
        # 添加有效条目
        response = self.client.post('/api/add',
                                   json={'ip': '192.168.1.100', 'hostname': 'api-test.local'},
                                   content_type='application/json')
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertIn('成功添加', data['message'])

        # 测试无效数据
        response = self.client.post('/api/add',
                                   json={'ip': 'invalid.ip', 'hostname': 'test.local'},
                                   content_type='application/json')
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data)
        self.assertFalse(data['success'])

    def test_api_remove_entry(self):
        """测试删除条目 API"""
        # 删除存在的条目
        response = self.client.post('/api/remove',
                                   json={'ip': '192.168.1.1', 'hostname': 'test.local'},
                                   content_type='application/json')
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertIn('成功删除', data['message'])

        # 尝试删除不存在的条目
        response = self.client.post('/api/remove',
                                   json={'ip': '192.168.1.999', 'hostname': 'nonexistent.local'},
                                   content_type='application/json')
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data)
        self.assertFalse(data['success'])

    def test_health_check(self):
        """测试健康检查端点"""
        response = self.client.get('/health')
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data)
        self.assertIn('status', data)
        self.assertIn('timestamp', data)
        self.assertEqual(data['status'], 'healthy')


class TestValidation(unittest.TestCase):
    """验证功能测试类"""

    def setUp(self):
        """测试前准备"""
        self.manager = HostsManager()

    def test_ip_validation_edge_cases(self):
        """测试 IP 验证的边界情况"""
        # 边界值测试
        valid_ips = [
            '0.0.0.0',
            '255.255.255.255',
            '1.2.3.4',
            '192.168.0.1',
            '10.0.0.1'
        ]

        for ip in valid_ips:
            with self.subTest(ip=ip):
                self.assertTrue(self.manager._validate_ip(ip), f"{ip} should be valid")

        invalid_ips = [
            '256.0.0.1',
            '192.168.1',
            '192.168.1.1.1',
            '192.168.1.-1',
            '',
            'abc.def.ghi.jkl'
        ]

        for ip in invalid_ips:
            with self.subTest(ip=ip):
                self.assertFalse(self.manager._validate_ip(ip), f"{ip} should be invalid")

    def test_hostname_validation_edge_cases(self):
        """测试主机名验证的边界情况"""
        # 边界值测试
        valid_hostnames = [
            'a',
            'ab',
            'test',
            'test123',
            'test-server',
            'test.server',
            'test-server-01.domain.com'
        ]

        for hostname in valid_hostnames:
            with self.subTest(hostname=hostname):
                self.assertTrue(self.manager._validate_hostname(hostname), f"{hostname} should be valid")

        invalid_hostnames = [
            '',
            '-test',
            'test-',
            '.test',
            'test.',
            'test..server',
            'test.-server',
            'test.-server.com'
        ]

        for hostname in invalid_hostnames:
            with self.subTest(hostname=hostname):
                self.assertFalse(self.manager._validate_hostname(hostname), f"{hostname} should be invalid")


def run_tests():
    """运行所有测试"""
    print("🧪 运行 Hosts 管理系统测试套件")
    print("=" * 50)

    # 创建测试套件
    test_suite = unittest.TestSuite()

    # 添加测试类
    test_classes = [TestHostsManager, TestFlaskApp, TestValidation]

    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)

    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)

    # 输出结果
    print("\n" + "=" * 50)
    print(f"测试结果: 运行 {result.testsRun} 个测试")
    print(f"成功: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"失败: {len(result.failures)}")
    print(f"错误: {len(result.errors)}")

    if result.failures:
        print("\n失败的测试:")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback}")

    if result.errors:
        print("\n错误的测试:")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback}")

    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)