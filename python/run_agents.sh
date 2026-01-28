#!/bin/bash
# Agent 启动脚本

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

case "${1:-help}" in
  aqi)
    adk run agent/aqi
    ;;
  grafana)
    adk run agent/grafana
    ;;
  receipt)
    adk run agent/receipt_agent
    ;;
  *)
    echo "用法: $0 {aqi|grafana|receipt}"
    echo ""
    echo "示例:"
    echo "  $0 aqi      # 启动 AQI Agent"
    echo "  $0 grafana  # 启动 Grafana Agent"
    echo "  $0 receipt  # 启动收据管理 Agent"
    ;;
esac
