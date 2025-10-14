# IP 地址管理系统

一个简单易用的 Web 系统，用于管理 IP 地址列表。专为非技术人员设计，提供直观的图形界面来添加、删除和管理 IP 地址。

## 功能特性

- 🌐 **Web 界面**: 简洁直观的用户界面，无需命令行操作
- ➕ **添加 IP**: 轻松添加新的 IP 地址
- ❌ **删除 IP**: 安全删除不需要的 IP 地址
- 🔍 **搜索筛选**: 快速查找特定的 IP 地址
- 📊 **统计信息**: 显示 IP 地址总数
- 💾 **自动备份**: 修改前自动创建备份文件
- ✅ **确认机制**: 删除操作需要二次确认，防止误操作
- 🔄 **实时刷新**: 一键刷新查看最新状态
- 📱 **响应式设计**: 支持桌面和移动设备

## 系统要求

- Python 3.6+
- 对项目目录的读写权限

## 快速开始

### 1. 安装依赖

```bash
# 进入项目目录
cd hosts-manager

# 安装 Python 依赖
pip install -r requirements.txt
```

### 2. 启动系统

#### 方法一：使用启动脚本（推荐）

```bash
# 直接启动（默认端口 5000）
python run.py

# 指定端口启动
python run.py --port 8080

# 启用调试模式
python run.py --debug

# 检查环境和依赖
python run.py --check-only
```

#### 方法二：直接运行 Flask 应用

```bash
cd backend
python app.py
```

### 3. 访问系统

打开浏览器访问：
- 本地访问: http://localhost:5000
- 局域网访问: http://你的IP地址:5000

## 使用说明

### 添加 IP 地址

1. 在页面顶部的"添加新 IP 地址"区域
2. 输入 IP 地址（如：192.168.1.100）
3. 点击"添加 IP"按钮

### 删除 IP 地址

1. 在 IP 地址列表中找到要删除的 IP
2. 点击右侧的"删除"按钮
3. 在确认对话框中点击"确认"

### 搜索 IP 地址

1. 在搜索框中输入 IP 地址或部分地址
2. 系统会实时筛选显示匹配的 IP

## 目录结构

```
hosts-manager/
├── backend/              # 后端代码
│   └── app.py           # Flask 主应用
├── static/              # 静态资源
│   ├── css/
│   │   └── style.css   # 样式文件
│   └── js/
│       └── app.js      # 前端 JavaScript
├── templates/           # HTML 模板
│   └── index.html      # 主页面
├── tests/              # 测试文件
│   └── test_app.py     # 测试用例
├── ip_list.txt         # IP 地址数据文件
├── requirements.txt    # Python 依赖
├── run.py             # 启动脚本
├── test_ip_system.py  # 系统测试脚本
└── README.md          # 说明文档
```

## API 接口

### 获取所有 IP 地址
```
GET /api/entries
```

### 添加 IP 地址
```
POST /api/add
Content-Type: application/json

{
  "ip": "192.168.1.100"
}
```

### 删除 IP 地址
```
POST /api/remove
Content-Type: application/json

{
  "ip": "192.168.1.100"
}
```

### 健康检查
```
GET /health
```

## 安全特性

- **输入验证**: 严格验证 IP 地址和主机名格式
- **自动备份**: 每次修改前自动创建备份文件
- **确认机制**: 删除操作需要二次确认
- **错误处理**: 完善的错误处理和用户提示

## 备份和恢复

系统会在每次修改 hosts 文件前自动创建备份：

- **备份位置**:
  - Linux/Mac: `/etc/hosts_backups/`
  - Windows: `C:\Windows\System32\drivers\etc\hosts_backups\`
- **备份格式**: `hosts_YYYYMMDD_HHMMSS.backup`

如需恢复备份，手动将备份文件内容复制回 hosts 文件即可。

## 权限说明

### Linux/Mac
```bash
# 需要管理员权限运行
sudo python run.py
```

### Windows
- 以管理员身份运行命令提示符或 PowerShell
- 然后执行启动命令

## 故障排除

### 常见问题

1. **权限不足错误**
   - 解决方案：使用管理员/root权限运行

2. **端口已被占用**
   - 解决方案：使用 `--port` 参数指定其他端口

3. **依赖安装失败**
   - 解决方案：使用 `--install-deps` 参数强制重新安装

4. **无法访问 Web 界面**
   - 检查防火墙设置
   - 确认服务器正常启动
   - 尝试使用 127.0.0.1 而非 localhost

### 日志查看

系统会在控制台输出详细的运行日志，包括：
- 启动信息
- 操作记录
- 错误信息
- 备份创建记录

## 开发说明

### 本地开发

```bash
# 克隆或下载项目
cd hosts-manager

# 安装开发依赖
pip install -r requirements.txt

# 启动开发服务器
python run.py --debug --port 5000
```

### 自定义配置

可以通过修改 `backend/app.py` 中的配置来自定义系统行为：

- `hosts_path`: hosts 文件路径
- `backup_dir`: 备份目录
- `secret_key`: Flask 密钥

## 贡献

欢迎提交 Issue 和 Pull Request 来改进这个项目！

## 许可证

本项目采用 MIT 许可证。

## 支持

如有问题或建议，请提交 Issue 或联系开发者。

---

**⚠️ 重要提示**:
- 请谨慎操作 hosts 文件，错误的配置可能导致网络问题
- 建议在修改前了解 hosts 文件的作用
- 如不确定操作，请先创建系统备份