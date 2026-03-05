#!/bin/bash
# Vision-0 Enhanced 启动脚本

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "======================================"
echo "  Vision-0 Enhanced — AI 影视制片厂"
echo "======================================"

# 检查 .env 文件
if [ ! -f ".env" ]; then
  echo ""
  echo "⚠️  未找到 .env 文件，正在从模板创建..."
  cp .env.example .env
  echo "请编辑 .env 文件，填入你的 OPENAI_API_KEY"
  echo ""
fi

# 加载环境变量
export $(grep -v '^#' .env | xargs) 2>/dev/null || true

if [ -z "$OPENAI_API_KEY" ]; then
  echo "❌ 错误：OPENAI_API_KEY 未设置，请在 .env 文件中配置"
  exit 1
fi

PORT=8765

echo ""
echo "✅ 环境变量已加载"

# 检查端口是否被占用，如果是则终止旧进程
EXISTING_PID=$(lsof -ti :$PORT 2>/dev/null || true)
if [ -n "$EXISTING_PID" ]; then
  echo "⚠️  端口 $PORT 已被占用 (PID: $EXISTING_PID)，正在终止旧进程..."
  kill $EXISTING_PID 2>/dev/null
  sleep 1
  # 如果还没退出，强制终止
  kill -9 $EXISTING_PID 2>/dev/null || true
  sleep 0.5
  echo "✅ 旧进程已终止"
fi

echo "🚀 启动后端服务 (端口 $PORT)..."
echo ""

# 启动 FastAPI 后端
python3 -m uvicorn backend.api.main:app \
  --host 0.0.0.0 \
  --port $PORT \
  --reload \
  --log-level info &

BACKEND_PID=$!
echo "后端 PID: $BACKEND_PID"

# 等待后端启动
sleep 2

echo ""
echo "======================================"
echo "  服务已启动！"
echo "  前端界面: 用浏览器打开 frontend/index.html"
echo "  后端 API: http://localhost:$PORT"
echo "  API 文档: http://localhost:$PORT/docs"
echo "======================================"
echo ""
echo "按 Ctrl+C 停止服务"

# 等待退出
wait $BACKEND_PID
