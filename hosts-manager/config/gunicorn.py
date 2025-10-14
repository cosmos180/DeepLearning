# Gunicorn 配置文件
import multiprocessing

# 服务器套接字
bind = "0.0.0.0:5000"
backlog = 2048

# 工作进程
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 50
preload_app = True

# 超时设置
timeout = 30
keepalive = 2
graceful_timeout = 30

# 日志
accesslog = "-"
errorlog = "-"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# 进程命名
proc_name = "ip-manager"

# 安全
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190