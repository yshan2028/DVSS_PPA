#!/bin/bash

# DVSS-PPA 日志查看脚本
# Log Viewer Script

echo "📊 DVSS-PPA 日志查看器"
echo ""

echo "请选择要查看的日志："
echo "1) Python后端日志"
echo "2) Go后端日志"
echo "3) 前端日志"
echo "4) PostgreSQL日志"
echo "5) MongoDB日志"
echo "6) Redis日志"
echo "7) ETL服务日志"
echo "8) 所有服务日志"
echo "9) 实时查看所有日志"
echo ""

read -p "请输入选项 (1-9): " choice

case $choice in
    1)
        echo "📜 Python后端日志："
        echo "=================="
        docker-compose logs -f backend-python
        ;;
    2)
        echo "📜 Go后端日志："
        echo "==============="
        docker-compose logs -f backend-go
        ;;
    3)
        echo "📜 前端日志："
        echo "============"
        docker-compose logs -f frontend
        ;;
    4)
        echo "📜 PostgreSQL日志："
        echo "=================="
        docker-compose logs -f postgres
        ;;
    5)
        echo "📜 MongoDB日志："
        echo "==============="
        docker-compose logs -f mongo
        ;;
    6)
        echo "📜 Redis日志："
        echo "============="
        docker-compose logs -f redis
        ;;
    7)
        echo "📜 ETL服务日志："
        echo "==============="
        docker-compose logs -f etl-service
        ;;
    8)
        echo "📜 所有服务日志："
        echo "================"
        docker-compose logs --tail=100
        ;;
    9)
        echo "📜 实时所有服务日志："
        echo "==================="
        docker-compose logs -f
        ;;
    *)
        echo "❌ 无效选项"
        ;;
esac
