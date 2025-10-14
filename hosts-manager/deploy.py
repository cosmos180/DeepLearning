#!/usr/bin/env python3
"""
IP 地址管理系统部署脚本
"""

import os
import sys
import shutil
import subprocess
import argparse
from pathlib import Path

class Deployer:
    def __init__(self, target_dir=None):
        self.source_dir = Path(__file__).parent
        self.target_dir = Path(target_dir) if target_dir else Path("ip_manager_deploy")
        self.python_cmd = "python3"

    def create_package(self):
        """创建部署包"""
        print("📦 创建部署包...")

        # 创建目标目录
        if self.target_dir.exists():
            shutil.rmtree(self.target_dir)
        self.target_dir.mkdir(parents=True)

        # 要复制的文件和目录
        files_to_copy = [
            "backend/",
            "static/",
            "templates/",
            "requirements.txt",
            "run.py",
            "README.md",
            "ip_list.txt"  # 示例数据文件
        ]

        # 复制文件
        for item in files_to_copy:
            src = self.source_dir / item
            dst = self.target_dir / item

            if src.is_dir():
                shutil.copytree(src, dst)
            else:
                shutil.copy2(src, dst)

        # 创建部署脚本
        self._create_deploy_scripts()

        # 创建配置文件
        self._create_config_files()

        print(f"✅ 部署包已创建: {self.target_dir}")
        return True

    def _create_deploy_scripts(self):
        """创建部署脚本"""
        # Linux/Mac 部署脚本
        deploy_sh = f"""#!/bin/bash
# IP 地址管理系统部署脚本

set -e

echo "🚀 开始部署 IP 地址管理系统..."

# 检查 Python 版本
echo "📋 检查 Python 版本..."
if ! command -v {self.python_cmd} &> /dev/null; then
    echo "❌ 错误: 未找到 {self.python_cmd}"
    exit 1
fi

PYTHON_VERSION=$({self.python_cmd} -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo "✅ Python 版本: $PYTHON_VERSION"

# 创建虚拟环境
echo "🔧 创建虚拟环境..."
{self.python_cmd} -m venv venv
source venv/bin/activate

# 安装依赖
echo "📦 安装依赖..."
pip install --upgrade pip
pip install -r requirements.txt

# 设置权限
echo "🔐 设置文件权限..."
chmod +x run.py

# 创建数据文件
if [ ! -f "ip_list.txt" ]; then
    echo "📄 创建示例数据文件..."
    cat > ip_list.txt << 'EOF'
# IP 地址列表
# 格式: IP地址 标识符
# 示例: 192.168.1.1 rt2

10.100.35.150 rt2
10.100.35.151 rt2
10.100.35.152 rt2
EOF
fi

# 创建备份目录
mkdir -p ip_backups

echo "✅ 部署完成！"
echo ""
echo "📝 启动命令:"
echo "  source venv/bin/activate"
echo "  python run.py"
echo ""
echo "🌐 访问地址: http://localhost:5000"
echo ""
echo "🛑 停止服务: 按 Ctrl+C"
"""

        # Windows 部署脚本
        deploy_bat = """@echo off
REM IP 地址管理系统部署脚本

echo 🚀 开始部署 IP 地址管理系统...

REM 检查 Python 版本
echo 📋 检查 Python 版本...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误: 未找到 Python
    pause
    exit /b 1
)

echo ✅ Python 已安装

REM 创建虚拟环境
echo 🔧 创建虚拟环境...
python -m venv venv
call venv\\Scripts\\activate.bat

REM 安装依赖
echo 📦 安装依赖...
pip install --upgrade pip
pip install -r requirements.txt

REM 创建数据文件
if not exist "ip_list.txt" (
    echo 📄 创建示例数据文件...
    (
        echo # IP 地址列表
        echo # 格式: IP地址 标识符
        echo # 示例: 192.168.1.1 rt2
        echo.
        echo 10.100.35.150 rt2
        echo 10.100.35.151 rt2
        echo 10.100.35.152 rt2
    ) > ip_list.txt
)

REM 创建备份目录
if not exist "ip_backups" mkdir ip_backups

echo ✅ 部署完成！
echo.
echo 📝 启动命令:
echo   venv\\Scripts\\activate.bat
echo   python run.py
echo.
echo 🌐 访问地址: http://localhost:5000
echo.
echo 🛑 停止服务: 按 Ctrl+C
pause
"""

        # 写入脚本文件
        with open(self.target_dir / "deploy.sh", "w", encoding="utf-8") as f:
            f.write(deploy_sh)
        os.chmod(self.target_dir / "deploy.sh", 0o755)

        with open(self.target_dir / "deploy.bat", "w", encoding="utf-8") as f:
            f.write(deploy_bat)

        # 创建快速启动脚本
        start_sh = f"""#!/bin/bash
# IP 地址管理系统启动脚本

cd "$(dirname "$0")"

if [ ! -d "venv" ]; then
    echo "❌ 虚拟环境不存在，请先运行 ./deploy.sh"
    exit 1
fi

source venv/bin/activate
python run.py "$@"
"""

        start_bat = """@echo off
cd /d "%~dp0"

if not exist "venv" (
    echo ❌ 虚拟环境不存在，请先运行 deploy.bat
    pause
    exit /b 1
)

call venv\\Scripts\\activate.bat
python run.py %*
pause
"""

        with open(self.target_dir / "start.sh", "w", encoding="utf-8") as f:
            f.write(start_sh)
        os.chmod(self.target_dir / "start.sh", 0o755)

        with open(self.target_dir / "start.bat", "w", encoding="utf-8") as f:
            f.write(start_bat)

    def _create_config_files(self):
        """创建配置文件"""
        # 环境配置
        config_env = """# IP 地址管理系统环境配置

# 服务器配置
FLASK_ENV=production
FLASK_HOST=0.0.0.0
FLASK_PORT=5000

# 数据文件配置
IP_FILE_PATH=ip_list.txt
BACKUP_DIR=ip_backups

# 日志配置
LOG_LEVEL=INFO
"""

        with open(self.target_dir / ".env", "w", encoding="utf-8") as f:
            f.write(config_env)

        # systemd 服务文件
        service_content = f"""[Unit]
Description=IP Address Management System
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory={self.target_dir.absolute()}
Environment=PATH={self.target_dir.absolute()}/venv/bin
ExecStart={self.target_dir.absolute()}/venv/bin/python run.py --host 0.0.0.0 --port 5000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
"""

        # 创建 systemd 目录
        systemd_dir = self.target_dir / "systemd"
        systemd_dir.mkdir(exist_ok=True)

        with open(systemd_dir / "ip-manager.service", "w", encoding="utf-8") as f:
            f.write(service_content)

    def create_archive(self):
        """创建压缩包"""
        print("📁 创建压缩包...")

        archive_name = f"ip_manager_{os.path.basename(self.target_dir)}"

        # 创建 tar.gz 文件
        shutil.make_archive(
            base_name=archive_name,
            format='gztar',
            root_dir=self.target_dir.parent,
            base_dir=self.target_dir.name
        )

        print(f"✅ 压缩包已创建: {archive_name}.tar.gz")
        return f"{archive_name}.tar.gz"

