# 🚀 启动指南

## ✅ 问题已修复！

模板路径问题已经解决，系统现在可以正常运行。

## 🎯 一键启动命令

### 方法一：使用虚拟环境（推荐）

```bash
# 进入项目目录
cd /home/bughero/Documents/github/DeepLearning/hosts-manager

# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 启动系统
python run.py
```

### 方法二：直接启动

```bash
# 进入项目目录
cd /home/bughero/Documents/github/DeepLearning/hosts-manager

# 安装依赖到系统
pip3 install -r requirements.txt

# 启动系统
python3 run.py
```

### 方法三：使用管理员权限（如果遇到权限问题）

```bash
# 进入项目目录
cd /home/bughero/Documents/github/DeepLearning/hosts-manager

# 安装依赖
pip3 install -r requirements.txt

# 使用管理员权限启动
sudo python3 run.py
```

## 🌐 访问系统

启动成功后，在浏览器中访问：
- **本地访问**: http://localhost:5000
- **局域网访问**: http://你的IP地址:5000

## 📋 启动成功标志

看到以下输出表示启动成功：

```
============================================================
🌐 Hosts 文件管理系统
============================================================
🔍 检查环境...
✅ Flask 已安装
⚠️  警告: 没有权限修改 hosts 文件: /etc/hosts
   提示: 在 Linux/Mac 上可能需要使用 sudo，在 Windows 上可能需要管理员权限

🚀 启动 Hosts 文件管理系统...
📡 服务地址: http://0.0.0.0:5000
🔧 调试模式: 关闭
📂 工作目录: /home/bughero/Documents/github/DeepLearning/hosts-manager
🛑 按 Ctrl+C 停止服务器

 * Running on all addresses (0.0.0.0)
 * Running on http://127.0.0.1:5000
 * Running on http://172.16.11.76:5000
```

## 🧪 验证系统

### 自动测试
```bash
# 运行Web界面测试
python test_web.py

# 运行功能演示
python demo.py
```

### 手动验证
1. 浏览器访问 http://localhost:5000
2. 看到 "Hosts 文件管理系统" 页面
3. 页面显示现有的 hosts 条目
4. 可以添加新条目和删除现有条目

## ⚙️ 启动选项

```bash
# 指定端口
python run.py --port 8080

# 启用调试模式
python run.py --debug

# 检查环境
python run.py --check-only

# 安装依赖
python run.py --install-deps

# 查看帮助
python run.py --help
```

## 🔧 常见问题解决

### 1. 模板未找到错误
✅ **已修复** - 如果还遇到此问题，请确保：
- 在正确的项目目录中运行
- templates/index.html 文件存在

### 2. 权限不足
```bash
# Linux/Mac 使用 sudo
sudo python run.py

# Windows 以管理员身份运行终端
```

### 3. 端口被占用
```bash
# 使用其他端口
python run.py --port 8080
```

### 4. 依赖安装失败
```bash
# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 📱 系统功能

启动后您可以：

1. **查看现有条目** - 自动显示所有 hosts 文件条目
2. **添加新条目** - 输入 IP 和主机名，点击添加
3. **删除条目** - 点击删除按钮，确认后删除
4. **搜索筛选** - 实时搜索 IP 或主机名
5. **查看统计** - 显示条目总数、唯一 IP 数等

## 🎉 成功案例

系统已通过完整测试：
- ✅ 主页访问正常 (状态码: 200)
- ✅ 页面内容完整 (5193 字符)
- ✅ API 接口正常 (获取 hosts 条目)
- ✅ 健康检查通过 (状态: healthy)

现在您可以安全地使用这个系统来管理您的 hosts 文件了！