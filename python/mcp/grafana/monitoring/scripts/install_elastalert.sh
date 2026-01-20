#!/bin/bash
# ElastAlert 安装脚本
# Install ElastAlert on Ubuntu/Debian

set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 配置变量
ELASTALERT_DIR="/opt/elastalert"
ELASTALERT_VERSION="0.2.4"
PYTHON_CMD="python3"

# 日志函数
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_step() {
    echo -e "${BLUE}==>${NC} $1"
}

# 检查是否以 root 用户运行
check_root() {
    if [ "$EUID" -ne 0 ]; then
        log_error "This script must be run as root or with sudo"
        exit 1
    fi
}

# 检测系统
detect_system() {
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        OS=$ID
        OS_VERSION=$VERSION_ID
    else
        log_error "Cannot detect operating system"
        exit 1
    fi

    log_info "Detected OS: $OS $OS_VERSION"
}

# 安装系统依赖
install_system_dependencies() {
    log_step "Installing system dependencies..."

    apt-get update

    apt-get install -y \
        python3 \
        python3-pip \
        python3-dev \
        build-essential \
        libssl-dev \
        libffi-dev \
        python3-setuptools \
        git

    log_info "System dependencies installed"
}

# 安装 ElastAlert
install_elastalert() {
    log_step "Installing ElastAlert..."

    # 创建安装目录
    mkdir -p "${ELASTALERT_DIR}"

    # 克隆 ElastAlert 仓库
    if [ ! -d "${ELASTALERT_DIR}/.git" ]; then
        git clone https://github.com/Yelp/elastalert.git "${ELASTALERT_DIR}"
    else
        log_info "ElastAlert repository already exists, updating..."
        cd "${ELASTALERT_DIR}"
        git pull
    fi

    # 安装 ElastAlert
    cd "${ELASTALERT_DIR}"
    pip3 install -e .

    log_info "ElastAlert installed to ${ELASTALERT_DIR}"
}

# 安装 Python 依赖
install_python_dependencies() {
    log_step "Installing Python dependencies..."

    # ElastAlert 核心依赖
    pip3 install \
        elasticsearch>=7.0.0 \
        aws-requests-auth \
        jsonschema \
        python-dateutil \
        pytz \
        croniter \
        jinja2

    # 可选依赖（用于增强功能）
    pip3 install \
        slackclient \
        pyyaml

    log_info "Python dependencies installed"
}

# 创建 ElastAlert 用户
create_elastalert_user() {
    log_step "Creating elastalert user..."

    if ! id -u elastalert > /dev/null 2>&1; then
        useradd -r -s /bin/false -d "${ELASTALERT_DIR}" elastalert
        log_info "User 'elastalert' created"
    else
        log_info "User 'elastalert' already exists"
    fi

    # 设置目录权限
    chown -R elastalert:elastalert "${ELASTALERT_DIR}"
}

# 创建 systemd 服务
create_systemd_service() {
    log_step "Creating systemd service..."

    cat > /etc/systemd/system/elastalert.service << 'EOF'
[Unit]
Description=ElastAlert Alerting Framework
After=network.target Elasticsearch.service

[Service]
Type=simple
User=elastalert
Group=elastalert
WorkingDirectory=/opt/elastalert
ExecStart=/usr/local/bin/elastalert --verbose --config /opt/elastalert/config.yaml
Restart=always
RestartSec=10

# Security
NoNewPrivileges=true
PrivateTmp=true

[Install]
WantedBy=multi-user.target
EOF

    systemctl daemon-reload
    log_info "Systemd service created"
}

# 创建 Elasticsearch 索引模板
create_index_template() {
    log_step "Creating Elasticsearch index template..."

    cd "${ELASTALERT_DIR}"

    # 创建 ElastAlert 索引（用于存储告警状态）
    if [ -f "create_index.sh" ]; then
        chmod +x create_index.sh
        ./create_index.sh || log_warn "Failed to create index (may need Elasticsearch configuration)"
    else
        log_warn "create_index.sh not found"
    fi
}

# 显示安装后信息
show_post_install_info() {
    log_step "Installation completed!"
    echo ""
    echo -e "${GREEN}ElastAlert has been installed successfully!${NC}"
    echo ""
    echo "Next steps:"
    echo ""
    echo "1. Create configuration file:"
    echo "   cp config.yaml.example ${ELASTALERT_DIR}/config.yaml"
    echo "   nano ${ELASTALERT_DIR}/config.yaml"
    echo ""
    echo "2. Add rules to ${ELASTALERT_DIR}/rules/"
    echo ""
    echo "3. Test ElastAlert:"
    echo "   elastalert --verbose --config ${ELASTALERT_DIR}/config.yaml --rule <rule-file.yaml>"
    echo ""
    echo "4. Enable and start service:"
    echo "   systemctl enable elastalert"
    echo "   systemctl start elastalert"
    echo ""
    echo "5. Check service status:"
    echo "   systemctl status elastalert"
    echo ""
    echo "For more information, see: https://elastalert.readthedocs.io/"
}

# 主函数
main() {
    echo ""
    echo "=========================================="
    echo "  ElastAlert Installation Script"
    echo "=========================================="
    echo ""

    # 检查 root 权限
    # check_root

    # 检测系统
    detect_system

    # 安装步骤
    install_system_dependencies
    install_elastalert
    install_python_dependencies
    create_elastalert_user
    create_systemd_service
    create_index_template

    # 显示安装后信息
    show_post_install_info
}

# 运行安装
main "$@"
