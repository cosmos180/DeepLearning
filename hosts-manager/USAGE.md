# 使用指南

## 快速开始

### 1. 安装依赖

```bash
# 进入项目目录
cd hosts-manager

# 安装依赖
pip install -r requirements.txt

# 或者使用启动脚本自动安装
python run.py --install-deps
```

### 2. 启动系统

```bash
# 使用启动脚本（推荐）
python run.py

# 或者直接运行 Flask 应用
cd backend && python app.py
```

### 3. 访问系统

打开浏览器访问：http://localhost:5000

## 功能演示

### 运行演示脚本

```bash
python demo.py
```

这将展示系统的主要功能：
- 读取现有 hosts 条目
- 添加新条目
- 删除条目
- 验证 IP 地址和主机名格式

## 运行测试

```bash
# 运行测试套件
python run_tests.py

# 或直接运行测试文件
python tests/test_app.py
```

## 主要功能

### 1. 查看现有条目
- 系统启动时自动加载所有 hosts 条目
- 显示 IP 地址和对应的主机名
- 提供统计信息（总条目数、唯一 IP 数、唯一主机名数）

### 2. 添加新条目
- 在页面顶部输入 IP 地址和主机名
- 系统会验证输入格式的有效性
- 添加成功后会自动刷新列表

### 3. 删除条目
- 点击条目右侧的"删除"按钮
- 弹出确认对话框，防止误操作
- 确认后删除条目并自动刷新列表

### 4. 搜索功能
- 在搜索框中输入关键词
- 实时筛选显示匹配的条目
- 支持按 IP 地址或主机名搜索

## 安全特性

### 自动备份
- 每次修改前自动创建备份
- 备份文件包含时间戳
- 备份位置：
  - Linux/Mac: `/etc/hosts_backups/` 或 `/tmp/hosts_backups/`
  - Windows: `C:\Windows\System32\drivers\etc\hosts_backups\`

### 输入验证
- IP 地址格式验证（支持 IPv4 和 IPv6）
- 主机名格式验证
- 防止添加重复条目

### 确认机制
- 删除操作需要二次确认
- 明确显示将要删除的条目信息

## 命令行选项

```bash
python run.py --help
```

可用选项：
- `--host`: 服务器主机地址（默认: 0.0.0.0）
- `--port`: 服务器端口（默认: 5000）
- `--debug`: 启用调试模式
- `--check-only`: 仅检查环境，不启动服务器
- `--install-deps`: 安装依赖包

## 常见问题

### 权限问题

**Linux/Mac:**
```bash
sudo python run.py
```

**Windows:**
- 以管理员身份运行命令提示符
- 然后执行启动命令

### 端口占用

如果 5000 端口被占用，可以使用其他端口：
```bash
python run.py --port 8080
```

### 依赖安装失败

如果遇到依赖安装问题，可以尝试：
```bash
# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt

# 运行系统
python run.py
```

## 系统要求

- Python 3.6+
- Flask 2.3.3+
- 足够的权限修改 hosts 文件

## 浏览器支持

- Chrome/Edge 88+
- Firefox 85+
- Safari 14+

## 故障排除

### 1. 无法访问 Web 界面

检查：
- 服务器是否正常启动
- 防火墙设置
- 端口是否被占用

### 2. 修改 hosts 文件失败

检查：
- 是否有足够的权限
- hosts 文件是否存在
- 杀毒软件是否阻止修改

### 3. 备份创建失败

系统会自动尝试使用临时目录作为备份位置，不影响主要功能。

## 高级配置

### 自定义 hosts 文件路径

可以修改 `backend/app.py` 中的 `HostsManager` 初始化代码：

```python
hosts_manager = HostsManager("/path/to/your/hosts/file")
```

### 自定义备份目录

同样可以修改备份目录路径：

```python
hosts_manager.backup_dir = "/path/to/backup/directory"
```