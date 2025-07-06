FROM golang:1.21-alpine AS builder

WORKDIR /app

# 安装依赖
RUN apk add --no-cache git

# 复制模块文件
COPY go.mod go.sum ./

# 下载依赖
RUN go mod download

# 复制源代码
COPY . .

# 构建应用
RUN go build -o main .

# 最终镜像
FROM alpine:latest

WORKDIR /app

# 安装运行时依赖
RUN apk add --no-cache ca-certificates

# 复制构建的应用
COPY --from=builder /app/main .

# 创建日志目录
RUN mkdir -p logs

# 暴露端口
EXPOSE 8001

# 启动命令
CMD ["./main"]
