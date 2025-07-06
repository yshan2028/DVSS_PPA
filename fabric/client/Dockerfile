# 多阶段构建：构建阶段
FROM golang:1.22-alpine AS builder

# 设置工作目录
WORKDIR /app

# 安装必要的工具
RUN apk add --no-cache git ca-certificates

# 复制go mod文件
COPY go.mod go.sum ./

# 下载依赖
RUN go mod download

# 复制源代码
COPY . .

# 构建应用程序
RUN CGO_ENABLED=0 GOOS=linux go build -a -installsuffix cgo -o dvss-fabric-client .

# 运行阶段
FROM alpine:3.18

# 安装curl用于健康检查
RUN apk --no-cache add ca-certificates curl

WORKDIR /app

# 从构建阶段复制二进制文件
COPY --from=builder /app/dvss-fabric-client .

# 创建必要的目录
RUN mkdir -p /app/config /app/data

# 设置权限
RUN chmod +x ./dvss-fabric-client

# 暴露端口
EXPOSE 8080

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8080/api/v1/health || exit 1

# 启动应用
CMD ["./dvss-fabric-client"]
