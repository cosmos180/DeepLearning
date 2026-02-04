.PHONY: help install send send-all agent-run agent-test scheduler scheduler-once docker-build docker-up docker-down docker-logs

# 默认目标
help:
	@echo "Grafana 告警邮件发送工具"
	@echo ""
	@echo "使用方式:"
	@echo "  独立工具:"
	@echo "    python3 grafana_alert_tool.py"
	@echo "  Makefile:"
	@echo "    make send"
	@echo "  ADK Agent（对话式）:"
	@echo "    make agent-run"
	@echo ""
	@echo "常用命令:"
	@echo "  make install       # 安装依赖"
	@echo "  make send          # 发送所有平台（今天）"
	@echo "  make send-24h      # 发送所有平台（24小时）"
	@echo ""
	@echo "参数:"
	@echo "  PLATFORMS    # 指定平台（如: sdc,tpboxv3）"
	@echo "  TIME_RANGE   # 时间范围（如: 24h, 7d）"
	@echo "  RECIPIENTS   # 收件人邮箱"
	@echo ""
	@echo "示例:"
	@echo "  make send PLATFORMS=sdc,tpboxv3"
	@echo "  make send TIME_RANGE=24h"
	@echo "  make send RECIPIENTS=user@example.com"
	@echo ""

# 安装依赖
install:
	@echo "安装依赖..."
	pip3 install -q -r requirements.txt
	@echo "✅ 安装完成"

# 发送告警邮件（默认所有平台，今天）
send:
	@echo "发送告警邮件..."
	python3 grafana_alert_tool.py \
		--time-range $(or $(TIME_RANGE),today) \
		$(if $(PLATFORMS),--platforms "$(PLATFORMS)",) \
		$(if $(RECIPIENTS),--recipients "$(RECIPIENTS)",)

# 发送所有平台的告警邮件
send-all:
	@echo "发送所有平台的告警邮件..."
	python3 grafana_alert_tool.py \
		--time-range $(or $(TIME_RANGE),today) \
		$(if $(RECIPIENTS),--recipients "$(RECIPIENTS)",)

# 发送今天的数据
send-today:
	@echo "发送所有平台（今天）..."
	$(MAKE) send TIME_RANGE=today

# 发送最近24小时的数据
send-24h:
	@echo "发送所有平台（最近24小时）..."
	$(MAKE) send TIME_RANGE=24h

# 管理收件人
add-recipient:
	@echo "添加收件人: $(EMAIL)"
	python3 tools/alert_email_reporter.py add $(EMAIL)

remove-recipient:
	@echo "移除收件人: $(EMAIL)"
	python3 tools/alert_email_reporter.py remove $(EMAIL)

list-recipients:
	@echo "收件人列表:"
	python3 tools/alert_email_reporter.py list

# ADK Agent（对话式）
agent-run:
	@echo "启动 ADK Agent（对话式）..."
	@echo "提示：需要设置 ZHIPU_API_KEY 环境变量"
	cd .. && adk run grafana

# 测试 ADK Agent
agent-test:
	@echo "测试 ADK Agent..."
	@echo "python3 -c 'from grafana.root_agent import root_agent; print(root_agent)'"
	python3 -c "from grafana.root_agent import root_agent; print(root_agent)"

# =============================================================================
# 定时调度器 (Python Scheduler)
# =============================================================================

# 启动定时调度器（本地运行）
scheduler:
	@echo "启动 Grafana 告警定时调度器..."
	@echo "配置:"
	@echo "  ALERT_SCHEDULE_TIME=$(or $(ALERT_SCHEDULE_TIME),09:00)"
	@echo "  TIME_RANGE=$(or $(TIME_RANGE),today)"
	@echo "  RUN_ON_START=$(or $(RUN_ON_START),false)"
	python3 scheduler.py

# 立即执行一次（不启动调度器）
scheduler-once:
	@echo "立即执行告警发送..."
	RUN_ON_START=true ALERT_SCHEDULE_TIME=none python3 scheduler.py

# =============================================================================
# Docker 部署
# =============================================================================

# 构建 Docker 镜像
docker-build:
	@echo "构建 Docker 镜像..."
	docker-compose build

# 启动 Docker 服务（后台运行）
docker-up:
	@echo "启动 Docker 服务..."
	docker-compose up -d grafana-scheduler
	@echo ""
	@echo "查看日志: make docker-logs"
	@echo "停止服务: make docker-down"

# 停止 Docker 服务
docker-down:
	@echo "停止 Docker 服务..."
	docker-compose down

# 查看 Docker 日志
docker-logs:
	docker-compose logs -f grafana-scheduler

# Docker 手动执行一次
docker-once:
	@echo "在 Docker 中执行一次告警发送..."
	docker-compose --profile manual run --rm grafana-alert-once

# 重启 Docker 服务
docker-restart: docker-down docker-up

# =============================================================================
# 调度器配置说明
# =============================================================================

scheduler-help:
	@echo "定时调度器使用说明"
	@echo ""
	@echo "环境变量:"
	@echo "  ALERT_SCHEDULE_TIME   每天执行时间 (默认: 09:00)"
	@echo "  ALERT_INTERVAL_HOURS  按小时间隔执行 (覆盖 ALERT_SCHEDULE_TIME)"
	@echo "  TIME_RANGE            告警时间范围 (默认: today)"
	@echo "  RUN_ON_START          启动时立即执行 (默认: false)"
	@echo "  ALERT_PLATFORMS       指定平台，逗号分隔 (默认: 全部)"
	@echo ""
	@echo "本地运行示例:"
	@echo "  make scheduler                              # 默认 09:00 执行"
	@echo "  ALERT_SCHEDULE_TIME=14:30 make scheduler    # 14:30 执行"
	@echo "  ALERT_INTERVAL_HOURS=6 make scheduler       # 每6小时执行"
	@echo "  RUN_ON_START=true make scheduler            # 启动立即执行"
	@echo ""
	@echo "Docker 运行示例:"
	@echo "  make docker-build    # 构建镜像"
	@echo "  make docker-up       # 启动服务"
	@echo "  make docker-logs     # 查看日志"
	@echo "  make docker-down     # 停止服务"
