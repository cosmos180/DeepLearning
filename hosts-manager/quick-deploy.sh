#!/bin/bash

# IP 地址管理系统一键部署脚本
# 支持 Linux/Ubuntu/CentOS 系统

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查是否为 root 用户
check_root() {
    if [[ $EUID -eq 0 ]]; then
        log_error "请不要以 root 用户运行此脚本"
        log_info "建议创建普通用户："
        log_info "  sudo useradd -m -s /bin/bash ipmanager"
        log_info "  sudo usermod -aG sudo ipmanager"
        log_info "  sudo su - ipmanager"
        exit 1
    fi
}

# 检测系统类型
detect_os() {
    if [[ -f /etc/os-release ]]; then
        . /etc/os-release
        OS=$NAME
        VER=$VERSION_ID
    elif type lsb_release >/dev/null 2>&1; then
        OS=$(lsb_release -si)
        VER=$(lsb_release -sr)
    else
        OS=$(uname -s)
        VER=$(uname -r)
    fi

    log_info "检测到系统: $OS $VER"
}

# 安装系统依赖
install_system_deps() {
    log_info "安装系统依赖..."

    case $OS in
        "Ubuntu"|"Debian"*)
            sudo apt update
            sudo apt install -y python3 python3-pip python3-venv nginx curl wget git
            ;;
        "CentOS"*|"Red Hat"*)
            sudo yum update -y
            sudo yum install -y python3 python3-pip nginx curl wget git
            ;;
        *)
            log_error "不支持的操作系统: $OS"
            exit 1
            ;;
    esac

    log_success "系统依赖安装完成"
}

# 创建应用目录
create_app_dir() {
    APP_DIR="/opt/ip-manager"
    log_info "创建应用目录: $APP_DIR"

    sudo mkdir -p $APP_DIR
    sudo chown $USER:$USER $APP_DIR
    cd $APP_DIR

    log_success "应用目录创建完成"
}

# 下载源码
download_source() {
    log_info "下载应用源码..."

    # 这里假设您已经将源码上传到服务器
    # 如果从 Git 仓库下载，请取消下面的注释并修改 URL
    # git clone https://github.com/your-repo/ip-manager.git .

    log_info "请确保已将源码文件复制到 $APP_DIR"
    ls -la

    if [[ ! -f "run.py" ]]; then
        log_error "未找到源码文件，请将源码复制到 $APP_DIR"
        exit 1
    fi

    log_success "源码准备完成"
}

# 创建虚拟环境
create_venv() {
    log_info "创建 Python 虚拟环境..."

    python3 -m venv venv
    source venv/bin/activate

    log_success "虚拟环境创建完成"
}

# 安装 Python 依赖
install_python_deps() {
    log_info "安装 Python 依赖..."

    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt

    # 生产环境安装额外依赖
    if [[ "$ENVIRONMENT" == "production" ]]; then
        pip install -r requirements.prod.txt
    fi

    log_success "Python 依赖安装完成"
}

# 创建配置文件
create_config() {
    log_info "创建配置文件..."

    # 创建环境配置
    cat > .env << EOF
# IP 地址管理系统环境配置
FLASK_ENV=${ENVIRONMENT:-production}
FLASK_HOST=0.0.0.0
FLASK_PORT=5000

# 数据文件配置
IP_FILE_PATH=$APP_DIR/data/ip_list.txt
BACKUP_DIR=$APP_DIR/data/ip_backups

# 日志配置
LOG_LEVEL=INFO
EOF

    # 创建数据目录
    mkdir -p data
    if [[ ! -f "data/ip_list.txt" ]]; then
        cat > data/ip_list.txt << EOF
# IP 地址列表
# 每行一个 IP 地址
# 示例: 192.168.1.1

127.0.0.1
192.168.1.1
EOF
    fi

    mkdir -p data/ip_backups

    log_success "配置文件创建完成"
}