def main():
    parser = argparse.ArgumentParser(description='IP 地址管理系统部署工具')
    parser.add_argument('--target', '-t', help='部署目标目录', default='ip_manager_deploy')
    parser.add_argument('--archive', '-a', action='store_true', help='创建压缩包')
    parser.add_argument('--python', '-p', help='Python 命令', default='python3')

    args = parser.parse_args()

    print("🚀 IP 地址管理系统部署工具")
    print("=" * 50)

    deployer = Deployer(args.target)
    deployer.python_cmd = args.python

    # 创建部署包
    if deployer.create_package():
        print("\n📋 部署包内容:")
        for item in deployer.target_dir.rglob("*"):
            if item.is_file():
                rel_path = item.relative_to(deployer.target_dir)
                print(f"  📄 {rel_path}")

        # 创建压缩包
        if args.archive:
            archive_path = deployer.create_archive()
            print(f"\n📦 压缩包: {archive_path}")

        print(f"\n✅ 部署准备完成！")
        print(f"\n📁 部署目录: {deployer.target_dir.absolute()}")
        print(f"\n📝 部署说明:")
        print(f"  1. 将 {deployer.target_dir.name} 目录复制到目标服务器")
        print(f"  2. 运行 ./deploy.sh (Linux/Mac) 或 deploy.bat (Windows)")
        print(f"  3. 使用 ./start.sh 或 start.bat 启动服务")

if __name__ == '__main__':
    main()