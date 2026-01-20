#!/bin/bash
# ElastAlert 规则部署脚本
# Deploy ElastAlert rules to production

set -e

# 配置变量
MONITORING_DIR="/home/bughero/Documents/github/DeepLearning/python/mcp/grafana/monitoring"
RULES_DIR="${MONITORING_DIR}/elastalert_rules"
CONFIG_FILE="${MONITORING_DIR}/config/elastalert.yaml"
BACKUP_DIR="${MONITORING_DIR}/backups"

# ElastAlert 安装目录（根据实际情况修改）
ELASTALERT_DIR="/opt/elastalert"
ELASTALERT_RULES_DIR="${ELASTALERT_DIR}/rules"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

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

# 检查目录是否存在
check_directory() {
    if [ ! -d "$1" ]; then
        log_error "Directory not found: $1"
        exit 1
    fi
}

# 创建备份
create_backup() {
    local backup_name="rules_backup_$(date +%Y%m%d_%H%M%S)"
    mkdir -p "${BACKUP_DIR}"

    if [ -d "${ELASTALERT_RULES_DIR}" ]; then
        log_info "Creating backup: ${backup_name}"
        cp -r "${ELASTALERT_RULES_DIR}" "${BACKUP_DIR}/${backup_name}"
        log_info "Backup created successfully"
    else
        log_warn "No existing rules to backup"
    fi
}

# 验证规则语法
validate_rules() {
    log_info "Validating rules syntax..."
    python3 "${MONITORING_DIR}/scripts/validate_rules.py" --rules-dir "${RULES_DIR}"

    if [ $? -ne 0 ]; then
        log_error "Rule validation failed. Aborting deployment."
        exit 1
    fi

    log_info "All rules validated successfully"
}

# 同步规则文件
sync_rules() {
    log_info "Syncing rules to ${ELASTALERT_RULES_DIR}..."

    # 创建目标目录（如果不存在）
    mkdir -p "${ELASTALERT_RULES_DIR}"

    # 复制规则文件
    rsync -av --delete \
        --exclude='*.pyc' \
        --exclude='__pycache__' \
        "${RULES_DIR}/" \
        "${ELASTALERT_RULES_DIR}/"

    log_info "Rules synced successfully"
}

# 同步配置文件
sync_config() {
    log_info "Syncing configuration..."

    if [ -f "${CONFIG_FILE}" ]; then
        cp "${CONFIG_FILE}" "${ELASTALERT_DIR}/config.yaml"
        log_info "Configuration synced"
    else
        log_warn "Configuration file not found: ${CONFIG_FILE}"
    fi
}

# 重启 ElastAlert 服务
restart_elastalert() {
    log_info "Restarting ElastAlert service..."

    # 检查服务是否运行
    if systemctl is-active --quiet elastalert; then
        sudo systemctl restart elastalert
        log_info "ElastAlert service restarted"
    else
        log_warn "ElastAlert service is not running. Start it with: sudo systemctl start elastalert"
    fi
}

# 主函数
main() {
    log_info "Starting ElastAlert rules deployment..."
    log_info "Source: ${RULES_DIR}"
    log_info "Target: ${ELASTALERT_RULES_DIR}"

    # 检查目录
    check_directory "${RULES_DIR}"
    check_directory "${MONITORING_DIR}"

    # 验证规则
    validate_rules

    # 创建备份
    create_backup

    # 同步规则
    sync_rules

    # 同步配置
    sync_config

    # 重启服务
    restart_elastalert

    log_info "Deployment completed successfully!"
}

# 运行
main "$@"
