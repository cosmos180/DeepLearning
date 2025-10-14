FROM python:3.9-slim

LABEL maintainer="IP Management System"
LABEL description="IP Address Management System"
LABEL version="1.0"

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV FLASK_ENV=production
ENV FLASK_APP=backend.app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装 Python 依赖
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 复制应用文件
COPY backend/ ./backend/
COPY static/ ./static/
COPY templates/ ./templates/
COPY run.py .

# 创建必要目录和数据文件
RUN mkdir -p ip_backups && \
    echo "# IP 地址列表" > ip_list.txt && \
    echo "# 每行一个 IP 地址" >> ip_list.txt && \
    echo "# 示例: 192.168.1.1" >> ip_list.txt && \
    echo "" >> ip_list.txt && \
    echo "127.0.0.1" >> ip_list.txt && \
    echo "192.168.1.1" >> ip_list.txt

# 设置权限
RUN chmod +x run.py

# 暴露端口
EXPOSE 5000

# 创建非 root 用户
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app
USER appuser

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# 启动命令
CMD ["python", "run.py", "--host", "0.0.0.0", "--port", "5000"]