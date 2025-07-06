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
    echo "❌ Docker 服务未运行，请启动 Docker Desktop"
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
echo "🧹 清理Docker环境..."
docker system prune -f 2>/dev/null || true

# 清理无用的挂载卷
docker volume prune -f 2>/dev/null || true
echo ""

# 创建Prometheus配置文件
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
    
  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres:5432']
    
  - job_name: 'redis'
    static_configs:
      - targets: ['redis:6379']
EOF

# 创建Nginx配置文件
echo "🌐 创建Nginx配置..."
mkdir -p nginx
cat > nginx/nginx.conf << 'EOF'
events {
    worker_connections 1024;
}

http {
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
        listen 80;
        server_name localhost;
        
        # 前端
        location / {
            proxy_pass http://frontend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }
        
        # Python API
        location /api/ {
            proxy_pass http://python_backend/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }
        
        # Go API  
        location /fabric-api/ {
            proxy_pass http://go_backend/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }
    }
}
EOF

# 启动基础设施服务
echo "🏗️ 启动基础设施服务..."
echo "1. 启动数据库服务..."
docker-compose up -d postgres mongo redis neo4j

echo "2. 等待数据库初始化..."
echo "   正在等待 PostgreSQL 启动..."
timeout 60 bash -c 'until docker exec dvss-postgres pg_isready -U dvss; do sleep 2; done' || echo "⚠️ PostgreSQL 启动超时"
echo "   正在等待 MongoDB 启动..."
timeout 60 bash -c 'until docker exec dvss-mongo mongo --eval "db.adminCommand('\''ping'\'')" &>/dev/null; do sleep 2; done' || echo "⚠️ MongoDB 启动超时"
echo "   正在等待 Redis 启动..."
timeout 60 bash -c 'until docker exec dvss-redis redis-cli ping &>/dev/null; do sleep 2; done' || echo "⚠️ Redis 启动超时"

echo "3. 启动监控服务..."
docker-compose up -d prometheus grafana

echo "4. 启动ETL服务..."
docker-compose up -d etl-service

echo "✅ 基础设施启动完成"
echo ""

# 构建和启动应用服务
echo "🔨 构建和启动应用服务..."
echo "1. 构建Python后端..."
docker-compose build backend-python

echo "2. 构建Go后端..."
docker-compose build backend-go

echo "3. 构建前端..."
docker-compose build frontend

echo "4. 启动应用服务..."
docker-compose up -d backend-python backend-go frontend nginx

echo "5. 等待应用服务启动..."
sleep 10

echo "✅ 应用服务启动完成"
echo ""

# 可选：启动Fabric网络
read -p "🔗 是否启动Hyperledger Fabric网络？(y/N): " start_fabric
if [[ $start_fabric =~ ^[Yy]$ ]]; then
    echo "启动Hyperledger Fabric网络..."
    echo "1. 启动Fabric CA..."
    docker-compose up -d fabric-ca
    
    echo "2. 检查是否需要启动完整Fabric网络..."
    if [ -f "fabric/network/docker-compose-fabric.yml" ]; then
        cd fabric/network
        echo "3. 启动完整Fabric网络（orderer、peer等）..."
        docker-compose -f docker-compose-fabric.yml up -d
        cd ../..
        echo "✅ 完整Fabric网络启动完成"
    else
        echo "⚠️ 完整Fabric网络配置文件不存在，仅启动CA服务"
    fi
    
    echo "✅ Fabric网络启动完成"
else
    echo "⏭️ 跳过Fabric网络启动"
fi
echo ""

# 检查服务状态
echo "📊 检查服务状态..."
sleep 5
echo ""
echo "=== 所有服务状态 ==="
docker-compose ps
echo ""

# 检查服务健康状态
echo "=== 服务健康检查 ==="
services=("dvss-postgres" "dvss-mongo" "dvss-redis" "dvss-neo4j" "dvss-backend-python" "dvss-go-backend" "dvss-frontend" "dvss-nginx")

for service in "${services[@]}"; do
    if docker ps --filter "name=$service" --filter "status=running" | grep -q $service; then
        echo "✅ $service - 运行中"
    else
        echo "❌ $service - 未运行或异常"
    fi
done
echo ""

echo "🎉 DVSS-PPA 开发环境启动完成！"
echo ""
echo "📱 服务访问地址："
echo "   前端应用:        http://localhost"
echo "   前端直接访问:    http://localhost:3000"
echo "   Python API:      http://localhost:8000"
echo "   Go API:          http://localhost:8001"
echo "   Swagger文档:     http://localhost:8000/docs"
echo "   PostgreSQL:      localhost:5432"
echo "   MongoDB:         localhost:27017"
echo "   Redis:           localhost:6379"
echo "   Neo4j:           http://localhost:7474"
echo "   Prometheus:      http://localhost:9090"
echo "   Grafana:         http://localhost:3001 (admin/admin123)"
if [[ $start_fabric =~ ^[Yy]$ ]]; then
echo "   Fabric CA:       https://localhost:7054"
fi
echo ""
echo "📋 演示账号："
echo "   卖家:           seller (密码: 123456)"
echo "   支付服务商:     payment_provider (密码: 123456)"
echo "   物流:           logistics (密码: 123456)"
echo "   审计:           auditor (密码: 123456)"
echo "   平台管理员:     platform (密码: 123456)"
echo ""
echo "🔧 管理命令："
echo "   查看服务状态:   docker-compose ps"
echo "   查看所有日志:   ./view-logs.sh"
echo "   查看特定日志:   docker-compose logs -f [服务名]"
echo "   停止服务:       ./stop-dev.sh"
echo "   重启服务:       docker-compose restart [服务名]"
echo "   重建服务:       docker-compose up -d --build [服务名]"
echo ""
echo "🔍 故障排查："
echo "   如果服务启动失败，请运行: docker-compose logs -f [服务名]"
echo "   如果端口被占用，请检查其他服务并停止占用的进程"
echo "   如果数据库连接失败，请等待数据库完全启动后重试"
echo ""
echo "✨ 开始你的DVSS-PPA之旅吧！"
