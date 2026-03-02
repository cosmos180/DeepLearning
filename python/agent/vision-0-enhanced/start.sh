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

echo ""
echo "✅ 环境变量已加载"
echo "🚀 启动后端服务 (端口 8765)..."
echo ""

# 启动 FastAPI 后端
python3 -m uvicorn backend.api.main:app \
  --host 0.0.0.0 \
  --port 8765 \
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
echo "  后端 API: http://localhost:8765"
echo "  API 文档: http://localhost:8765/docs"
echo "======================================"
echo ""
echo "按 Ctrl+C 停止服务"

# 等待退出
wait $BACKEND_PID
