# 🚀 IP 地址管理系统部署指南

本文档详细说明如何将 IP 地址管理系统部署到不同的服务器环境。

## 📋 目录

- [快速部署](#快速部署)
- [手动部署](#手动部署)
- [生产环境部署](#生产环境部署)
- [Docker 部署](#docker-部署)
- [Nginx 反向代理](#nginx-反向代理)
- [SSL 证书配置](#ssl-证书配置)
- [故障排除](#故障排除)

## 🚀 快速部署

### 使用部署工具（推荐）

1. **创建部署包**
```bash
# 在源码目录运行
python deploy.py --archive
```

2. **上传到服务器**
```bash
# 上传生成的压缩包到服务器
scp ip_manager_deploy.tar.gz user@server:/path/to/deploy/
```

3. **在服务器上部署**
```bash
# 解压
tar -xzf ip_manager_deploy.tar.gz
cd ip_manager_deploy

# 运行部署脚本
./deploy.sh  # Linux/Mac
# 或
deploy.bat   # Windows
```

4. **启动服务**
```bash
./start.sh  # Linux/Mac
# 或
start.bat   # Windows
```

## 🔧 手动部署

### 系统要求

- Python 3.6+
- 2GB+ RAM
- 100MB+ 磁盘空间
- 网络访问权限

### Linux/Mac 部署

1. **上传文件**
```bash
# 将以下文件上传到服务器
# - backend/
# - static/
# - templates/
# - requirements.txt
# - run.py
# - ip_list.txt
```

2. **创建虚拟环境**
```bash
python3 -m venv venv
source venv/bin/activate
```

3. **安装依赖**
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

4. **设置权限**
```bash
chmod +x run.py
mkdir -p ip_backups
```

5. **启动服务**
```bash
python run.py
```

### Windows 部署

1. **上传文件**（同 Linux）

2. **创建虚拟环境**
```cmd
python -m venv venv
venv\Scripts\activate.bat
```

3. **安装依赖**
```cmd
pip install --upgrade pip
pip install -r requirements.txt
```

4. **创建备份目录**
```cmd
mkdir ip_backups
```

5. **启动服务**
```cmd
python run.py
```

## 🏭 生产环境部署

### 使用 systemd 服务（Linux）

1. **创建服务文件**
```bash
sudo nano /etc/systemd/system/ip-manager.service
```

2. **服务配置**
```ini
[Unit]
Description=IP Address Management System
After=network.target

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/path/to/ip_manager_deploy
Environment=PATH=/path/to/ip_manager_deploy/venv/bin
ExecStart=/path/to/ip_manager_deploy/venv/bin/python run.py --host 0.0.0.0 --port 5000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

3. **启动服务**
```bash
sudo systemctl daemon-reload
sudo systemctl enable ip-manager
sudo systemctl start ip-manager
sudo systemctl status ip-manager
```

### 使用 Supervisor

1. **安装 Supervisor**
```bash
sudo apt install supervisor  # Ubuntu/Debian
sudo yum install supervisor  # CentOS/RHEL
```

2. **创建配置文件**
```bash
sudo nano /etc/supervisor/conf.d/ip-manager.conf
```

3. **配置内容**
```ini
[program:ip-manager]
command=/path/to/ip_manager_deploy/venv/bin/python run.py
directory=/path/to/ip_manager_deploy
user=www-data
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/ip-manager.log
```

4. **启动服务**
```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start ip-manager
```

## 🐳 Docker 部署

### 1. 创建 Dockerfile

```dockerfile
FROM python:3.9-slim

WORKDIR /app

# 复制依赖文件
COPY requirements.txt .

# 安装依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用文件
COPY . .

# 创建必要目录
RUN mkdir -p ip_backups

# 设置权限
RUN chmod +x run.py

# 暴露端口
EXPOSE 5000

# 设置环境变量
ENV FLASK_ENV=production

# 启动命令
CMD ["python", "run.py", "--host", "0.0.0.0", "--port", "5000"]
```

### 2. 创建 docker-compose.yml

```yaml
version: '3.8'

services:
  ip-manager:
    build: .
    ports:
      - "5000:5000"
    volumes:
      - ./ip_list.txt:/app/ip_list.txt
      - ./ip_backups:/app/ip_backups
    restart: unless-stopped
    environment:
      - FLASK_ENV=production
      - FLASK_HOST=0.0.0.0
      - FLASK_PORT=5000

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - ip-manager
    restart: unless-stopped
```

### 3. 部署命令

```bash
# 构建并启动
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

## 🌐 Nginx 反向代理

### 安装 Nginx

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install nginx

# CentOS/RHEL
sudo yum install nginx
```

### 配置 Nginx

创建配置文件 `/etc/nginx/sites-available/ip-manager`:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # 静态文件直接服务
    location /static/ {
        alias /path/to/ip_manager_deploy/static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # 安全头
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
}
```

启用配置：
```bash
sudo ln -s /etc/nginx/sites-available/ip-manager /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## 🔒 SSL 证书配置

### 使用 Let's Encrypt（免费）

1. **安装 Certbot**
```bash
sudo apt install certbot python3-certbot-nginx
```

2. **获取证书**
```bash
sudo certbot --nginx -d your-domain.com
```

3. **自动续期**
```bash
sudo crontab -e
# 添加以下行
0 12 * * * /usr/bin/certbot renew --quiet
```

### 使用自签名证书

1. **生成证书**
```bash
sudo mkdir -p /etc/nginx/ssl
sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout /etc/nginx/ssl/nginx-selfsigned.key \
    -out /etc/nginx/ssl/nginx-selfsigned.crt
```

2. **更新 Nginx 配置**
```nginx
server {
    listen 443 ssl;
    server_name your-domain.com;

    ssl_certificate /etc/nginx/ssl/nginx-selfsigned.crt;
    ssl_certificate_key /etc/nginx/ssl/nginx-selfsigned.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;

    location / {
        proxy_pass http://127.0.0.1:5000;
        # ... 其他配置
    }
}
```

## 🔧 环境配置

### 环境变量配置

创建 `.env` 文件：
```bash
# 服务器配置
FLASK_ENV=production
FLASK_HOST=0.0.0.0
FLASK_PORT=5000

# 数据文件配置
IP_FILE_PATH=/path/to/ip_list.txt
BACKUP_DIR=/path/to/ip_backups

# 日志配置
LOG_LEVEL=INFO
```

### 防火墙配置

```bash
# Ubuntu (UFW)
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw enable

# CentOS/RHEL (firewalld)
sudo firewall-cmd --permanent --add-service=ssh
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --reload
```

## 📊 监控和日志

### 日志管理

```bash
# 查看应用日志
tail -f /var/log/ip-manager.log

# 查看 Nginx 日志
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log

# 查看 systemd 日志
journalctl -u ip-manager -f
```

### 健康检查

```bash
# 本地健康检查
curl http://localhost:5000/health

# 远程健康检查
curl http://your-domain.com/health
```

## 🔧 故障排除

### 常见问题

1. **端口被占用**
```bash
# 查看端口占用
sudo netstat -tulpn | grep :5000
# 或
sudo lsof -i :5000

# 杀死进程
sudo kill -9 <PID>
```

2. **权限问题**
```bash
# 修改文件所有者
sudo chown -R www-data:www-data /path/to/ip_manager_deploy

# 修改权限
sudo chmod -R 755 /path/to/ip_manager_deploy
```

3. **Python 依赖问题**
```bash
# 重新安装依赖
pip install --force-reinstall -r requirements.txt

# 检查依赖
pip check
```

4. **服务无法启动**
```bash
# 检查服务状态
sudo systemctl status ip-manager

# 查看详细日志
sudo journalctl -u ip-manager -n 50
```

### 性能优化

1. **启用 Gzip 压缩**
```nginx
# 在 Nginx 配置中添加
gzip on;
gzip_types text/plain text/css application/json application/javascript;
```

2. **设置缓存头**
```nginx
location /static/ {
    expires 30d;
    add_header Cache-Control "public, immutable";
}
```

3. **使用 Gunicorn（生产环境）**
```bash
# 安装 Gunicorn
pip install gunicorn

# 启动 Gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 "backend.app:app"
```

## 📞 支持

如果在部署过程中遇到问题，请：

1. 检查日志文件
2. 验证系统要求
3. 确认网络连接
4. 查看防火墙设置
5. 检查权限配置

部署完成后，您可以通过以下地址访问系统：
- HTTP: http://your-domain.com
- HTTPS: https://your-domain.com (如果配置了 SSL)