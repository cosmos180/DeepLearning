#!/bin/bash
# ElastAlert2 启动脚本
# ElastAlert2 Startup Script for ELK Monitoring

set -e

# 配置变量
MONITORING_DIR="/home/bughero/Documents/github/DeepLearning/python/mcp/grafana/monitoring"
CONFIG_FILE="${MONITORING_DIR}/config/elastalert.yaml"
RULES_DIR="${MONITORING_DIR}/elastalert_rules"
ALERTS_DIR="${MONITORING_DIR}/alerts"
PYTHON_CMD="python3.12"

# 颜色输出
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

# 检查配置文件
check_config() {
    if [ ! -f "$CONFIG_FILE" ]; then
        log_error "配置文件不存在: $CONFIG_FILE"
        exit 1
    fi

    if [ ! -d "$RULES_DIR" ]; then
        log_error "规则目录不存在: $RULES_DIR"
        exit 1
    fi

    # 创建告警输出目录
    mkdir -p "$ALERTS_DIR"
}

# 测试模式 - 运行单个规则并输出到文件
test_rule() {
    local rule_file="$1"

    if [ ! -f "$rule_file" ]; then
        log_error "规则文件不存在: $rule_file"
        exit 1
    fi

    log_info "测试规则: $rule_file"
    log_info "配置文件: $CONFIG_FILE"

    # 禁用代理
    unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY

    # 运行测试
    $PYTHON_CMD -c "
import sys
sys.path.insert(0, '${MONITORING_DIR}/alerters')
from elastalert.test_rule import main
main()
" "$rule_file" --config "$CONFIG_FILE" --days 1
}

# 运行 ElastAlert
run_elastalert() {
    local verbose="${1:-}"

    check_config

    log_info "启动 ElastAlert2..."
    log_info "配置: $CONFIG_FILE"
    log_info "规则目录: $RULES_DIR"
    log_info "告警输出: $ALERTS_DIR"

    # 禁用代理
    unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY

    # 运行 ElastAlert
    if [ -n "$verbose" ]; then
        $PYTHON_CMD -c "from elastalert.elastalert import main; main()" \
            --config "$CONFIG_FILE" --verbose
    else
        $PYTHON_CMD -c "from elastalert.elastalert import main; main()" \
            --config "$CONFIG_FILE"
    fi
}

# 创建索引
create_index() {
    log_info "创建 ElastAlert 索引..."

    unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY

    $PYTHON_CMD -c "from elastalert.create_index import main; main()" \
        --host 172.26.2.88 \
        --port 39202 \
        --no-ssl \
        --index elastalert_status \
        --alias elastalert_alerts \
        --old-index "" 2>&1 | grep -v "Enter optional"
}

# 显示帮助
show_help() {
    cat << EOF
ElastAlert2 管理脚本

用法:
    $0 [命令] [参数]

命令:
    run [verbose]    启动 ElastAlert 服务
    test <rule>       测试单个规则
    create-index     创建 Elasticsearch 索引
    help             显示此帮助信息

示例:
    $0 run                    # 启动服务
    $0 run verbose            # 启动服务（详细模式）
    $0 test error_rules/go_log_errors.yaml  # 测试规则
    $0 create-index          # 创建索引

环境变量:
    MONITORING_DIR    监控目录（默认: $MONITORING_DIR）
    CONFIG_FILE       配置文件（默认: $CONFIG_FILE）
EOF
}

# 主函数
main() {
    local command="${1:-help}"
    shift || true

    case "$command" in
        run)
            run_elastalert "$@"
            ;;
        test)
            if [ -z "$1" ]; then
                log_error "请指定规则文件"
                exit 1
            fi
            test_rule "$@"
            ;;
        create-index)
            create_index
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            log_error "未知命令: $command"
            show_help
            exit 1
            ;;
    esac
}

main "$@"
