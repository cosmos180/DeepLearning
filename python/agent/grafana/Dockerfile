FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖 (用于 Pillow 等)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libjpeg-dev \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件并安装
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目代码
COPY . .

# 创建日志目录
RUN mkdir -p /app/logs

# 环境变量默认值
ENV ALERT_SCHEDULE_TIME=09:00 \
    TIME_RANGE=today \
    RUN_ON_START=false \
    SCHEDULER_LOOP_INTERVAL=60 \
    PYTHONUNBUFFERED=1

# 健康检查
HEALTHCHECK --interval=60s --timeout=10s --start-period=30s --retries=3 \
    CMD python3 -c "import schedule; print('OK')" || exit 1

# 启动调度器
CMD ["python3", "scheduler.py"]
