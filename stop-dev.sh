#!/bin/bash

# DVSS-PPA 开发环境停止脚本
# Development Environment Stop Script

echo "🛑 停止 DVSS-PPA 开发环境..."
echo ""

# 停止所有Docker容器
echo "停止Docker容器..."
docker-compose down -v

# 清理Docker资源
echo "清理Docker资源..."
docker system prune -f 2>/dev/null || true

# 删除临时日志文件
echo "清理日志文件..."
rm -f logs/*.pid 2>/dev/null || true

echo ""
echo "✅ DVSS-PPA 开发环境已完全停止"
