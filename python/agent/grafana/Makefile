.PHONY: help install send send-all agent-run agent-test

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
