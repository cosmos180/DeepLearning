from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
import os
import ipaddress
from datetime import datetime
import logging
from typing import List, Dict, Tuple

# 获取项目根目录
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 创建 Flask 应用并配置模板和静态文件路径
app = Flask(__name__,
           template_folder=os.path.join(project_root, 'templates'),
           static_folder=os.path.join(project_root, 'static'))
app.secret_key = 'your-secret-key-here'

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class IPManager:
    def __init__(self, ip_file_path: str = None):
        self.ip_file_path = ip_file_path or os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'ip_list.txt')
        self.backup_dir = os.path.join(os.path.dirname(self.ip_file_path), 'ip_backups')
        self._ensure_backup_dir()
        self._ensure_ip_file_exists()

    def _ensure_backup_dir(self):
        """确保备份目录存在"""
        if not os.path.exists(self.backup_dir):
            try:
                os.makedirs(self.backup_dir)
            except PermissionError:
                # 如果无法在系统目录创建备份，使用用户目录
                import tempfile
                user_backup_dir = os.path.join(tempfile.gettempdir(), 'ip_backups')
                if not os.path.exists(user_backup_dir):
                    os.makedirs(user_backup_dir)
                self.backup_dir = user_backup_dir
                logger.warning(f"无法创建备份目录，使用临时目录: {self.backup_dir}")

    def _ensure_ip_file_exists(self):
        """确保 IP 文件存在"""
        if not os.path.exists(self.ip_file_path):
            try:
                with open(self.ip_file_path, 'w', encoding='utf-8') as f:
                    f.write("# IP 地址列表\n")
                    f.write("# 格式: IP地址 标识符\n")
                    f.write("# 示例: 192.168.1.1 rt2\n")
                logger.info(f"已创建 IP 文件: {self.ip_file_path}")
            except Exception as e:
                logger.error(f"创建 IP 文件失败: {e}")

    def _create_backup(self):
        """创建 IP 文件备份"""
        if os.path.exists(self.ip_file_path):
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_path = os.path.join(self.backup_dir, f'ip_list_{timestamp}.backup')
            try:
                with open(self.ip_file_path, 'r', encoding='utf-8') as src:
                    with open(backup_path, 'w', encoding='utf-8') as dst:
                        dst.write(src.read())
                logger.info(f"备份已创建: {backup_path}")
            except Exception as e:
                logger.error(f"创建备份失败: {e}")

    def _get_default_identifier(self) -> str:
        """获取默认标识符"""
        return "rt2"

    def _validate_ip(self, ip: str) -> bool:
        """验证 IP 地址格式"""
        try:
            ipaddress.ip_address(ip)
            return True
        except ValueError:
            return False

    def _parse_ip_line(self, line: str) -> Tuple[str, str]:
        """解析 IP 行，返回 (ip, identifier)"""
        parts = line.strip().split()
        if len(parts) >= 2 and self._validate_ip(parts[0]):
            return parts[0], parts[1]
        elif len(parts) == 1 and self._validate_ip(parts[0]):
            return parts[0], self._get_default_identifier()
        return None, None

    def _format_ip_line(self, ip: str, identifier: str = None) -> str:
        """格式化 IP 行"""
        if identifier is None:
            identifier = self._get_default_identifier()
        return f"{ip} {identifier}"

    def read_ip_list(self) -> List[Dict[str, str]]:
        """读取 IP 列表文件内容"""
        ip_entries = []

        if not os.path.exists(self.ip_file_path):
            logger.warning(f"IP 文件不存在: {self.ip_file_path}")
            return ip_entries

        try:
            with open(self.ip_file_path, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()

                    # 跳过空行和注释
                    if not line or line.startswith('#'):
                        continue

                    # 解析 IP 行
                    ip, identifier = self._parse_ip_line(line)
                    if ip:
                        ip_entries.append({
                            'line_num': line_num,
                            'ip': ip,
                            'identifier': identifier,
                            'full_line': line,
                            'id': len(ip_entries) + 1  # 简单的 ID 用于前端操作
                        })

        except Exception as e:
            logger.error(f"读取 IP 文件失败: {e}")

        return ip_entries

    def add_ip(self, ip: str) -> Tuple[bool, str]:
        """添加 IP 地址"""
        if not self._validate_ip(ip):
            return False, "无效的 IP 地址格式"

        # 检查是否已存在
        existing_ips = self.read_ip_list()
        for entry in existing_ips:
            if entry['ip'] == ip:
                return False, f"IP 地址已存在: {ip}"

        try:
            # 创建备份
            self._create_backup()

            # 添加新 IP（带默认标识符）
            ip_line = self._format_ip_line(ip)

            # 检查文件末尾是否有换行符，避免多余的空行
            with open(self.ip_file_path, 'rb') as f:
                f.seek(-1, 2)  # 移到文件末尾
                last_char = f.read(1)

            with open(self.ip_file_path, 'a', encoding='utf-8') as f:
                # 如果文件末尾不是换行符，先添加换行符
                if last_char != b'\n':
                    f.write('\n')
                # 添加IP行（只加一个换行符）
                f.write(f"{ip_line}\n")

            logger.info(f"已添加 IP 地址: {ip_line}")
            return True, f"成功添加 IP 地址: {ip}"

        except Exception as e:
            logger.error(f"添加 IP 地址失败: {e}")
            return False, f"添加失败: {str(e)}"

    def remove_ip(self, ip: str) -> Tuple[bool, str]:
        """删除 IP 地址"""
        if not os.path.exists(self.ip_file_path):
            return False, "IP 文件不存在"

        try:
            # 创建备份
            self._create_backup()

            # 读取所有行
            with open(self.ip_file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            # 查找并删除指定 IP
            found = False
            new_lines = []

            for line in lines:
                stripped_line = line.strip()
                if stripped_line and not stripped_line.startswith('#'):
                    # 解析这一行的 IP 地址
                    line_ip, _ = self._parse_ip_line(stripped_line)
                    if line_ip == ip:
                        found = True
                        continue  # 跳过这一行（删除）

                new_lines.append(line)

            if not found:
                return False, f"未找到 IP 地址: {ip}"

            # 写回文件
            with open(self.ip_file_path, 'w', encoding='utf-8') as f:
                f.writelines(new_lines)

            logger.info(f"已删除 IP 地址: {ip}")
            return True, f"成功删除 IP 地址: {ip}"

        except Exception as e:
            logger.error(f"删除 IP 地址失败: {e}")
            return False, f"删除失败: {str(e)}"

# 创建 IP 管理器实例
ip_manager = IPManager()

@app.route('/')
def index():
    """主页 - 显示所有 IP 地址"""
    entries = ip_manager.read_ip_list()
    return render_template('index.html', entries=entries)

@app.route('/api/entries')
def get_entries():
    """API: 获取所有 IP 地址"""
    entries = ip_manager.read_ip_list()
    return jsonify(entries)

@app.route('/api/add', methods=['POST'])
def add_entry():
    """API: 添加 IP 地址"""
    data = request.get_json()
    ip = data.get('ip', '').strip()

    if not ip:
        return jsonify({'success': False, 'message': 'IP 地址不能为空'})

    success, message = ip_manager.add_ip(ip)
    return jsonify({'success': success, 'message': message})

@app.route('/api/remove', methods=['POST'])
def remove_entry():
    """API: 删除 IP 地址"""
    data = request.get_json()
    ip = data.get('ip', '').strip()

    if not ip:
        return jsonify({'success': False, 'message': 'IP 地址不能为空'})

    success, message = ip_manager.remove_ip(ip)
    return jsonify({'success': success, 'message': message})

@app.route('/health')
def health_check():
    """健康检查端点"""
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

if __name__ == '__main__':
    print("🚀 启动 IP 地址管理系统...")
    print(f"📁 IP 文件路径: {ip_manager.ip_file_path}")
    print(f"💾 备份目录: {ip_manager.backup_dir}")
    print("🌐 访问地址: http://localhost:5000")

    try:
        app.run(host='0.0.0.0', port=5000, debug=True)
    except Exception as e:
        logger.error(f"启动失败: {e}")
        print(f"❌ 启动失败: {e}")
        print("💡 提示: 请检查文件权限")