# 创建 systemd 服务
create_systemd_service() {
    log_info "创建 systemd 服务..."

    sudo tee /etc/systemd/system/ip-manager.service > /dev/null << EOF
[Unit]
Description=IP Address Management System
After=network.target

[Service]
Type=simple
User=$USER
Group=$USER
WorkingDirectory=$APP_DIR
Environment=PATH=$APP_DIR/venv/bin
EnvironmentFile=$APP_DIR/.env
ExecStart=$APP_DIR/venv/bin/python run.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal
SyslogIdentifier=ip-manager

[Install]
WantedBy=multi-user.target
EOF

    sudo systemctl daemon-reload
    sudo systemctl enable ip-manager

    log_success "systemd 服务创建完成"
}

# 配置 Nginx
configure_nginx() {
    log_info "配置 Nginx..."

    sudo tee /etc/nginx/sites-available/ip-manager > /dev/null << EOF
server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_redirect off;
    }

    location /static/ {
        alias $APP_DIR/static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    location /health {
        proxy_pass http://127.0.0.1:5000;
        access_log off;
    }
}
EOF

    sudo rm -f /etc/nginx/sites-enabled/default
    sudo ln -s /etc/nginx/sites-available/ip-manager /etc/nginx/sites-enabled/
    sudo nginx -t

    log_success "Nginx 配置完成"
}

# 设置防火墙
setup_firewall() {
    log_info "配置防火墙..."

    if command -v ufw >/dev/null 2>&1; then
        # Ubuntu/Debian
        sudo ufw allow 22/tcp
        sudo ufw allow 80/tcp
        sudo ufw allow 443/tcp
        sudo ufw --force enable
    elif command -v firewall-cmd >/dev/null 2>&1; then
        # CentOS/RHEL
        sudo firewall-cmd --permanent --add-service=ssh
        sudo firewall-cmd --permanent --add-service=http
        sudo firewall-cmd --permanent --add-service=https
        sudo firewall-cmd --reload
    else
        log_warning "未检测到防火墙工具，请手动配置防火墙规则"
    fi

    log_success "防火墙配置完成"
}

# 启动服务
start_services() {
    log_info "启动服务..."

    # 启动应用服务
    sudo systemctl start ip-manager
    sudo systemctl status ip-manager --no-pager

    # 启动 Nginx
    sudo systemctl restart nginx
    sudo systemctl enable nginx
    sudo systemctl status nginx --no-pager

    log_success "服务启动完成"
}

# 运行健康检查
health_check() {
    log_info "运行健康检查..."

    sleep 5

    if curl -f http://localhost/health >/dev/null 2>&1; then
        log_success "健康检查通过"
    else
        log_error "健康检查失败，请检查日志"
        sudo journalctl -u ip-manager -n 20
        exit 1
    fi
}

# 显示部署信息
show_deployment_info() {
    log_success "🎉 部署完成！"
    echo
    echo "==================================="
    echo "📋 部署信息"
    echo "==================================="
    echo "📁 应用目录: $APP_DIR"
    echo "🌐 访问地址: http://$(curl -s ifconfig.me)"
    echo "🔧 管理命令:"
    echo "  查看状态: sudo systemctl status ip-manager"
    echo "  查看日志: sudo journalctl -u ip-manager -f"
    echo "  重启服务: sudo systemctl restart ip-manager"
    echo "  停止服务: sudo systemctl stop ip-manager"
    echo
    echo "📁 数据文件位置:"
    echo "  IP 列表: $APP_DIR/data/ip_list.txt"
    echo "  备份目录: $APP_DIR/data/ip_backups"
    echo
    echo "🔧 Nginx 配置: /etc/nginx/sites-available/ip-manager"
    echo "==================================="
}

# 主函数
main() {
    log_info "开始 IP 地址管理系统部署..."

    # 设置环境变量
    export ENVIRONMENT=${ENVIRONMENT:-production}

    check_root
    detect_os
    install_system_deps
    create_app_dir
    download_source
    create_venv
    install_python_deps
    create_config
    create_systemd_service
    configure_nginx
    setup_firewall
    start_services
    health_check
    show_deployment_info

    log_success "部署完成！"
}

# 脚本入口
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi