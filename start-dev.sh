#!/bin/bash

# DVSS-PPA 开发环境启动脚本
# Development Environment Startup Script

set -e

echo "🚀 启动 DVSS-PPA 开发环境..."
echo "Starting DVSS-PPA Development Environment..."
echo ""

# 检查必要的工具
echo "📋 检查环境依赖..."
if ! command -v docker &> /dev/null; then
    echo "❌ Docker 未安装，请先安装 Docker"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose 未安装，请先安装 Docker Compose"
    exit 1
fi

# 检查Docker是否运行
if ! docker info &> /dev/null; then
    echo "❌ Docker 服务未运行，请启动 Docker Desktop 或 Docker 服务"
    exit 1
fi

echo "✅ 环境依赖检查完成"
echo ""

# 创建必要的目录
echo "📁 创建必要的目录..."
mkdir -p logs
mkdir -p monitoring/grafana/dashboards
mkdir -p monitoring/grafana/datasources
mkdir -p fabric-config/ca
mkdir -p fabric/crypto-config
mkdir -p fabric/channel-artifacts
mkdir -p nginx
mkdir -p etl/logs
echo ""

# 停止可能运行的容器
echo "🛑 停止现有容器..."
docker-compose down -v 2>/dev/null || true

# 清理旧的容器和镜像
echo "🧹 清理 Docker 环境..."
docker system prune -f 2>/dev/null || true

# 清理无用的挂载卷
docker volume prune -f 2>/dev/null || true
echo ""

# 创建 Prometheus 配置文件
echo "⚙️ 创建监控配置文件..."
cat > monitoring/prometheus.yml << 'EOF'
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'python-backend'
    static_configs:
      - targets: ['backend-python:8000']
  - job_name: 'go-backend'
    static_configs:
      - targets: ['backend-go:8001']
  - job_name: 'mysql'
    static_configs:
      - targets: ['mysql:3306']
  - job_name: 'redis'
    static_configs:
      - targets: ['redis:6379']
EOF
echo ""

# 创建 Nginx 配置文件
echo "🌐 创建 Nginx 配置..."
cat > nginx/nginx.conf << 'EOF'
worker_processes auto;
error_log  /var/log/nginx/error.log  warn;
pid        /var/run/nginx.pid;

events {
    worker_connections 1024;
}

http {
    include       mime.types;
    default_type  application/octet-stream;

    sendfile        on;
    keepalive_timeout  65;

    # 开启 gzip 压缩
    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;
    gzip_min_length 1000;

    # 定义上游服务
    upstream python_backend {
        server backend-python:8000;
    }
    upstream go_backend {
        server backend-go:8001;
    }
    upstream frontend {
        server frontend:80;
    }

    server {
        listen       80;
        server_name  localhost;

        # 前端静态资源 / SPA 回退
        location / {
            try_files $uri $uri/ /index.html;
            proxy_pass http://frontend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }

        # Python API
        location /api {
            proxy_pass http://python_backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_connect_timeout 5s;
            proxy_read_timeout 120s;
        }

        # Go (Fabric) API
        location /fabric-api {
            proxy_pass http://go_backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_connect_timeout 5s;
            proxy_read_timeout 120s;
        }

        # 自定义错误页面
        error_page 404 /404.html;
        location = /404.html {
            root /usr/share/nginx/html;
            internal;
        }
        error_page 500 502 503 504 /50x.html;
        location = /50x.html {
            root /usr/share/nginx/html;
            internal;
        }
    }
}
EOF
echo ""

# 启动基础设施服务
echo "🏗️ 启动基础设施服务..."
echo "1. 启动 MySQL / MongoDB / Redis / Neo4j..."
docker-compose up -d mysql mongo redis neo4j

# 等待数据库初始化
echo "2. 等待数据库初始化..."
MYSQL_CID=$(docker-compose ps -q mysql)
MONGO_CID=$(docker-compose ps -q mongo)
REDIS_CID=$(docker-compose ps -q redis)

echo "   等待 MySQL (3306) 启动..."
timeout 60 bash -c \
  'until docker exec '"$MYSQL_CID"' mysqladmin ping -uroot -padmin123 &>/dev/null; do sleep 2; done' \
  || echo "⚠️ MySQL 启动超时"

echo "   等待 MongoDB (27017) 启动..."
timeout 60 bash -c '
  until docker exec "$MONGO_CID" mongo --eval "db.adminCommand(\"ping\")" &>/dev/null; do sleep 2; done
' || echo "⚠️ MongoDB 启动超时"

echo "   等待 Redis (6379) 启动..."
timeout 60 bash -c \
  'until docker exec '"$REDIS_CID"' redis-cli ping &>/dev/null; do sleep 2; done' \
  || echo "⚠️ Redis 启动超时"
echo ""

# 启动监控与 ETL 服务
echo "3. 启动 Prometheus / Grafana..."
docker-compose up -d prometheus grafana
echo "4. 启动 ETL 服务..."
docker-compose up -d etl-service
echo "✅ 基础设施启动完成"
echo ""

# 构建并启动应用服务
echo "🔨 构建并启动应用服务..."
echo "1. 构建 Python 后端..."
docker-compose build backend-python
echo "2. 构建 Go 后端..."
docker-compose build backend-go
echo "3. 构建 前端..."
docker-compose build frontend

echo "4. 启动 应用服务..."
docker-compose up -d backend-python backend-go frontend nginx
echo "5. 等待 应用服务 启动..."
sleep 10
echo "✅ 应用服务启动完成"
echo ""

# 可选启动 Hyperledger Fabric 网络 (2.5)
read -p "🔗 是否启动 Fabric CA？(y/N): " start_fabric
if [[ $start_fabric =~ ^[Yy]$ ]]; then
    echo "启动 Fabric CA..."
    docker-compose up -d fabric-ca
    if [ -f "fabric/network/docker-compose-fabric.yml" ]; then
        echo "启动 完整 Fabric 网络..."
        pushd fabric/network >/dev/null
        docker-compose -f docker-compose-fabric.yml up -d
        popd >/dev/null
        echo "✅ Fabric 网络 启动完成"
    else
        echo "⚠️ 未找到 完整 Fabric 网络 配置，仅启动 CA 服务"
    fi
else
    echo "⏭️ 跳过 Fabric CA 启动"
fi
echo ""

# 检查服务状态
echo "📊 检查 服务 状态..."
sleep 5
echo ""
echo "=== 所有 服务 状态 ==="
docker-compose ps
echo ""

# 检查 服务 健康 状态
echo "=== 服务 健康 检查 ==="
services="dvss-mysql dvss-mongo dvss-redis dvss-neo4j dvss-backend-python dvss-go-backend dvss-frontend dvss-nginx"
for svc in $services; do
    if docker ps --filter "name=$svc" --filter "status=running" | grep -q $svc; then
        echo "✅ $svc - 运行中"
    else
        echo "❌ $svc - 未运行或异常"
    fi
done
echo ""

echo "🎉 DVSS-PPA 开发环境启动完成！"
echo ""
echo "📱 服务访问 地址："
echo "   前端应用:     http://localhost"
echo "   前端直连:     http://localhost:3000"
echo "   Python API:   http://localhost:8000"
echo "   Go API:       http://localhost:8001"
echo "   Swagger:      http://localhost:8000/docs"
echo "   MySQL:        localhost:3306"
echo "   MongoDB:      localhost:27017"
echo "   Redis:        localhost:6379"
echo "   Neo4j:        http://localhost:7474"
echo "   Prometheus:   http://localhost:9090"
echo "   Grafana:      http://localhost:3001 (admin/admin123)"
if [[ $start_fabric =~ ^[Yy]$ ]]; then
    echo "   Fabric CA:    https://localhost:7054"
fi
echo ""
echo "📋 演示 账号："
echo "   卖家:           seller (密码: 123456)"
echo "   支付服务商:     payment_provider (密码: 123456)"
echo "   物流:           logistics (密码: 123456)"
echo "   审计:           auditor (密码: 123456)"
echo "   平台管理员:     platform (密码: 123456)"
echo ""
echo "🔧 管理 命令："
echo "   查看 状态:       docker-compose ps"
echo "   查看 所有 日志:   ./view-logs.sh"
echo "   查看 指定 日志:   docker-compose logs -f [服务名]"
echo "   停止 服务:       ./stop-dev.sh"
echo "   重启 服务:       docker-compose restart [服务名]"
echo "   重建 服务:       docker-compose up -d --build [服务名]"
echo ""
echo "🔍 故障 排查："
echo "   如果 启动 失败，请运行: docker-compose logs -f [服务名]"
echo "   如果 端口 被 占用，请 停止 其他 进程"
echo "   如果 数据库 连接 失败，请 等待 完全 启动 后 重试"
echo ""
echo "✨ 开始 你的 DVSS-PPA 之旅 吧！"
