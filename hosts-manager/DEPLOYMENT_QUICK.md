# 🚀 快速部署指南

## 一分钟部署

### 方式一：使用部署工具（推荐）

```bash
# 1. 创建部署包
python deploy.py --archive

# 2. 上传到服务器
scp ip_manager_deploy.tar.gz user@server:/tmp/

# 3. 服务器上部署
cd /tmp
tar -xzf ip_manager_deploy.tar.gz
cd ip_manager_deploy
./deploy.sh
./start.sh
```

### 方式二：Docker 部署

```bash
# 1. 克隆或上传代码
git clone <repository> ip-manager
cd ip-manager

# 2. 启动服务
docker-compose up -d

# 3. 访问系统
curl http://localhost:5000/health
```

### 方式三：一键脚本部署

```bash
# 1. 上传 quick-deploy.sh 到服务器
chmod +x quick-deploy.sh

# 2. 运行部署
./quick-deploy.sh
```

## 生产环境部署

### 系统要求
- Ubuntu 18.04+ / CentOS 7+ / Debian 9+
- Python 3.6+
- 2GB+ RAM
- 10GB+ 磁盘空间

### 推荐配置

#### 小型部署（< 100 用户）
- CPU: 1 核
- RAM: 2GB
- 磁盘: 20GB SSD

#### 中型部署（100-1000 用户）
- CPU: 2 核
- RAM: 4GB
- 磁盘: 50GB SSD

#### 大型部署（> 1000 用户）
- CPU: 4 核
- RAM: 8GB
- 磁盘: 100GB SSD
- 负载均衡器

### 安全配置

1. **防火墙设置**
```bash
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw enable
```

2. **SSL 证书**
```bash
# 使用 Let's Encrypt
sudo certbot --nginx -d your-domain.com
```

3. **定期备份**
```bash
# 添加到 crontab
0 2 * * * tar -czf /backup/ip-manager-$(date +\%Y\%m\%d).tar.gz /opt/ip-manager/data/
```

## 监控和维护

### 健康检查
```bash
# 应用状态
curl http://localhost:5000/health

# 服务状态
sudo systemctl status ip-manager
sudo systemctl status nginx
```

### 日志查看
```bash
# 应用日志
sudo journalctl -u ip-manager -f

# Nginx 日志
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### 性能优化

1. **启用 Gzip**（已配置）
2. **静态文件缓存**（已配置）
3. **使用 CDN**（可选）
4. **数据库优化**（如果使用）

## 故障排除

| 问题 | 解决方案 |
|------|----------|
| 端口被占用 | `sudo lsof -i :5000` 然后杀死进程 |
| 权限问题 | `sudo chown -R user:user /opt/ip-manager` |
| 服务无法启动 | 检查日志 `sudo journalctl -u ip-manager -n 50` |
| 502 错误 | 检查应用是否正常运行 |
| 503 错误 | 检查系统资源使用情况 |

## 技术支持

如需帮助，请：
1. 查看详细文档：`DEPLOYMENT.md`
2. 检查系统日志
3. 验证网络连接
4. 确认配置正确

---

**注意**: 部署前请确保：
- 服务器安全配置完成
- 备份重要数据
- 网络防火墙规则设置
- SSL 证书准备（生产环境）